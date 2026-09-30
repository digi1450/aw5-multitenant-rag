import asyncio
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from discord_bot.backend import BackendClient, BackendDenied, BackendRouteMissing, BackendUnavailable, Project
from discord_bot.bot import _chunks, create_bot
from discord_bot.config import Config, load_config
from discord_bot.store import Store


def config(path: Path) -> Config:
    return Config("fake-discord-token", 10, 20, path, "http://127.0.0.1:8765", "fake-backend-token")


class ConfigTests(unittest.TestCase):
    def test_config_needs_backend_not_tenant_json(self):
        value = load_config({
            "AW5_DISCORD_BOT_TOKEN": "fake-discord-token", "AW5_DISCORD_GUILD_ID": "10",
            "AW5_DISCORD_START_CHANNEL_ID": "20", "AW5_BACKEND_API_URL": "http://127.0.0.1:8765",
            "AW5_BACKEND_BOT_TOKEN": "fake-backend-token",
        })
        self.assertEqual(value.backend_api_url, "http://127.0.0.1:8765")
        self.assertFalse(hasattr(value, "tenants"))

    def test_remote_plain_http_rejected(self):
        with self.assertRaises(ValueError):
            load_config({
                "AW5_DISCORD_BOT_TOKEN": "fake", "AW5_DISCORD_GUILD_ID": "10",
                "AW5_DISCORD_START_CHANNEL_ID": "20", "AW5_BACKEND_API_URL": "http://example.com",
                "AW5_BACKEND_BOT_TOKEN": "fake",
            })

    def test_docker_api_service_is_allowed(self):
        value = load_config({
            "AW5_DISCORD_BOT_TOKEN": "fake", "AW5_DISCORD_GUILD_ID": "10",
            "AW5_DISCORD_START_CHANNEL_ID": "20", "AW5_BACKEND_API_URL": "http://aw5_api:8765",
            "AW5_BACKEND_BOT_TOKEN": "fake",
        })
        self.assertEqual(value.backend_api_url, "http://aw5_api:8765")


class BackendClientTests(unittest.TestCase):
    def test_missing_route_is_not_reported_as_denied(self):
        with tempfile.TemporaryDirectory() as directory:
            client = BackendClient(config(Path(directory) / "state.sqlite3"))
            for status, expected in ((404, BackendRouteMissing), (403, BackendDenied)):
                error = HTTPError("", status, "", {}, None)
                try:
                    with patch.object(client.opener, "open", side_effect=error):
                        with self.assertRaises(expected):
                            client.close_ticket(40, 10, 30)
                finally:
                    error.close()

    def test_eligible_projects_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            client = BackendClient(config(Path(directory) / "state.sqlite3"))
            with patch.object(client, "_request", return_value={"projects": [
                {"tenant_id": 1, "tenant_name": "Nature Footprint"},
                {"tenant_id": 2, "tenant_name": "Project B"},
            ]}) as request:
                self.assertEqual([item.tenant_id for item in client.eligible_projects(10, 30)], [1, 2])
            self.assertEqual(request.call_args.kwargs["query"], {"guild_id": 10, "user_id": 30})

    def test_close_ticket_requires_boolean_result(self):
        with tempfile.TemporaryDirectory() as directory:
            client = BackendClient(config(Path(directory) / "state.sqlite3"))
            with patch.object(client, "_request", return_value={"closed": True}) as request:
                self.assertTrue(client.close_ticket(40, 10, 30))
                request.assert_called_once_with(
                    "POST", "/v1/tickets/40/close", data={"guild_id": 10, "user_id": 30},
                )
            with patch.object(client, "_request", return_value={"closed": "true"}):
                with self.assertRaises(BackendUnavailable):
                    client.close_ticket(40, 10, 30)


class StoreTests(unittest.TestCase):
    def test_start_panel_id_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory) / "state.sqlite3")
            store.set_start_panel_id(10, 20, 50)
            self.assertEqual(Store(store.path).get_start_panel_id(10, 20), 50)


class ChunkTests(unittest.TestCase):
    def test_long_code_block_reopens_with_language_and_stays_within_limit(self):
        chunks = _chunks("```python\n" + "print('hello')\n" * 50 + "```", limit=100)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 100 for chunk in chunks))
        self.assertTrue(all(chunk.startswith("```python\n") and chunk.endswith("\n```")
                            for chunk in chunks))

    def test_long_table_repeats_header_and_separator(self):
        header = "| File | Status |\n| --- | --- |\n"
        chunks = _chunks(header + "| SDS | available |\n" * 30, limit=110)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.startswith(header) and len(chunk) <= 110 for chunk in chunks))

    def test_oversized_code_line_and_table_row_keep_size_bound(self):
        message = "```text\n" + "x" * 500 + "\n```\n\n| A | B |\n| --- | --- |\n| " + "y" * 500 + " |"
        self.assertTrue(all(len(chunk) <= 100 for chunk in _chunks(message, limit=100)))


