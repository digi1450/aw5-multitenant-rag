import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock

from aw5_backend.db import Project, Ticket
from aw5_backend.integrations import DifyAccess
from aw5_backend.service import Service, Unavailable
from aw5_backend.source_registry import registry_payload
from dify.code.backend_file_registry import main
from tests.test_aw5_backend import project, settings


DATASET = "22222222-2222-2222-2222-222222222222"
OTHER_DATASET = "33333333-3333-3333-3333-333333333333"
WORKFLOW = "11111111-1111-1111-1111-111111111111"


def document(tenant=7, number=1, name="Design.pdf", kind="SDS", status="available"):
    return {"tenant_id": tenant, "document_id": f"00000000-0000-0000-0000-{number:012d}",
            "dataset_id": DATASET, "name": name, "document_type": kind,
            "dataset_name": "Design knowledge", "status": status}


def payload(files=None, question="Design.pdf", tenant=7):
    return registry_payload(tenant_id=tenant, workflow_id=WORKFLOW,
                            dataset_ids=frozenset({DATASET}),
                            files=tuple(files if files is not None else [document(tenant)]),
                            question=question)


class RegistryContractTests(unittest.TestCase):
    def test_existing_tenant_number_and_old_node_wrapper(self):
        encoded = payload(tenant=83)
        self.assertEqual(json.loads(encoded)["tenant_id"], 83)
        self.assertEqual(main(encoded), {"json": [{"data": [{
            "document_id": document()["document_id"], "document_name": "Design.pdf",
            "document_type": "SDS",
        }]}]})

    def test_mixed_tenants_rejected_before_serialization(self):
        with self.assertRaises(ValueError):
            payload([document(), document(tenant=8, number=2)])

    def test_unselected_dataset_rejected_even_when_name_matches(self):
        file = document()
        file["dataset_id"] = OTHER_DATASET
        with self.assertRaises(ValueError):
            payload([file])

    def test_disabled_archived_and_indexing_documents_not_shortlisted(self):
        files = [document(number=n, status=status) for n, status in enumerate(
            ("disabled", "archived", "indexing"), start=1)]
        self.assertEqual(main(payload(files)), {"json": [{"data": []}]})

    def test_shortlist_is_query_based_not_whole_inventory(self):
        self.assertEqual(main(payload(question="What is the project objective?")), {"json": [{"data": []}]})

    def test_filename_type_and_token_scoring(self):
        files = [document(number=1, name="API notes.pdf", kind="notes"),
                 document(number=2, name="Other.pdf", kind="SDS"),
                 document(number=3, name="Exact.pdf", kind="notes")]
        rows = main(payload(files, question="Exact.pdf SDS API"))["json"][0]["data"]
        self.assertEqual([row["document_name"] for row in rows], ["Exact.pdf", "Other.pdf", "API notes.pdf"])

    def test_duplicate_names_keep_distinct_document_ids_for_ambiguity_checks(self):
        rows = main(payload([document(number=1), document(number=2)]))["json"][0]["data"]
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["document_id"], rows[1]["document_id"])

    def test_duplicate_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            payload([document(), document()])

    def test_missing_document_id_fails_as_validation_error(self):
        file = document()
        del file["document_id"]
        with self.assertRaises(ValueError):
            payload([file])

    def test_shortlist_limit_remains_twenty(self):
        rows = main(payload([document(number=n) for n in range(1, 25)]))["json"][0]["data"]
        self.assertEqual(len(rows), 20)

    def test_malformed_or_wrong_version_is_not_treated_as_empty_registry(self):
        for encoded in ("", "not JSON", "[]", '{"schema_version":"wrong"}'):
            with self.subTest(encoded=encoded), self.assertRaises(ValueError):
                main(encoded)

    def test_duplicate_json_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            main('{"tenant_id":7,"tenant_id":8}')

    def test_node_rejects_document_outside_envelope_selection(self):
        envelope = json.loads(payload())
        envelope["documents"][0]["dataset_id"] = OTHER_DATASET
        with self.assertRaises(ValueError):
            main(json.dumps(envelope))

    def test_names_remain_exact_including_thai_and_punctuation(self):
        name = "ข้อกำหนด, ฉบับใหม่.pdf"
        row = main(payload([document(name=name)], question=name))["json"][0]["data"][0]
        self.assertEqual(row["document_name"], name)

    def test_oversized_payload_fails_instead_of_truncating(self):
        name = "ก" * 30_000
        with self.assertRaises(ValueError):
            payload([document(name=name)], question=name)


class ScopedDispatchTests(unittest.TestCase):
    def test_dispatch_uses_stored_tenant_captured_workflow_and_one_scan_per_question(self):
        async def check():
            registry, discord, dify = MagicMock(), MagicMock(), MagicMock()
            service = Service(settings(), registry, discord, dify)
            p = project(tenant_id=7)
            registry.get_project.return_value = Project(
                p.tenant_id, p.tenant_name, p.guild_id, p.discord_role_id, p.dify_app_id,
                service.cipher.encrypt(b"app-key"), p.status, p.published_workflow_id,
                p.last_sync_error, p.synced_at,
            )
            registry.get_ticket.return_value = Ticket(40, 10, 30, 7, "existing-conversation")
            registry.published_selection.return_value = (WORKFLOW, {DATASET})
            registry.datasets.return_value = {DATASET}
            registry.set_conversation.return_value = True
            discord.member_roles = AsyncMock(return_value={101})
            dify.project_files = AsyncMock(return_value=[document()])
            dify.ask = AsyncMock(return_value=("Answer", "existing-conversation"))
            await service.ask(40, 10, 30, "Design.pdf")
            call = dify.ask.call_args.kwargs
            self.assertEqual(call["workflow_id"], WORKFLOW)
            self.assertEqual(json.loads(call["registry_json"])["tenant_id"], 7)
            self.assertEqual(call["conversation_id"], "existing-conversation")
            self.assertEqual(call["user_key"], "aw5:7:30:40")
            self.assertEqual(dify.project_files.await_count, 1)
            dify.project_files.return_value = [document(), document(number=2, name="Plan.pdf")]
            await service.ask(40, 10, 30, "Plan.pdf")
            next_call = dify.ask.call_args.kwargs
            self.assertEqual(next_call["conversation_id"], "existing-conversation")
            self.assertEqual([row["document_name"] for row in json.loads(next_call["registry_json"])["documents"]],
                             ["Plan.pdf"])
            files = await service.ticket_files(40, 10, 30)
            self.assertEqual(set(files[0]), {"name", "dataset_name", "status"})
            self.assertEqual(dify.project_files.await_count, 3)
            dify.project_files.return_value = [document(tenant=8)]
            with self.assertRaises(Unavailable):
                await service.ask(40, 10, 30, "Design.pdf")
            self.assertEqual(dify.ask.await_count, 2)
        asyncio.run(check())

    def test_chat_api_forwards_registry_as_string_and_pinned_version(self):
        async def check():
            dify = DifyAccess("http://unused/v1", "key")
            dify._json = AsyncMock(return_value={"answer": "Answer", "conversation_id": "conversation"})
            encoded = payload()
            await dify.ask("app-key", question="Design.pdf", user_key="user",
                           conversation_id="conversation", registry_json=encoded, workflow_id=WORKFLOW)
            request = dify._json.call_args.kwargs["payload"]
            self.assertEqual(request["workflow_id"], WORKFLOW)
            self.assertEqual(request["inputs"], {"aw5_registry_json": encoded})
            self.assertEqual(request["conversation_id"], "conversation")
        asyncio.run(check())
