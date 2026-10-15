"""Authorization and automatic reconciliation of Published Dify projects."""

import asyncio
from dataclasses import dataclass
import logging
from time import perf_counter
from uuid import UUID

import aiohttp
from cryptography.fernet import Fernet, InvalidToken

from .config import Settings
from .db import Project, Registry, Ticket
from .integrations import DifyAccess, DiscordAccess, IntegrationError
from .source_registry import registry_payload


LOG = logging.getLogger(__name__)


class Denied(Exception):
    pass


class Unavailable(Exception):
    pass


@dataclass(frozen=True)
class ValidatedScope:
    project: Project
    workflow_id: str
    dataset_ids: frozenset[str]
    files: tuple[dict, ...]


class Service:
    def __init__(self, settings: Settings, registry: Registry | None = None,
                 discord: DiscordAccess | None = None, dify: DifyAccess | None = None):
        self.settings = settings
        self.registry = registry or Registry(settings.database_url, settings.dify_read_url)
        self.discord = discord or DiscordAccess(settings.discord_bot_token)
        self.dify = dify or DifyAccess(settings.knowledge_api_base_url, settings.knowledge_api_key)
        self.cipher = Fernet(settings.encryption_key.encode())
        self.ticket_locks: dict[int, asyncio.Lock] = {}

    def bind_session(self, session: aiohttp.ClientSession | None) -> None:
        """Use the backend's shared HTTP pool for real external integrations."""
        if isinstance(self.discord, DiscordAccess):
            self.discord.session = session
        if isinstance(self.dify, DifyAccess):
            self.dify.session = session

    async def sync_project(self, tenant_id: int) -> Project:
        return (await self._sync_scope(tenant_id)).project

    async def _sync_scope(self, tenant_id: int) -> ValidatedScope:
        project = await asyncio.to_thread(self.registry.get_project, tenant_id)
        if project is None:
            raise Denied("Unknown project")
        try:
            view_started = perf_counter()
            selection = await asyncio.to_thread(self.registry.published_selection, project.dify_app_id)
            view_ms = (perf_counter() - view_started) * 1000
            if selection is None:
                raise Unavailable("Published Retrieval selection is absent")
            workflow_id, datasets = selection
            # Validate all documents each time: a new document must not enter
            # retrieval merely because the same Knowledge Base was previously safe.
            validation_started = perf_counter()
            files = await self.dify.project_files(tenant_id, datasets)
            validation_ms = (perf_counter() - validation_started) * 1000
            LOG.info("Project %s preflight: published_view_ms=%.1f document_validation_ms=%.1f datasets=%s",
                     tenant_id, view_ms, validation_ms, len(datasets))
            if (project.published_workflow_id != workflow_id or project.status != "active"
                    or await asyncio.to_thread(self.registry.datasets, tenant_id) != datasets):
                await asyncio.to_thread(self.registry.activate_project, tenant_id, workflow_id, datasets)
            current = await asyncio.to_thread(self.registry.get_project, tenant_id)
            if current is None:
                raise Unavailable("Project disappeared during sync")
            if (current.dify_app_id, current.dify_api_key_ciphertext, current.guild_id,
                    current.discord_role_id) != (project.dify_app_id, project.dify_api_key_ciphertext,
                                                  project.guild_id, project.discord_role_id):
                raise Unavailable("Project registration changed during sync")
            return ValidatedScope(current, workflow_id, frozenset(datasets), tuple(files))
        except (IntegrationError, ValueError, Unavailable) as exc:
            LOG.warning("Project %s sync failed: %s", tenant_id, exc)
            await asyncio.to_thread(self.registry.suspend_project, tenant_id, str(exc))
            raise Unavailable("Project knowledge is not ready") from exc
        except Exception as exc:
            # Database or unexpected failures must never fall back to an old
            # project scope. Do not log credentials or the workflow graph.
            LOG.exception("Project %s sync failed unexpectedly", tenant_id)
            raise Unavailable("Project knowledge is unavailable") from exc

    async def eligible_projects(self, guild_id: int, user_id: int) -> list[dict]:
        if guild_id != self.settings.guild_id:
            raise Denied("Guild is not configured")
        try:
            roles = await self.discord.member_roles(guild_id, user_id)
        except IntegrationError as exc:
            raise Unavailable("Discord membership is unavailable") from exc
        projects = await asyncio.to_thread(self.registry.projects)
        result = []
        for project in projects:
            if project.guild_id == guild_id and project.discord_role_id in roles:
                try:
                    current = await self.sync_project(project.tenant_id)
                except Unavailable:
                    continue
                result.append({"tenant_id": current.tenant_id, "tenant_name": current.tenant_name})
        return result

    async def _authorize_project(self, guild_id: int, user_id: int, tenant_id: int) -> ValidatedScope:
        if guild_id != self.settings.guild_id:
            raise Denied("Guild is not configured")
        project = await asyncio.to_thread(self.registry.get_project, tenant_id)
        if project is None or project.guild_id != guild_id:
            raise Denied("Project is unavailable")
        try:
            roles = await self.discord.member_roles(guild_id, user_id)
        except IntegrationError as exc:
            raise Unavailable("Discord membership is unavailable") from exc
        if project.discord_role_id not in roles:
            raise Denied("Project role is missing")
        scope = await self._sync_scope(tenant_id)
        if (scope.project.guild_id, scope.project.discord_role_id) != (guild_id, project.discord_role_id):
            raise Unavailable("Project membership mapping changed during authorization")
        return scope

    async def create_ticket(self, *, guild_id: int, user_id: int, thread_id: int,
                            tenant_id: int) -> None:
        await self._authorize_project(guild_id, user_id, tenant_id)
        await asyncio.to_thread(self.registry.create_ticket,
                                Ticket(thread_id, guild_id, user_id, tenant_id, None))

    async def _authorize_ticket(self, thread_id: int, guild_id: int, user_id: int) -> tuple[ValidatedScope, Ticket]:
        ticket = await asyncio.to_thread(self.registry.get_ticket, thread_id)
        if ticket is None or ticket.guild_id != guild_id or ticket.discord_user_id != user_id:
            raise Denied("Ticket is not assigned to this member")
        if ticket.closed_at is not None:
            raise Denied("Ticket is closed")
        project = await self._authorize_project(guild_id, user_id, ticket.tenant_id)
        return project, ticket

    async def close_ticket(self, thread_id: int, guild_id: int, user_id: int) -> bool:
        lock = self.ticket_locks.setdefault(thread_id, asyncio.Lock())
        async with lock:
            ticket = await asyncio.to_thread(self.registry.get_ticket, thread_id)
            if ticket is None or ticket.guild_id != guild_id or ticket.discord_user_id != user_id:
                raise Denied("Ticket is not assigned to this member")
            if ticket.closed_at is not None:
                return False
            # Closing one's own ticket does not require a current project role:
            # it performs no retrieval and must remain possible after revocation.
            return await asyncio.to_thread(self.registry.close_ticket, thread_id, guild_id, user_id)

    async def ticket_files(self, thread_id: int, guild_id: int, user_id: int) -> list[dict]:
        lock = self.ticket_locks.setdefault(thread_id, asyncio.Lock())
        async with lock:
            scope, _ = await self._authorize_ticket(thread_id, guild_id, user_id)
            # The adapter needs display fields only, not the registry envelope.
            return [{key: file[key] for key in ("name", "dataset_name", "status")}
                    for file in scope.files]

    async def ask(self, thread_id: int, guild_id: int, user_id: int,
                  question: str) -> str:
        if not question.strip() or len(question) > 2000:
            raise Denied("Question length is invalid")
        lock = self.ticket_locks.setdefault(thread_id, asyncio.Lock())
        async with lock:
            started = perf_counter()
            scope, ticket = await self._authorize_ticket(thread_id, guild_id, user_id)
            project = scope.project
            preflight_ms = (perf_counter() - started) * 1000
            try:
                app_key = self.cipher.decrypt(project.dify_api_key_ciphertext).decode()
                source_registry = registry_payload(
                    tenant_id=ticket.tenant_id, workflow_id=scope.workflow_id,
                    dataset_ids=scope.dataset_ids, files=scope.files, question=question,
                )
                dify_started = perf_counter()
                answer, conversation_id = await self.dify.ask(
                    app_key, question=question,
                    user_key=f"aw5:{project.tenant_id}:{user_id}:{thread_id}",
                    conversation_id=ticket.dify_conversation_id,
                    registry_json=source_registry, workflow_id=scope.workflow_id,
                )
                dify_ms = (perf_counter() - dify_started) * 1000
            except (IntegrationError, InvalidToken, ValueError) as exc:
                # IntegrationError contains only a status or fixed validation text;
                # never log the question, app key, answer, or response body.
                LOG.warning("Project %s Dify ask failed: %s", project.tenant_id, exc)
                raise Unavailable("Dify answer is unavailable") from exc
            saved = await asyncio.to_thread(self.registry.set_conversation, thread_id, conversation_id)
            if not saved:
                raise Denied("Ticket closed while the answer was running")
            LOG.info("Project %s question timing: preflight_ms=%.1f dify_ms=%.1f total_ms=%.1f",
                     project.tenant_id, preflight_ms, dify_ms,
                     (perf_counter() - started) * 1000)
            return answer

    async def register_project(self, *, name: str, role_id: int, app_id: str,
                               app_key: str, tenant_id: int) -> Project:
        if not name.strip() or len(name) > 70 or not app_key.strip():
            raise Denied("Project name or Dify app key is invalid")
        try:
            parsed_app_id = UUID(app_id)
        except ValueError as exc:
            raise Denied("Dify app ID is invalid") from exc
        if role_id <= 0:
            raise Denied("Discord role is unavailable")
        try:
            role_found = await self.discord.role_exists(self.settings.guild_id, role_id)
        except IntegrationError as exc:
            raise Unavailable("Discord role lookup is unavailable") from exc
        if not role_found:
            raise Denied("Discord role is unavailable")
        if type(tenant_id) is not int or not 0 < tenant_id <= 2**63 - 1:
            raise Denied("AW5 tenant ID is invalid")
        if not await asyncio.to_thread(self.registry.verify_app_key, str(parsed_app_id), app_key.strip()):
            raise Denied("Dify app key does not belong to this app")
        encrypted = self.cipher.encrypt(app_key.strip().encode())
        return await asyncio.to_thread(
            self.registry.register_project,
            name=name.strip(), guild_id=self.settings.guild_id, role_id=role_id,
            app_id=parsed_app_id, encrypted_key=encrypted, tenant_id=tenant_id,
        )