class BotTests(unittest.TestCase):
    def test_single_project_start_registers_ticket_with_backend(self):
        with tempfile.TemporaryDirectory() as directory:
            bot = create_bot(config(Path(directory) / "state.sqlite3"))

            async def check():
                guild = MagicMock(spec=discord.Guild)
                guild.id = 10
                channel = MagicMock(spec=discord.TextChannel)
                channel.guild = guild
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.mention = "<#40>"
                thread.add_user = AsyncMock()
                thread.send = AsyncMock()
                channel.create_thread = AsyncMock(return_value=thread)
                bot.get_channel = MagicMock(return_value=channel)
                interaction = MagicMock(spec=discord.Interaction)
                interaction.guild = guild
                interaction.guild_id = 10
                interaction.channel_id = 20
                interaction.user.id = 30
                interaction.response.defer = AsyncMock()
                interaction.followup.send = AsyncMock()
                with patch.object(bot.backend, "eligible_projects", return_value=[Project(1, "Nature Footprint")]), \
                        patch.object(bot.backend, "create_ticket") as register:
                    await bot.tree.get_command("start").callback(interaction)
                register.assert_called_once_with(10, 30, 40, 1)
                thread.add_user.assert_awaited_once()
                self.assertIn("Nature Footprint", thread.send.await_args.args[0])

            asyncio.run(check())

    def test_plain_text_uses_backend_and_denies_revoked_user(self):
        with tempfile.TemporaryDirectory() as directory:
            bot = create_bot(config(Path(directory) / "state.sqlite3"))

            async def check():
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.parent_id = 20
                thread.type = discord.ChannelType.private_thread
                thread.send = AsyncMock()
                guild = MagicMock(spec=discord.Guild)
                guild.id = 10
                message = MagicMock(spec=discord.Message)
                message.guild = guild
                message.channel = thread
                message.author.id = 30
                message.author.bot = False
                message.webhook_id = None
                message.type = discord.MessageType.default
                message.content = "คำถาม"
                message.attachments = []
                with patch.object(bot.backend, "ask", return_value="คำตอบ") as ask:
                    await bot.on_message(message)
                ask.assert_called_once_with(40, 10, 30, "คำถาม")
                self.assertEqual(thread.send.await_args.args[0], "คำตอบ")
                with patch.object(bot.backend, "ask", side_effect=BackendDenied):
                    await bot.on_message(message)
                self.assertIn("ไม่มีสิทธิ์", thread.send.await_args.args[0])

            asyncio.run(check())

    def test_attachment_only_warns_and_text_plus_attachment_uses_text(self):
        with tempfile.TemporaryDirectory() as directory:
            bot = create_bot(config(Path(directory) / "state.sqlite3"))

            async def check():
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.parent_id = 20
                thread.type = discord.ChannelType.private_thread
                thread.send = AsyncMock()
                guild = MagicMock(spec=discord.Guild)
                guild.id = 10
                message = MagicMock(spec=discord.Message)
                message.guild = guild
                message.channel = thread
                message.author.id = 30
                message.author.bot = False
                message.webhook_id = None
                message.type = discord.MessageType.default
                message.attachments = [object()]
                with patch.object(bot.backend, "ask", return_value="Answer") as ask:
                    message.content = ""
                    await bot.on_message(message)
                    ask.assert_not_called()
                    self.assertIn("ไม่รองรับการอ่านไฟล์แนบ", thread.send.await_args.args[0])
                    message.content = "What is this?"
                    await bot.on_message(message)
                    ask.assert_called_once_with(40, 10, 30, "What is this?")
                    self.assertIn("ข้อความที่พิมพ์เท่านั้น", thread.send.await_args_list[-2].args[0])
            asyncio.run(check())

    def test_close_archives_owners_ticket_and_rejects_other_user(self):
        with tempfile.TemporaryDirectory() as directory:
            bot = create_bot(config(Path(directory) / "state.sqlite3"))

            async def check():
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.parent_id = 20
                thread.type = discord.ChannelType.private_thread
                thread.edit = AsyncMock()
                interaction = MagicMock(spec=discord.Interaction)
                interaction.channel = thread
                interaction.guild_id = 10
                interaction.user.id = 30
                interaction.response.defer = AsyncMock()
                interaction.followup.send = AsyncMock()
                with patch.object(bot.backend, "close_ticket", return_value=True) as close:
                    await bot.tree.get_command("close").callback(interaction)
                    close.assert_called_once_with(40, 10, 30)
                    thread.edit.assert_awaited_once_with(archived=True)
                thread.edit.reset_mock()
                with patch.object(bot.backend, "close_ticket", side_effect=BackendDenied):
                    await bot.tree.get_command("close").callback(interaction)
                    thread.edit.assert_not_awaited()
                    self.assertIn("ไม่ใช่เจ้าของ", interaction.followup.send.await_args.args[0])
                with patch.object(bot.backend, "close_ticket", side_effect=BackendRouteMissing):
                    await bot.tree.get_command("close").callback(interaction)
                    thread.edit.assert_not_awaited()
                    self.assertIn("backend", interaction.followup.send.await_args.args[0])
            asyncio.run(check())
