"""Offline administrator trust-boundary and provisioning failure tests."""
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from aiohttp import web
from cryptography.fernet import Fernet

from aw5_backend.onboarding import AdminPortal, COOKIE, positive_id
from aw5_backend.service import Denied
from aw5_backend.integrations import IntegrationError
from aw5_backend.db import Registry
from tests.test_aw5_backend import settings, project


class AdminTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.service = SimpleNamespace(
            settings=replace(settings(), admin_channel_id=20, admin_role_id=30),
            discord=SimpleNamespace(member_roles=AsyncMock(return_value={30}),
                admin_role_options=AsyncMock(return_value={"roles": [{"id": "101", "name": "Project"}], "can_create": True,
                                                          "role_names": {"101": "Project"}}),
                create_project_role=AsyncMock(return_value=102)),
            dify=SimpleNamespace(project_files=AsyncMock(return_value=[]),
                _json=AsyncMock(return_value={"user_input_form": [{"paragraph": {"variable": "aw5_registry_json", "required": True}}]})),
            registry=MagicMock(), cipher=Fernet(Fernet.generate_key()), sync_project=AsyncMock(return_value=project(7)),
        )
        self.service.registry.get_enrollment.return_value = None
        self.service.registry.begin_enrollment.return_value = None
        self.service.registry.verify_app_key.return_value = True
        self.app_id = str(uuid4())
        self.service.registry.resolve_app_key.return_value = self.app_id
        self.service.registry.published_selection.return_value = ('workflow', {'dataset'})
        self.service.registry.projects.return_value = []
        self.service.registry.register_project.return_value = project(7)
        self.service.registry.get_project.return_value = project(7)
        self.service.registry.begin_role_change.return_value = None
        self.service.registry.complete_role_change.return_value = project(7, role_id=102)
        self.portal = AdminPortal(self.service)
        self.data = dict(tenant_id='7', request_id=str(uuid4()),
                         tenant_name='Project', dify_app_api_key='fixture-key', role_mode='new')

    def request(self, data=None, *, cookie=None, csrf='', origin='http://127.0.0.1:8765', method='POST'):
        return SimpleNamespace(headers={'Origin': origin, 'X-AW5-CSRF': csrf},
                               cookies={COOKIE: cookie} if cookie else {}, method=method,
                               json=AsyncMock(return_value=data))

    async def login(self):
        link = await self.portal.issue_link(10, 20, 50)
        token = link.split('login=')[1]
        response = await self.portal.exchange(self.request({'token': token}))
        import json
        return token, response.cookies[COOKIE].value, json.loads(response.text)['csrf']

    async def test_model_resolves_registered_role_without_offering_it_for_enrollment(self):
        import json
        _, cookie, _ = await self.login()
        self.service.registry.projects.return_value = [project(7)]
        response = await self.portal.model(self.request(cookie=cookie, method='GET'))
        model = json.loads(response.text)
        self.assertEqual(model['projects'][0]['discord_role_name'], 'Project')
        self.assertEqual(model['projects'][0]['discord_role_id'], '101')
        self.assertEqual(model['roles'], [])

    async def test_model_keeps_role_id_when_name_is_missing(self):
        import json
        _, cookie, _ = await self.login()
        self.service.registry.projects.return_value = [project(7, role_id=999)]
        model = json.loads((await self.portal.model(self.request(cookie=cookie, method='GET'))).text)
        self.assertIsNone(model['projects'][0]['discord_role_name'])
        self.assertEqual(model['projects'][0]['discord_role_id'], '999')

    async def test_model_role_lookup_failure_preserves_display_and_disables_provisioning(self):
        import json
        _, cookie, _ = await self.login()
        self.service.registry.projects.return_value = [project(7)]
        self.service.discord.admin_role_options.side_effect = IntegrationError('unavailable')
        model = json.loads((await self.portal.model(self.request(cookie=cookie, method='GET'))).text)
        self.assertIsNone(model['projects'][0]['discord_role_name'])
        self.assertEqual(model['roles'], [])
        self.assertFalse(model['can_create'])

    async def test_wrong_channel_and_role_never_issue_link(self):
        with self.assertRaises(Denied): await self.portal.issue_link(10, 21, 50)
        self.service.discord.member_roles.assert_not_awaited()
        self.service.discord.member_roles.return_value = set()
        with self.assertRaises(Denied): await self.portal.issue_link(10, 20, 50)
        self.assertFalse(self.portal.grants)

    async def test_link_single_use_and_cookie_flags(self):
        token, cookie, csrf = await self.login()
        self.assertTrue(cookie and csrf)
        with self.assertRaises(Denied): await self.portal.exchange(self.request({'token': token}))
        link = await self.portal.issue_link(10, 20, 50)
        response = await self.portal.exchange(self.request({'token': link.split('login=')[1]}))
        self.assertTrue(response.cookies[COOKIE]['httponly'])
        self.assertEqual(response.cookies[COOKIE]['samesite'], 'Strict')

    async def test_origin_csrf_and_revocation(self):
        _, cookie, csrf = await self.login()
        with self.assertRaises(web.HTTPForbidden): await self.portal.identity(self.request(cookie=cookie, csrf=csrf, origin='https://evil.example'))
        with self.assertRaises(Denied): await self.portal.identity(self.request(cookie=cookie))
        self.service.discord.member_roles.return_value = set()
        with self.assertRaises(Denied): await self.portal.identity(self.request(cookie=cookie, csrf=csrf))
        self.service.registry.register_project.assert_not_called()

    async def test_expired_grant_and_session(self):
        token, cookie, csrf = await self.login()
        self.portal.sessions[self.portal.digest(cookie)] = (0, 50, csrf)
        with self.assertRaises(Denied): await self.portal.identity(self.request(cookie=cookie, csrf=csrf))
        self.portal.grants[self.portal.digest(token)] = (0, 50)
        with self.assertRaises(Denied): await self.portal.exchange(self.request({'token': token}))

    async def test_wrong_app_key_or_metadata_never_create_role(self):
        self.service.registry.verify_app_key.return_value = False
        with self.assertRaises(ValueError): await self.portal.enroll(50, self.data)
        self.service.discord.create_project_role.assert_not_awaited()
        self.service.registry.verify_app_key.return_value = True
        self.service.dify.project_files.side_effect = IntegrationError('Wrong tenant')
        with self.assertRaises(IntegrationError): await self.portal.enroll(50, self.data)
        self.service.discord.create_project_role.assert_not_awaited()
        self.service.registry.begin_enrollment.assert_not_called()

    async def test_optional_registry_input_is_rejected(self):
        self.service.dify._json.return_value['user_input_form'][0]['paragraph']['required'] = False
        with self.assertRaises(ValueError): await self.portal.enroll(50, self.data)
        self.service.discord.create_project_role.assert_not_awaited()

    async def test_explicit_id_encrypted_key_and_replay(self):
        result = await self.portal.enroll(50, self.data)
        self.assertEqual(result['tenant_id'], '7')
        arguments = self.service.registry.register_project.call_args.kwargs
        self.assertEqual(arguments['tenant_id'], 7)
        self.assertEqual(str(arguments['app_id']), self.app_id)
        self.service.registry.resolve_app_key.assert_called_once_with('fixture-key')
        self.service.registry.verify_app_key.assert_called_once_with(self.app_id, 'fixture-key')
        self.assertEqual(self.service.cipher.decrypt(arguments['encrypted_key']), b'fixture-key')
        self.assertNotIn('fixture-key', str(result))
        self.service.registry.get_enrollment.return_value = {'state': 'completed'}
        self.service.registry.get_project.return_value = project(7)
        await self.portal.enroll(50, self.data)
        self.assertEqual(self.service.discord.create_project_role.await_count, 1)

    async def test_unresolved_key_stops_before_side_effects(self):
        self.service.registry.resolve_app_key.side_effect = ValueError('Not exactly one app')
        with self.assertRaises(ValueError): await self.portal.enroll(50, self.data)
        self.service.registry.verify_app_key.assert_not_called()
        self.service.registry.published_selection.assert_not_called()
        self.service.registry.begin_enrollment.assert_not_called()
        self.service.registry.register_project.assert_not_called()
        self.service.discord.create_project_role.assert_not_awaited()

    async def test_legacy_app_id_cannot_override_resolved_identity(self):
        self.data['dify_app_id'] = str(uuid4())
        with self.assertRaises(ValueError): await self.portal.enroll(50, self.data)
        self.service.registry.begin_enrollment.assert_not_called()
        self.service.discord.create_project_role.assert_not_awaited()
        self.data['dify_app_id'] = self.app_id
        await self.portal.enroll(50, self.data)
        self.assertEqual(str(self.service.registry.register_project.call_args.kwargs['app_id']), self.app_id)

    async def test_revoked_admin_cannot_resolve_key(self):
        self.service.discord.member_roles.return_value = set()
        with self.assertRaises(Denied): await self.portal.enroll(50, self.data)
        self.service.registry.resolve_app_key.assert_not_called()

    async def test_invalid_keys_are_not_resolved(self):
        for key in ('', '  ', None, True, 'x' * 513):
            with self.subTest(key_type=type(key).__name__):
                with self.assertRaises(ValueError):
                    await self.portal.enroll(50, {**self.data, 'dify_app_api_key': key})
        self.service.registry.resolve_app_key.assert_not_called()

    async def test_change_role_creates_new_without_changing_app(self):
        result = await self.portal.change_role(50, 7, {'request_id': str(uuid4()), 'role_mode': 'new'})
        self.assertEqual(result['discord_role_id'], '102')
        self.service.registry.begin_role_change.assert_called_once()
        self.service.registry.complete_role_change.assert_called_once()
        self.service.registry.register_project.assert_not_called()
        self.service.dify.project_files.assert_not_awaited()
        self.service.discord.create_project_role.assert_awaited_once_with(10, 'Project 7')

    async def test_change_role_selects_existing_and_replay_does_not_create(self):
        data = {'request_id': str(uuid4()), 'role_mode': 'existing', 'discord_role_id': '101'}
        await self.portal.change_role(50, 7, data)
        self.service.discord.create_project_role.assert_not_awaited()
        self.service.registry.begin_role_change.return_value = {'state': 'completed'}
        await self.portal.change_role(50, 7, data)
        self.assertEqual(self.service.registry.complete_role_change.call_count, 1)

    async def test_role_change_failures_are_reserved_and_not_retried(self):
        data = {'request_id': str(uuid4()), 'role_mode': 'new'}
        self.service.discord.create_project_role.side_effect = IntegrationError('uncertain')
        with self.assertRaises(IntegrationError): await self.portal.change_role(50, 7, data)
        self.service.registry.fail_role_change.assert_called_once_with(data['request_id'], None)
        self.service.registry.complete_role_change.assert_not_called()
        self.service.registry.begin_role_change.return_value = {'state': 'needs_attention'}
        with self.assertRaises(web.HTTPConflict): await self.portal.change_role(50, 7, data)
        self.assertEqual(self.service.discord.create_project_role.await_count, 1)

    async def test_role_change_rejects_other_project_role_missing_role_and_permissions(self):
        self.service.registry.projects.return_value = [project(8, role_id=101)]
        import psycopg
        data = {'request_id': str(uuid4()), 'role_mode': 'existing', 'discord_role_id': '101'}
        with self.assertRaises(psycopg.errors.UniqueViolation): await self.portal.change_role(50, 7, data)
        data['discord_role_id'] = '999'
        with self.assertRaises(ValueError): await self.portal.change_role(50, 7, data)
        self.service.discord.admin_role_options.return_value['can_create'] = False
        with self.assertRaises(ValueError): await self.portal.change_role(50, 7, {**data, 'role_mode': 'new'})
        self.service.registry.begin_role_change.assert_not_called()

    async def test_role_change_rechecks_admin_after_creation(self):
        self.service.discord.member_roles.side_effect = [{30}, {30}, set()]
        data = {'request_id': str(uuid4()), 'role_mode': 'new'}
        with self.assertRaises(Denied): await self.portal.change_role(50, 7, data)
        self.service.registry.complete_role_change.assert_not_called()
        self.service.registry.fail_role_change.assert_called_once_with(data['request_id'], 102)

    async def test_ambiguous_creation_is_reserved_and_not_retried(self):
        self.service.discord.create_project_role.side_effect = IntegrationError('Uncertain response')
        with self.assertRaises(IntegrationError): await self.portal.enroll(50, self.data)
        self.service.registry.finish_enrollment.assert_called_once_with(self.data['request_id'], 'needs_attention', None)
        self.service.registry.get_enrollment.return_value = {'state': 'needs_attention'}
        with self.assertRaises(web.HTTPConflict): await self.portal.enroll(50, self.data)
        self.assertEqual(self.service.discord.create_project_role.await_count, 1)

    async def test_publish_change_after_role_creation_is_not_registered(self):
        self.service.registry.published_selection.side_effect = [('workflow', {'dataset'}), ('new-workflow', {'dataset'})]
        from aw5_backend.service import Unavailable
        with self.assertRaises(Unavailable): await self.portal.enroll(50, self.data)
        self.service.registry.register_project.assert_not_called()
        self.assertEqual(self.service.registry.finish_enrollment.call_args.args[1], 'needs_attention')

    async def test_existing_role_and_completed_replay(self):
        self.data.update(role_mode='existing', discord_role_id='101')
        await self.portal.enroll(50, self.data)
        self.service.discord.create_project_role.assert_not_awaited()
        self.service.registry.projects.return_value = [project(7)]
        self.service.registry.get_enrollment.return_value = {'state': 'completed'}
        self.service.registry.get_project.return_value = project(7)
        self.assertEqual((await self.portal.enroll(50, self.data))['tenant_id'], '7')

    async def test_permissions_missing_blocks_new_role(self):
        self.service.discord.admin_role_options.return_value['can_create'] = False
        with self.assertRaises(ValueError): await self.portal.enroll(50, self.data)
        self.service.registry.begin_enrollment.assert_not_called()

    def test_identifiers_reject_boolean_float_overflow(self):
        for value in (True, 1.5, '1.5', '-1', '0', str(2**63)):
            with self.assertRaises(ValueError): positive_id(value)
        self.assertEqual(positive_id('1555931570886410270'), 1555931570886410270)

