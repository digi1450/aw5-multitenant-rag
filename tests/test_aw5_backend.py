import asyncio
from datetime import datetime
import unittest
from unittest.mock import AsyncMock, MagicMock

from cryptography.fernet import Fernet

from aw5_backend.api import build_app
from aw5_backend.config import Settings
from aw5_backend.db import Project, Ticket
from aw5_backend.integrations import DifyAccess, DiscordAccess, IntegrationError, _metadata_tenant
from aw5_backend.service import Denied, Service, Unavailable


def settings() -> Settings:
    return Settings("unused-aw5-db", "unused-dify-db", "fake-discord-token", "bot-token",
                    "admin-token", Fernet.generate_key().decode(), "http://api:5001/v1",
                    "fake-knowledge-key", 10)


def project(tenant_id=1, role_id=101, status="active", workflow="11111111-1111-1111-1111-111111111111"):
    return Project(tenant_id, f"Project {tenant_id}", 10, role_id,
                   "6647a5da-36d7-4c90-b0e7-a5b37f3e9de2",
                   b"encrypted", status, workflow, None, datetime.now())


class MetadataTests(unittest.TestCase):
    def test_exact_aw5_tenant_metadata(self):
        self.assertEqual(_metadata_tenant({"doc_metadata": {"tenant_id": 1}}), "1")
        self.assertEqual(_metadata_tenant({"doc_metadata": [{"name": "tenant_id", "value": "2"}]}), "2")
        self.assertIsNone(_metadata_tenant({"doc_metadata": {"tenant_id": True}}))


class DocumentScanTests(unittest.TestCase):
    def test_parallel_dataset_scan_still_rejects_wrong_tenant(self):
        async def check():
            first = "11111111-1111-1111-1111-111111111111"
            second = "22222222-2222-2222-2222-222222222222"
            dify = DifyAccess("http://unused/v1", "key")
            active = 0
            max_active = 0
            document_tenants = {first: 1, second: 1}

            async def pages(path):
                nonlocal active, max_active
                if path == "/datasets":
                    for dataset_id in (first, second):
                        yield {"id": dataset_id, "name": dataset_id}
                    return
                dataset_id = path.split("/")[2]
                active += 1
                max_active = max(max_active, active)
                try:
                    await asyncio.sleep(0)
                    yield {"name": f"{dataset_id}.pdf", "doc_metadata": {"tenant_id": document_tenants[dataset_id]},
                           "enabled": True, "archived": False, "indexing_status": "completed"}
                finally:
                    active -= 1

            dify._pages = pages
            files = await dify.project_files(1, {first, second})
            self.assertEqual(len(files), 2)
            self.assertEqual(max_active, 2)
            document_tenants[second] = 2
            with self.assertRaises(IntegrationError):
                await dify.project_files(1, {first, second})
        asyncio.run(check())


class DifyResponseTests(unittest.TestCase):
    def test_json_response_arriving_in_multiple_chunks(self):
        class Content:
            async def iter_chunked(self, size):
                yield b'{"answer": "hel'
                await asyncio.sleep(0)
                yield b'lo", "conversation_id": "conversation"}'

        class Response:
            status = 200
            content_length = None
            headers = {"Content-Type": "application/json"}
            content = Content()

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

        class Session:
            def request(self, *args, **kwargs):
                return Response()

        async def check():
            dify = DifyAccess("http://unused/v1", "key", Session())
            answer, conversation = await dify.ask(
                "app-key", question="question", user_key="user", conversation_id=None,
            )
            self.assertEqual((answer, conversation), ("hello", "conversation"))

        asyncio.run(check())


