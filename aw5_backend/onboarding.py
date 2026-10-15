"""Local administrator sessions and project enrollment; no secrets in Discord."""

import asyncio
import hashlib
import json
import secrets
from time import monotonic
from uuid import UUID

import psycopg
from aiohttp import web

from .integrations import IntegrationError
from .service import Denied, Unavailable


COOKIE = "aw5_admin_session"


def positive_id(value) -> int:
    if type(value) is bool or not isinstance(value, (str, int)):
        raise ValueError("Invalid identifier")
    text = str(value)
    if not text.isascii() or not text.isdecimal() or not 0 < int(text) <= 2**63 - 1:
        raise ValueError("Invalid identifier")
    return int(text)


def project_summary(project) -> dict:
    return {"tenant_id": str(project.tenant_id), "tenant_name": project.tenant_name,
            "discord_role_id": str(project.discord_role_id), "dify_app_id": project.dify_app_id,
            "status": project.status, "last_sync_error": project.last_sync_error}


class AdminPortal:
    def __init__(self, service):
        self.service = service
        self.settings = service.settings
        self.grants: dict[str, tuple[float, int]] = {}
        self.sessions: dict[str, tuple[float, int, str]] = {}
        self.enrollment_lock = asyncio.Lock()

    def prune(self):
        now = monotonic()
        self.grants = {k: v for k, v in self.grants.items() if v[0] > now}
        self.sessions = {k: v for k, v in self.sessions.items() if v[0] > now}

    @staticmethod
    def digest(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def authorize(self, user_id: int):
        if not self.settings.admin_role_id or not self.settings.admin_channel_id:
            raise Denied("Admin is not configured")
        try:
            roles = await self.service.discord.member_roles(self.settings.guild_id, user_id)
        except IntegrationError as exc:
            raise Unavailable("Discord admin lookup unavailable") from exc
        if self.settings.admin_role_id not in roles:
            raise Denied("Admin role required")

    async def issue_link(self, guild_id: int, channel_id: int, user_id: int) -> str:
        if (guild_id, channel_id) != (self.settings.guild_id, self.settings.admin_channel_id):
            raise Denied("Admin channel required")
        await self.authorize(user_id)
        self.prune()
        if len(self.grants) >= 1000:
            raise Unavailable("Admin links exhausted")
        token = secrets.token_urlsafe(32)
        self.grants[self.digest(token)] = (monotonic() + 180, user_id)
        return self.settings.admin_portal_origin + "/admin#login=" + token

    def same_origin(self, request):
        if request.headers.get("Origin") != self.settings.admin_portal_origin:
            raise web.HTTPForbidden(text="Invalid origin")

    async def exchange(self, request):
        self.same_origin(request)
        data = await request.json()
        if not isinstance(data, dict):
            raise Denied("Invalid link")
        token = data.get("token")
        if not isinstance(token, str) or len(token) > 128:
            raise Denied("Invalid link")
        self.prune()
        grant = self.grants.pop(self.digest(token), None)
        if grant is None:
            raise Denied("Link expired or used")
        await self.authorize(grant[1])
        if len(self.sessions) >= 1000:
            raise Unavailable("Admin sessions exhausted")
        cookie, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        self.sessions[self.digest(cookie)] = (monotonic() + 900, grant[1], csrf)
        response = web.json_response({"csrf": csrf})
        response.set_cookie(COOKIE, cookie, httponly=True, samesite="Strict", max_age=900,
                            path="/v1/admin/portal")
        return response

    async def identity(self, request):
        self.prune()
        cookie = request.cookies.get(COOKIE, "")
        session = self.sessions.get(self.digest(cookie))
        if not session:
            raise Denied("Admin session expired")
        await self.authorize(session[1])
        if request.method != "GET":
            self.same_origin(request)
            if not secrets.compare_digest(request.headers.get("X-AW5-CSRF", ""), session[2]):
                raise Denied("Invalid CSRF token")
        return session

    async def model(self, request):
        session = await self.identity(request)
        try:
            options = await self.service.discord.admin_role_options(self.settings.guild_id, self.settings.admin_role_id)
        except IntegrationError:
            # Display existing bindings even when Discord cannot resolve names.
            # Enrollment still performs its own fresh role/permission checks.
            options = {"roles": [], "can_create": False, "role_names": {}}
        projects = await asyncio.to_thread(self.service.registry.projects)
        registered = {str(p.discord_role_id) for p in projects}
        summaries = [{**project_summary(p),
                      "discord_role_name": options["role_names"].get(str(p.discord_role_id))}
                     for p in projects]
        return web.json_response({"csrf": session[2], "projects": summaries,
                                  "roles": [r for r in options["roles"] if r["id"] not in registered],
                                  "can_create": options["can_create"]})

    async def enroll(self, actor_id: int, data: dict) -> dict:
        tenant = positive_id(data["tenant_id"])
        request_id = str(UUID(data["request_id"]))
        name, key, mode = data["tenant_name"], data["dify_app_api_key"], data["role_mode"]
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 70:
            raise ValueError("Invalid project name")
        if not isinstance(key, str) or not 1 <= len(key.strip()) <= 512 or mode not in {"existing", "new"}:
            raise ValueError("Invalid enrollment")
        name, key = name.strip(), key.strip()
        role_id = positive_id(data["discord_role_id"]) if mode == "existing" else None
        async with self.enrollment_lock:
            await self.authorize(actor_id)
            # Resolve identity only from the trusted digest view, never browser input.
            app = await asyncio.to_thread(self.service.registry.resolve_app_key, key)
            # Older clients may still supply an ID; reject mismatches, not override.
            if "dify_app_id" in data and str(UUID(data["dify_app_id"])) != app:
                raise ValueError("Dify app ID does not match this key")
            # Never store the plaintext key or its fingerprint in browser storage/logs.
            fingerprint = hashlib.sha256(json.dumps([tenant, app, name, mode, role_id,
                                                      hashlib.sha256(key.encode()).hexdigest()]).encode()).hexdigest()
            previous = await asyncio.to_thread(self.service.registry.get_enrollment, request_id, actor_id, fingerprint)
            if previous:
                if previous["state"] == "completed":
                    return project_summary(await asyncio.to_thread(self.service.registry.get_project, tenant))
                raise web.HTTPConflict(text="รายการนี้ค้างอยู่ กรุณาติดต่อผู้ดูแล อย่าสร้างยศซ้ำ")
            if not await asyncio.to_thread(self.service.registry.verify_app_key, app, key):
                raise ValueError("Dify key does not belong to this app")
            selection = await asyncio.to_thread(self.service.registry.published_selection, app)
            if selection is None:
                raise ValueError("Publish this app with Knowledge Retrieval first")
            workflow, datasets = selection
            await self.service.dify.project_files(tenant, datasets)
            params = await self.service.dify._json("GET", "/parameters", key)
            if not any(next(iter(item.values()), {}).get("variable") == "aw5_registry_json"
                       and next(iter(item.values()), {}).get("required") is True
                       for item in params.get("user_input_form", [])):
                raise ValueError("Published app must accept aw5_registry_json")
            options = await self.service.discord.admin_role_options(self.settings.guild_id, self.settings.admin_role_id)
            if mode == "existing" and str(role_id) not in {r["id"] for r in options["roles"]}:
                raise ValueError("Role cannot be enrolled")
            if mode == "new" and not options["can_create"]:
                raise ValueError("AW5-Bot needs Manage Roles to create a role")
            projects = await asyncio.to_thread(self.service.registry.projects)
            if role_id is not None and any(p.discord_role_id == role_id for p in projects):
                raise psycopg.errors.UniqueViolation("Role already registered")
            previous = await asyncio.to_thread(self.service.registry.begin_enrollment,
                                              request_id, tenant, app, actor_id, fingerprint)
            if previous:
                if previous["state"] == "completed":
                    project = await asyncio.to_thread(self.service.registry.get_project, tenant)
                    return project_summary(project)
                raise web.HTTPConflict(text="รายการนี้ค้างอยู่ กรุณาติดต่อผู้ดูแล อย่าสร้างยศซ้ำ")
            try:
                await self.authorize(actor_id)
                if mode == "new":
                    role_id = await self.service.discord.create_project_role(self.settings.guild_id, name)
                await asyncio.to_thread(self.service.registry.finish_enrollment, request_id, "in_progress", role_id)
                await self.authorize(actor_id)
                # Recheck Publish after role provisioning; do not activate a changed selection.
                if await asyncio.to_thread(self.service.registry.published_selection, app) != (workflow, datasets):
                    raise Unavailable("Published selection changed during enrollment")
                project = await asyncio.to_thread(self.service.registry.register_project,
                                                 name=name, guild_id=self.settings.guild_id, role_id=role_id,
                                                 app_id=UUID(app), encrypted_key=self.service.cipher.encrypt(key.encode()),
                                                 tenant_id=tenant, enrollment_request=request_id)
                try:
                    project = await self.service.sync_project(tenant)
                except Unavailable:
                    project = await asyncio.to_thread(self.service.registry.get_project, tenant)
                return project_summary(project)
            except BaseException:
                await asyncio.shield(asyncio.to_thread(self.service.registry.finish_enrollment,
                                                      request_id, "needs_attention", role_id))
                raise

    async def change_role(self, actor_id, tenant, data):
        request_id = str(UUID(data['request_id']))
        mode = data['role_mode']
        if mode not in {'existing', 'new'}:
            raise ValueError('Invalid role mode')
        role_id = positive_id(data['discord_role_id']) if mode == 'existing' else None
        fingerprint = hashlib.sha256(json.dumps([tenant, mode, role_id]).encode()).hexdigest()
        async with self.enrollment_lock:
            await self.authorize(actor_id)
            project = await asyncio.to_thread(self.service.registry.get_project, tenant)
            if project is None or project.guild_id != self.settings.guild_id:
                raise ValueError('Unknown project')
            options = await self.service.discord.admin_role_options(self.settings.guild_id, self.settings.admin_role_id)
            if mode == 'existing':
                if str(role_id) not in {r['id'] for r in options['roles']}:
                    raise ValueError('Unsafe or missing role')
                projects = await asyncio.to_thread(self.service.registry.projects)
                if any(p.tenant_id != tenant and p.discord_role_id == role_id for p in projects):
                    raise psycopg.errors.UniqueViolation('Role already registered')
            elif not options['can_create']:
                raise ValueError('Manage Roles required')
            previous = await asyncio.to_thread(self.service.registry.begin_role_change,
                request_id, tenant, actor_id, fingerprint, project.discord_role_id)
            if previous:
                if previous['state'] == 'completed':
                    return project_summary(project)
                raise web.HTTPConflict(text='รายการเปลี่ยนยศค้างอยู่ กรุณาติดต่อผู้ดูแล อย่าสร้างยศซ้ำ')
            try:
                await self.authorize(actor_id)
                if mode == 'new':
                    role_id = await self.service.discord.create_project_role(self.settings.guild_id, project.tenant_name)
                await self.authorize(actor_id)
                updated = await asyncio.to_thread(self.service.registry.complete_role_change, request_id, role_id)
                return project_summary(updated)
            except BaseException:
                await asyncio.shield(asyncio.to_thread(self.service.registry.fail_role_change, request_id, role_id))
                raise

    async def rebind_role(self, request):
        session = await self.identity(request)
        try:
            return web.json_response(await self.change_role(session[1], positive_id(request.match_info['tenant_id']), await request.json()))
        except psycopg.errors.UniqueViolation:
            return web.json_response({'error': 'ยศนี้ถูกผูกแล้ว หรือมีรายการเปลี่ยนยศค้างอยู่'}, status=409)
        except (ValueError, TypeError, KeyError):
            return web.json_response({'error': 'ตรวจโปรเจกต์และยศที่เลือก ยศต้องมีอยู่และปลอดภัย หรือบอทต้องมี Manage Roles'}, status=400)
        except (psycopg.Error, IntegrationError):
            return web.json_response({'error': 'เปลี่ยนยศไม่สำเร็จ กรุณาติดต่อผู้ดูแลก่อนลองใหม่หากสร้างยศไปแล้ว'}, status=503)

    async def delete_project(self, request):
        session = await self.identity(request)
        try:
            tenant = positive_id(request.match_info['tenant_id'])
            data = await request.json()
            name = data['confirmation_name']
            if not isinstance(name, str) or not 1 <= len(name) <= 70:
                raise ValueError('Project name required')
            app_id = str(UUID(data['dify_app_id']))
            role_id = positive_id(data['discord_role_id'])
            async with self.enrollment_lock:
                await self.authorize(session[1])
                result = await asyncio.to_thread(self.service.registry.delete_project,
                    tenant, self.settings.guild_id, name, app_id, role_id)
            return web.json_response(result)
        except psycopg.errors.ObjectInUse:
            return web.json_response({'error': 'มีรายการลงทะเบียนหรือเปลี่ยนยศค้างอยู่ ต้องตรวจสอบและแก้รายการนั้นก่อนลบ'}, status=409)
        except (ValueError, TypeError, KeyError):
            return web.json_response({'error': 'ชื่อยืนยันไม่ตรงหรือข้อมูลโปรเจกต์เปลี่ยนแล้ว กรุณาโหลดหน้าใหม่'}, status=400)
        except psycopg.Error:
            return web.json_response({'error': 'ฐานข้อมูลไม่พร้อม ลบไม่สำเร็จ กรุณาตรวจรายการก่อนลองใหม่'}, status=503)

    async def register(self, request):
        session = await self.identity(request)
        try:
            result = await self.enroll(session[1], await request.json())
            return web.json_response(result, status=201)
        except psycopg.errors.UniqueViolation:
            return web.json_response({"error": "tenant ID, app หรือยศนี้ถูกลงทะเบียนหรือจองไว้แล้ว"}, status=409)
        except (ValueError, TypeError, KeyError):
            return web.json_response({"error": "ข้อมูลไม่ถูกต้อง: ตรวจ tenant ID, App API key, ยศ และ Published input (คีย์ต้องระบุ Dify app ได้เพียงหนึ่งแอป)"}, status=400)
        except psycopg.Error:
            return web.json_response({"error": "ฐานข้อมูลลงทะเบียนไม่พร้อม กรุณาติดต่อผู้ดูแล"}, status=503)
        except IntegrationError:
            return web.json_response({"error": "ตรวจ Dify/Discord ไม่สำเร็จ ตรวจ metadata และสิทธิ์บอทก่อนลองใหม่"}, status=503)

    async def logout(self, request):
        await self.identity(request)
        self.sessions.pop(self.digest(request.cookies.get(COOKIE, "")), None)
        response = web.json_response({"logged_out": True})
        response.del_cookie(COOKIE, path="/v1/admin/portal")
        return response