class PortalHTTPTests(unittest.IsolatedAsyncioTestCase):
    setUp = AdminTests.setUp
    async def test_routes_security_headers_and_no_service_token_login(self):
        from aiohttp.test_utils import TestClient, TestServer
        from aw5_backend.api import build_app
        app = build_app(self.service.settings, self.service)
        app.cleanup_ctx.clear()  # Offline dependencies above; no databases or live Discord.
        client = TestClient(TestServer(app))
        try:
            await client.start_server()
            response = await client.get('/admin')
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])
            html = await response.text()
            self.assertIn('dify_app_api_key', html)
            self.assertNotIn('name="dify_app_id"', html)
            self.assertEqual((await client.post('/v1/admin/links', json={})).status, 401)
            response = await client.post('/v1/admin/links', headers={'Authorization': 'Bearer bot-token'},
                                         json={'guild_id': '10', 'channel_id': '20', 'user_id': '50'})
            self.assertEqual(response.status, 200)
            token = (await response.json())['url'].split('login=')[1]
            response = await client.post('/v1/admin/portal/session', json={'token': token},
                                         headers={'Origin': 'https://evil.example'})
            self.assertEqual(response.status, 403)
            response = await client.post('/v1/admin/portal/session', json={'token': token},
                                         headers={'Origin': 'http://127.0.0.1:8765'})
            self.assertEqual(response.status, 200)
            self.assertIn('HttpOnly', response.headers['Set-Cookie'])
            cookie = response.cookies[COOKIE].value
            response = await client.get('/v1/admin/portal/model', headers={'Cookie': COOKIE+'='+cookie})
            self.assertEqual(response.status, 200)
            csrf = (await response.json())['csrf']
            response = await client.post('/v1/admin/portal/projects', headers={'Cookie': COOKIE+'='+cookie,
                                         'Origin': 'http://127.0.0.1:8765'}, json=self.data)
            self.assertEqual(response.status, 403)
            response = await client.post('/v1/admin/portal/projects', headers={'Cookie': COOKIE+'='+cookie,
                                         'Origin': 'http://127.0.0.1:8765', 'X-AW5-CSRF': csrf}, json=self.data)
            self.assertEqual(response.status, 201)
            self.assertEqual(str(self.service.registry.register_project.call_args.kwargs['app_id']), self.app_id)
            change = {'request_id': str(uuid4()), 'role_mode': 'new'}
            headers = {'Cookie': COOKIE+'='+cookie, 'Origin': 'http://127.0.0.1:8765'}
            response = await client.post('/v1/admin/portal/projects/7/role', headers=headers, json=change)
            self.assertEqual(response.status, 403)
            self.service.registry.begin_role_change.assert_not_called()
            response = await client.post('/v1/admin/portal/projects/7/role',
                                         headers={**headers, 'X-AW5-CSRF': csrf}, json=change)
            self.assertEqual(response.status, 200)
            self.assertEqual((await response.json())['discord_role_id'], '102')
            deletion = {'confirmation_name': 'Project 7', 'dify_app_id': self.app_id, 'discord_role_id': '102'}
            response = await client.delete('/v1/admin/portal/projects/7', headers=headers, json=deletion)
            self.assertEqual(response.status, 403)
            self.service.registry.delete_project.assert_not_called()
            self.service.registry.delete_project.return_value = {'deleted': True, 'tenant_id': '7', 'deleted_tickets': 0}
            response = await client.delete('/v1/admin/portal/projects/7',
                                           headers={**headers, 'X-AW5-CSRF': csrf}, json=deletion)
            self.assertEqual(response.status, 200)
            self.assertTrue((await response.json())['deleted'])
        finally:
            await client.close()


