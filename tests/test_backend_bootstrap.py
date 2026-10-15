"""Backend bootstrap must obtain Dify credentials outside the bot environment."""
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from aw5_backend import bootstrap_local


class BootstrapSecretBoundaryTests(unittest.TestCase):
    def workspace(self, folder):
        root = Path(folder)
        (root / 'discord_bot').mkdir()
        (root / 'aw5_backend').mkdir()
        (root / 'discord_bot/.env').write_text(
            'AW5_DISCORD_BOT_TOKEN=fixture-discord\n'
            'AW5_DISCORD_GUILD_ID=10\n'
            'AW5_DISCORD_START_CHANNEL_ID=20\n')
        (root / 'aw5_backend/dify_read_view.sql').write_text('-- fixture view; no database is called\n')
        return root

    def test_new_setup_without_any_bot_dify_key(self):
        with TemporaryDirectory() as folder:
            root = self.workspace(folder)
            with patch.object(bootstrap_local, 'ROOT', root), \
                 patch.object(bootstrap_local.getpass, 'getpass', return_value='fixture-backend-knowledge') as prompt, \
                 patch.object(bootstrap_local.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='0')) as docker, \
                 patch('builtins.print'):
                bootstrap_local.main()
            self.assertEqual(prompt.call_count, 1)
            self.assertEqual(docker.call_count, 2)
            backend = bootstrap_local._read_env(root / 'aw5_backend/.env')
            self.assertEqual(backend['AW5_DIFY_KNOWLEDGE_API_KEY'], 'fixture-backend-knowledge')
            self.assertEqual(backend['AW5_DISCORD_START_CHANNEL_ID'], '20')
            self.assertNotIn('DIFY', (root / 'discord_bot/.env').read_text())
            self.assertEqual((root / 'aw5_backend/.env').stat().st_mode & 0o777, 0o600)

    def test_legacy_value_is_not_a_fallback_for_empty_backend_entry(self):
        with TemporaryDirectory() as folder:
            root = self.workspace(folder)
            with (root / 'discord_bot/.env').open('a') as stream:
                stream.write('AW5_DIFY_KNOWLEDGE_API_KEY_1=fixture-legacy-do-not-use\n')
            with patch.object(bootstrap_local, 'ROOT', root), \
                 patch.object(bootstrap_local.getpass, 'getpass', return_value='  '), \
                 patch.object(bootstrap_local.subprocess, 'run') as docker:
                with self.assertRaises(SystemExit):
                    bootstrap_local.main()
            docker.assert_not_called()
            self.assertFalse((root / 'aw5_backend/.env').exists())

    def test_existing_backend_is_preserved_without_prompt_or_docker(self):
        with TemporaryDirectory() as folder:
            root = self.workspace(folder)
            (root / 'aw5_backend/.env').write_text('existing-fixture-configuration\n')
            with patch.object(bootstrap_local, 'ROOT', root), \
                 patch.object(bootstrap_local.getpass, 'getpass') as prompt, \
                 patch.object(bootstrap_local.subprocess, 'run') as docker:
                with self.assertRaises(SystemExit):
                    bootstrap_local.main()
            prompt.assert_not_called()
            docker.assert_not_called()
            self.assertEqual((root / 'aw5_backend/.env').read_text(), 'existing-fixture-configuration\n')
