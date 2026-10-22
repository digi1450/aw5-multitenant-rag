"""Offline safety checks for fresh-install preparation; no network/Docker calls."""

import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "prepare_dify", Path(__file__).resolve().parents[1] / "scripts/prepare_dify.py"
)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class PrepareDifyTests(unittest.TestCase):
    def workspace(self, folder):
        root = Path(folder)
        pin = root / "deploy/dify"
        pin.mkdir(parents=True)
        (pin / "version.json").write_text(json.dumps({
            "repository": "https://example.invalid/upstream.git",
            "tag": "test-version", "commit": "fixture-commit", "compose_project": "aw5-dify",
        }))
        (pin / "compose.override.yml").write_text("services: {}\n")
        target = root / "vendor"
        (target / ".git").mkdir(parents=True)
        (target / "docker").mkdir()
        (target / "docker/.env.example").write_text("SECRET_KEY=old\nDB_PASSWORD=old\n# preserve comment\n")
        return root, target

    def invoke(self, root, target, results):
        with patch.object(PREPARE, "ROOT", root), \
                patch.object(PREPARE, "run", side_effect=results), \
                patch.object(PREPARE.subprocess, "run") as commands, \
                patch("sys.argv", ["prepare_dify.py", "--source-dir", str(target)]), \
                patch("builtins.print"):
            PREPARE.main()
            commands.assert_not_called()

    def test_fresh_configuration_and_independent_secrets(self):
        with TemporaryDirectory() as folder:
            root, target = self.workspace(folder)
            self.invoke(root, target, ["fixture-commit", ""])
            env = target / "docker/.env"
            values = dict(line.split("=", 1) for line in env.read_text().splitlines()
                          if line and not line.startswith("#"))
            self.assertNotEqual(values["SECRET_KEY"], "old")
            self.assertNotEqual(values["SECRET_KEY"], values["DB_PASSWORD"])
            self.assertEqual(values["WEAVIATE_API_KEY"], values["WEAVIATE_AUTHENTICATION_APIKEY_ALLOWED_KEYS"])
            self.assertEqual(values["COMPOSE_PROJECT_NAME"], "aw5-dify")
            self.assertEqual(env.stat().st_mode & 0o777, 0o600)
            self.assertEqual((target / "docker/docker-compose.override.yaml").read_text(), "services: {}\n")

    def test_existing_environment_is_never_overwritten(self):
        with TemporaryDirectory() as folder:
            root, target = self.workspace(folder)
            env = target / "docker/.env"
            env.write_text("existing-private-configuration\n")
            with self.assertRaises(SystemExit):
                self.invoke(root, target, ["fixture-commit", ""])
            self.assertEqual(env.read_text(), "existing-private-configuration\n")
            self.assertFalse((target / "docker/docker-compose.override.yaml").exists())

    def test_wrong_commit_or_dirty_source_is_rejected(self):
        for results in (["different-commit"], ["fixture-commit", " M docker/example.yml"]):
            with self.subTest(results=results), TemporaryDirectory() as folder:
                root, target = self.workspace(folder)
                with self.assertRaises(SystemExit):
                    self.invoke(root, target, results)
                self.assertFalse((target / "docker/.env").exists())


if __name__ == "__main__":
    unittest.main()