class RoleChangeRegistryTests(unittest.TestCase):
    def test_completion_changes_only_role_and_commits_journal_together(self):
        from dataclasses import asdict
        request_id = str(uuid4())
        updated = asdict(project(7, role_id=102))
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchone.side_effect = [
                {'state': 'in_progress', 'tenant_id': 7, 'old_role_id': 101}, updated]
            result = Registry('unused', 'unused').complete_role_change(request_id, 102)
            self.assertEqual(result.discord_role_id, 102)
            queries = [call.args for call in db.execute.call_args_list]
            update = next(args for args in queries if 'UPDATE projects' in args[0])
            self.assertIn('SET discord_role_id=%s', update[0])
            self.assertEqual(update[1], (102, 7, 101))
            self.assertNotIn('dify_app_id', update[0])
            self.assertNotIn('tickets', update[0])
            self.assertIn("state='completed'", queries[-1][0])

    def test_concurrent_role_change_does_not_complete_journal(self):
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchone.side_effect = [
                {'state': 'in_progress', 'tenant_id': 7, 'old_role_id': 101}, None]
            with self.assertRaises(ValueError):
                Registry('unused', 'unused').complete_role_change(str(uuid4()), 102)
            self.assertFalse(any("state='completed'" in call.args[0] for call in db.execute.call_args_list))

    def test_reservation_replay_is_actor_and_payload_bound(self):
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchone.return_value = {
                'actor_id': 50, 'tenant_id': 7, 'fingerprint': 'original', 'state': 'completed'}
            registry = Registry('unused', 'unused')
            request_id = str(uuid4())
            self.assertEqual(registry.begin_role_change(request_id, 7, 50, 'original', 101)['state'], 'completed')
            with self.assertRaises(ValueError): registry.begin_role_change(request_id, 7, 51, 'original', 101)
            with self.assertRaises(ValueError): registry.begin_role_change(request_id, 7, 50, 'changed', 101)


