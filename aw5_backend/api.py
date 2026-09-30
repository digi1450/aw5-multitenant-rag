"""Private HTTP API for Discord adapter and project administration."""

import asyncio
import hmac
import logging
from pathlib import Path

from aiohttp import ClientSession, TCPConnector, web
import psycopg

from .config import Settings
from .db import Ticket
from .service import Denied, Service, Unavailable


LOG = logging.getLogger(__name__)


def _positive(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("invalid identifier")
    result = int(value)
    if result <= 0:
        raise ValueError("invalid identifier")
    return result


def _auth(request: web.Request, expected: str) -> None:
    supplied = request.headers.get("Authorization", "")
    if not hmac.compare_digest(supplied, f"Bearer {expected}"):
        raise web.HTTPUnauthorized(text="Unauthorized")


@web.middleware
async def errors(request: web.Request, handler):
    try:
        return await handler(request)
    except Denied:
        raise web.HTTPForbidden(text="Access denied")
    except Unavailable:
        raise web.HTTPServiceUnavailable(text="Project service unavailable")
    except (ValueError, TypeError, KeyError):
        raise web.HTTPBadRequest(text="Invalid request")
    except psycopg.errors.UniqueViolation:
        raise web.HTTPConflict(text="Project or role is already registered")


def build_app(settings: Settings, service: Service | None = None) -> web.Application:
    service = service or Service(settings)
    app = web.Application(middlewares=[errors], client_max_size=16 * 1024)
    app[web.AppKey("service", Service)] = service

    async def eligible(request: web.Request) -> web.Response:
        _auth(request, settings.bot_api_token)
        guild_id = _positive(request.query["guild_id"])
        user_id = _positive(request.query["user_id"])
        return web.json_response({"projects": await service.eligible_projects(guild_id, user_id)})

    async def create_ticket(request: web.Request) -> web.Response:
        _auth(request, settings.bot_api_token)
        data = await request.json()
        await service.create_ticket(
            guild_id=_positive(data["guild_id"]), user_id=_positive(data["user_id"]),
            thread_id=_positive(data["thread_id"]), tenant_id=_positive(data["tenant_id"]),
        )
        return web.json_response({"result": "created"}, status=201)

    async def ticket_files(request: web.Request) -> web.Response:
        _auth(request, settings.bot_api_token)
        files = await service.ticket_files(
            _positive(request.match_info["thread_id"]), _positive(request.query["guild_id"]),
            _positive(request.query["user_id"]),
        )
        ticket = await asyncio.to_thread(service.registry.get_ticket,
                                         _positive(request.match_info["thread_id"]))
        return web.json_response({"files": files, "tenant_id": ticket.tenant_id})

    async def ask(request: web.Request) -> web.Response:
        _auth(request, settings.bot_api_token)
        data = await request.json()
        question = data["question"]
        if not isinstance(question, str):
            raise ValueError("question must be text")
        answer = await service.ask(
            _positive(request.match_info["thread_id"]), _positive(data["guild_id"]),
            _positive(data["user_id"]), question,
        )
        return web.json_response({"answer": answer})

    async def close_ticket(request: web.Request) -> web.Response:
        _auth(request, settings.bot_api_token)
        data = await request.json()
        closed = await service.close_ticket(
            _positive(request.match_info["thread_id"]), _positive(data["guild_id"]),
            _positive(data["user_id"]),
        )
        return web.json_response({"closed": closed})

    async def register_project(request: web.Request) -> web.Response:
        _auth(request, settings.admin_api_token)
        data = await request.json()
        if not all(isinstance(data.get(name), str) for name in ("tenant_name", "dify_app_id", "dify_app_api_key")):
            raise ValueError("project registration fields are invalid")
        project = await service.register_project(
            name=data["tenant_name"], role_id=_positive(data["discord_role_id"]),
            app_id=data["dify_app_id"], app_key=data["dify_app_api_key"],
        )
        try:
            project = await service.sync_project(project.tenant_id)
        except Unavailable:
            project = await asyncio.to_thread(service.registry.get_project, project.tenant_id)
        return web.json_response({"tenant_id": project.tenant_id, "status": project.status}, status=201)

    async def admin_projects(request: web.Request) -> web.Response:
        _auth(request, settings.admin_api_token)
        projects = await asyncio.to_thread(service.registry.projects)
        return web.json_response({"projects": [
            {"tenant_id": item.tenant_id, "tenant_name": item.tenant_name,
             "discord_role_id": item.discord_role_id, "dify_app_id": item.dify_app_id,
             "status": item.status, "published_workflow_id": item.published_workflow_id,
             "last_sync_error": item.last_sync_error}
            for item in projects
        ]})

    async def sync_project(request: web.Request) -> web.Response:
        _auth(request, settings.admin_api_token)
        project = await service.sync_project(_positive(request.match_info["tenant_id"]))
        return web.json_response({"tenant_id": project.tenant_id, "status": project.status,
                                  "published_workflow_id": project.published_workflow_id})

    async def import_tickets(request: web.Request) -> web.Response:
        _auth(request, settings.admin_api_token)
        data = await request.json()
        rows = data["tickets"]
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("invalid ticket batch")
        tickets = []
        for row in rows:
            conversation = row.get("dify_conversation_id")
            if conversation is not None and (not isinstance(conversation, str) or len(conversation) > 128):
                raise ValueError("invalid conversation ID")
            tickets.append(Ticket(_positive(row["thread_id"]), _positive(row["guild_id"]),
                                  _positive(row["discord_user_id"]), _positive(row["tenant_id"]),
                                  conversation))
        count = await asyncio.to_thread(service.registry.import_tickets, tickets)
        return web.json_response({"imported": count})

    async def health(request: web.Request) -> web.Response:
        return web.json_response({"status": "running"})

    app.router.add_get("/health", health)
    app.router.add_get("/v1/projects/eligible", eligible)
    app.router.add_post("/v1/tickets", create_ticket)
    app.router.add_get("/v1/tickets/{thread_id}/files", ticket_files)
    app.router.add_post("/v1/tickets/{thread_id}/ask", ask)
    app.router.add_post("/v1/tickets/{thread_id}/close", close_ticket)
    app.router.add_get("/v1/admin/projects", admin_projects)
    app.router.add_post("/v1/admin/projects", register_project)
    app.router.add_post("/v1/admin/projects/{tenant_id}/sync", sync_project)
    app.router.add_post("/v1/admin/tickets/import", import_tickets)

    async def resources(app: web.Application):
        schema = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
        await asyncio.to_thread(service.registry.initialize, schema)

        async def reconcile() -> None:
            while True:
                try:
                    for project in await asyncio.to_thread(service.registry.projects):
                        try:
                            await service.sync_project(project.tenant_id)
                        except Unavailable:
                            continue
                except Exception:
                    LOG.exception("Background project sync failed")
                await asyncio.sleep(60)

        async with ClientSession(connector=TCPConnector(keepalive_timeout=30)) as session:
            service.bind_session(session)
            sync_task = asyncio.create_task(reconcile())
            try:
                yield
            finally:
                sync_task.cancel()
                try:
                    await sync_task
                except asyncio.CancelledError:
                    pass
                service.bind_session(None)

    app.cleanup_ctx.append(resources)
    return app


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings.from_env()
    web.run_app(build_app(settings), host="0.0.0.0", port=8765)


if __name__ == "__main__":
    main()