class ServiceTests(unittest.TestCase):
    def build(self):
        registry = MagicMock()
        discord = MagicMock()
        dify = MagicMock()
        service = Service(settings(), registry, discord, dify)
        registry.get_project.return_value = project()
        registry.published_selection.return_value = ("11111111-1111-1111-1111-111111111111",
                                                      {"22222222-2222-2222-2222-222222222222"})
        registry.datasets.return_value = {"22222222-2222-2222-2222-222222222222"}
        discord.member_roles = AsyncMock(return_value={101})
        dify.project_files = AsyncMock(return_value=[{"name": "SDS.pdf", "dataset_name": "SDS", "status": "available"}])
        return service, registry, discord, dify

    def test_role_revocation_blocks_question_before_dify(self):
        async def check():
            service, registry, discord, dify = self.build()
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            discord.member_roles.return_value = set()
            with self.assertRaises(Denied):
                await service.ask(40, 10, 30, "Question")
            dify.ask.assert_not_called()
        asyncio.run(check())

    def test_owner_can_close_after_role_revocation_and_cannot_ask_again(self):
        async def check():
            service, registry, discord, dify = self.build()
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            registry.close_ticket.return_value = True
            discord.member_roles.return_value = set()
            self.assertTrue(await service.close_ticket(40, 10, 30))
            registry.close_ticket.assert_called_once_with(40, 10, 30)
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None, datetime.now())
            self.assertFalse(await service.close_ticket(40, 10, 30))
            with self.assertRaises(Denied):
                await service.ask(40, 10, 30, "After closing")
            with self.assertRaises(Denied):
                await service.ticket_files(40, 10, 30)
            dify.ask.assert_not_called()
            self.assertEqual(dify.project_files.await_count, 0)
        asyncio.run(check())

    def test_other_user_cannot_close_ticket(self):
        async def check():
            service, registry, _, _ = self.build()
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            with self.assertRaises(Denied):
                await service.close_ticket(40, 10, 31)
            registry.close_ticket.assert_not_called()
        asyncio.run(check())

    def test_close_waits_for_active_answer(self):
        async def check():
            service, registry, _, dify = self.build()
            original = project()
            registry.get_project.return_value = Project(
                original.tenant_id, original.tenant_name, original.guild_id,
                original.discord_role_id, original.dify_app_id,
                service.cipher.encrypt(b"app-key"), original.status,
                original.published_workflow_id, original.last_sync_error,
                original.synced_at,
            )
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            registry.close_ticket.return_value = True
            entered = asyncio.Event()
            release = asyncio.Event()

            async def answer(*args, **kwargs):
                entered.set()
                await release.wait()
                return "Answer", "conversation"

            dify.ask = AsyncMock(side_effect=answer)
            asking = asyncio.create_task(service.ask(40, 10, 30, "Question"))
            await asyncio.wait_for(entered.wait(), timeout=2)
            closing = asyncio.create_task(service.close_ticket(40, 10, 30))
            await asyncio.sleep(0)
            registry.close_ticket.assert_not_called()
            release.set()
            self.assertEqual(await asking, "Answer")
            self.assertTrue(await closing)
            registry.close_ticket.assert_called_once()
        asyncio.run(check())

    def test_each_question_rechecks_roles_and_document_metadata(self):
        async def check():
            service, registry, discord, dify = self.build()
            original = project()
            registry.get_project.return_value = Project(
                original.tenant_id, original.tenant_name, original.guild_id,
                original.discord_role_id, original.dify_app_id,
                service.cipher.encrypt(b"app-key"), original.status,
                original.published_workflow_id, original.last_sync_error,
                original.synced_at,
            )
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            dify.ask = AsyncMock(return_value=("Answer", "conversation"))
            await service.ask(40, 10, 30, "First question")
            await service.ask(40, 10, 30, "Second question")
            self.assertEqual(discord.member_roles.await_count, 2)
            self.assertEqual(dify.project_files.await_count, 2)
            self.assertEqual(dify.ask.await_count, 2)
        asyncio.run(check())

    def test_new_mismatched_document_blocks_next_question_without_publish(self):
        async def check():
            service, registry, _, dify = self.build()
            original = project()
            registry.get_project.return_value = Project(
                original.tenant_id, original.tenant_name, original.guild_id,
                original.discord_role_id, original.dify_app_id,
                service.cipher.encrypt(b"app-key"), original.status,
                original.published_workflow_id, original.last_sync_error,
                original.synced_at,
            )
            registry.get_ticket.return_value = Ticket(40, 10, 30, 1, None)
            dify.ask = AsyncMock(return_value=("Answer", "conversation"))
            await service.ask(40, 10, 30, "First question")
            dify.project_files.side_effect = IntegrationError("Document tenant metadata is missing or mismatched")
            with self.assertRaises(Unavailable):
                await service.ask(40, 10, 30, "Second question")
            self.assertEqual(dify.ask.await_count, 1)
            registry.suspend_project.assert_called_once()
        asyncio.run(check())

    def test_http_session_follows_app_lifecycle(self):
        async def check():
            registry = MagicMock()
            registry.projects.return_value = []
            service = Service(settings(), registry, DiscordAccess("token"),
                              DifyAccess("http://api:5001/v1", "key"))
            app = build_app(settings(), service)
            app.freeze()
            await app.startup()
            try:
                session = service.discord.session
                self.assertIsNotNone(session)
                self.assertIs(session, service.dify.session)
                self.assertFalse(session.closed)
            finally:
                await app.cleanup()
            self.assertTrue(session.closed)
            self.assertIsNone(service.discord.session)
            self.assertIsNone(service.dify.session)
        asyncio.run(check())

    def test_published_change_updates_registry_without_manual_ids(self):
        async def check():
            service, registry, _, dify = self.build()
            registry.published_selection.return_value = (
                "33333333-3333-3333-3333-333333333333", {"44444444-4444-4444-4444-444444444444"})
            current = await service.sync_project(1)
            self.assertEqual(current.tenant_id, 1)
            registry.activate_project.assert_called_once_with(
                1, "33333333-3333-3333-3333-333333333333",
                {"44444444-4444-4444-4444-444444444444"})
            dify.project_files.assert_awaited_once()
        asyncio.run(check())

    def test_mismatched_document_fails_closed(self):
        async def check():
            service, registry, _, dify = self.build()
            dify.project_files.side_effect = IntegrationError("Document tenant metadata is missing or mismatched")
            with self.assertRaises(Unavailable):
                await service.sync_project(1)
            registry.suspend_project.assert_called_once()
        asyncio.run(check())

    def test_user_with_two_roles_gets_two_projects(self):
        async def check():
            service, registry, discord, _ = self.build()
            registry.projects.return_value = [project(1, 101), project(2, 202)]
            discord.member_roles.return_value = {101, 202}
            service.sync_project = AsyncMock(side_effect=[project(1, 101), project(2, 202)])
            result = await service.eligible_projects(10, 30)
            self.assertEqual([item["tenant_id"] for item in result], [1, 2])
        asyncio.run(check())