class ProjectDeletionTests(unittest.IsolatedAsyncioTestCase):
    setUp = AdminTests.setUp
    request = AdminTests.request
    login = AdminTests.login

    async def delete_request(self, **overrides):
        _, cookie, csrf = await self.login()
        payload = {'confirmation_name': 'Project 7', 'dify_app_id': self.app_id, 'discord_role_id': '101'}
        payload.update(overrides)
        request = self.request(payload, cookie=cookie, csrf=csrf)
        request.match_info = {'tenant_id': '7'}
        return request

    async def test_delete_rechecks_authorization_and_delegates_only_to_aw5_registry(self):
        self.service.registry.delete_project.return_value = {'deleted': True, 'tenant_id': '7', 'deleted_tickets': 2}
        response = await self.portal.delete_project(await self.delete_request())
        self.assertEqual(response.status, 200)
        self.service.registry.delete_project.assert_called_once_with(7, 10, 'Project 7', self.app_id, 101)
        self.service.discord.create_project_role.assert_not_awaited()
        self.service.dify._json.assert_not_awaited()

    async def test_delete_csrf_revocation_and_invalid_confirmation(self):
        request = await self.delete_request()
        request.headers['X-AW5-CSRF'] = ''
        with self.assertRaises(Denied): await self.portal.delete_project(request)
        request = await self.delete_request()
        self.service.discord.member_roles.return_value = set()
        with self.assertRaises(Denied): await self.portal.delete_project(request)
        self.service.discord.member_roles.return_value = {30}
        response = await self.portal.delete_project(await self.delete_request(confirmation_name=''))
        self.assertEqual(response.status, 400)
        self.service.registry.delete_project.assert_not_called()

    async def test_pending_operation_is_conflict(self):
        import psycopg
        self.service.registry.delete_project.side_effect = psycopg.errors.ObjectInUse('pending')
        response = await self.portal.delete_project(await self.delete_request())
        self.assertEqual(response.status, 409)


class ProjectDeletionRegistryTests(unittest.TestCase):
    def fixture(self):
        from dataclasses import asdict
        return asdict(project(7))

    def test_scoped_deletion_and_journal_cleanup_share_transaction(self):
        row = self.fixture()
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchone.side_effect = [row, None]
            db.execute.return_value.rowcount = 2
            result = Registry('unused', 'unused').delete_project(7, 10, row['tenant_name'], row['dify_app_id'], 101)
            self.assertEqual(result['deleted_tickets'], 2)
            deletes = [call.args for call in db.execute.call_args_list if call.args[0].startswith('DELETE')]
            self.assertEqual([sql.split()[2] for sql, _ in deletes],
                             ['tickets', 'project_datasets', 'project_role_changes', 'onboarding_requests', 'projects'])
            self.assertTrue(all(params == (7,) and 'WHERE tenant_id=%s' in sql for sql, params in deletes))
            connect.assert_called_once()

    def test_stale_wrong_guild_or_missing_confirmation_never_deletes(self):
        row = self.fixture()
        for current in (None, {**row, 'guild_id': 999}, {**row, 'tenant_name': 'different'}, {**row, 'discord_role_id': 999}):
            with self.subTest(current=current), patch('aw5_backend.db.psycopg.connect') as connect:
                db = connect.return_value.__enter__.return_value
                db.execute.return_value.fetchone.return_value = current
                with self.assertRaises(ValueError):
                    Registry('unused', 'unused').delete_project(7, 10, row['tenant_name'], row['dify_app_id'], 101)
                self.assertFalse(any(call.args[0].startswith('DELETE') for call in db.execute.call_args_list))

    def test_unresolved_provisioning_journal_is_not_destroyed(self):
        import psycopg
        row = self.fixture()
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchone.side_effect = [row, {'pending': 1}]
            with self.assertRaises(psycopg.errors.ObjectInUse):
                Registry('unused', 'unused').delete_project(7, 10, row['tenant_name'], row['dify_app_id'], 101)
            self.assertFalse(any(call.args[0].startswith('DELETE') for call in db.execute.call_args_list))


class AppKeyResolutionTests(unittest.TestCase):
    def test_digest_only_lookup_resolves_one_app(self):
        import hashlib
        app_id = uuid4()
        with patch('aw5_backend.db.psycopg.connect') as connect:
            db = connect.return_value.__enter__.return_value
            db.execute.return_value.fetchall.return_value = [(app_id,)]
            self.assertEqual(Registry('unused', 'unused').resolve_app_key(' fixture-key '), str(app_id))
            sql, params = db.execute.call_args.args
            self.assertIn('SELECT DISTINCT app_id FROM aw5_app_key_bindings_v1', sql)
            self.assertIn('LIMIT 2', sql)
            self.assertEqual(params, (hashlib.sha256(b'fixture-key').hexdigest(),))
            self.assertNotIn('fixture-key', str(db.execute.call_args))

    def test_missing_ambiguous_or_invalid_identity_is_rejected(self):
        for rows in ([], [(uuid4(),), (uuid4(),)], [(None,)], [('invalid',)]):
            with self.subTest(rows=rows), patch('aw5_backend.db.psycopg.connect') as connect:
                connect.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = rows
                with self.assertRaises(ValueError): Registry('unused', 'unused').resolve_app_key('fixture-key')

    def test_invalid_key_never_opens_database(self):
        with patch('aw5_backend.db.psycopg.connect') as connect:
            for key in ('', ' ', None, True, 'x' * 513):
                with self.assertRaises(ValueError): Registry('unused', 'unused').resolve_app_key(key)
            connect.assert_not_called()
