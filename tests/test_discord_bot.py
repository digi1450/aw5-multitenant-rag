import asyncio
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from discord_bot.auth import AccessDenied, authorize_session, authorize_start, authorized_tenants
from discord_bot.bot import create_bot
from discord_bot.config import Config, Tenant, load_config
from discord_bot.dify import DifyAnswer, ask_dify
from discord_bot.store import Session, Store


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name) / "test.sqlite3")
        self.config = Config("fake-token", 10, 20, self.store.path, {
            1: Tenant(1, 101, "http://127.0.0.1/v1", "fake-key"),
            2: Tenant(2, 202, "http://127.0.0.1/v1", "fake-key"),
        })

    def test_membership_and_role_are_both_required(self):
        with self.assertRaises(AccessDenied):
            authorize_start(self.config, self.store, 10, 30, {101})
        self.store.set_membership(10, 30, 1, True)
        with self.assertRaises(AccessDenied):
            authorize_start(self.config, self.store, 10, 30, set())
        self.assertEqual(authorize_start(self.config, self.store, 10, 30, {101}).tenant_id, 1)
        self.store.set_membership(10, 30, 1, False)
        with self.assertRaises(AccessDenied):
            authorize_start(self.config, self.store, 10, 30, {101})

    def test_ambiguous_tenant_and_foreign_ticket_fail_closed(self):
        self.store.set_membership(10, 30, 1, True)
        self.store.set_membership(10, 30, 2, True)
        with self.assertRaises(AccessDenied):
            authorize_start(self.config, self.store, 10, 30, {101, 202})
        self.assertEqual(
            {tenant.tenant_id for tenant in authorized_tenants(self.config, self.store, 10, 30, {101, 202})},
            {1, 2},
        )
        self.store.create_session(Session(40, 10, 30, 1, None))
        with self.assertRaises(AccessDenied):
            authorize_session(self.config, self.store, 10, 31, {101}, 40)
        with self.assertRaises(AccessDenied):
            authorize_session(self.config, self.store, 11, 30, {101}, 40)
        self.assertEqual(authorize_session(self.config, self.store, 10, 30, {101}, 40)[0].tenant_id, 1)
        self.store.set_membership(10, 30, 1, False)
        with self.assertRaises(AccessDenied):
            authorize_session(self.config, self.store, 10, 30, {101}, 40)

    def test_start_panel_id_survives_store_reopen(self):
        self.assertIsNone(self.store.get_start_panel_id(10, 20))
        self.store.set_start_panel_id(10, 20, 50)
        reopened = Store(self.store.path)
        self.assertEqual(reopened.get_start_panel_id(10, 20), 50)
        self.assertIsNone(reopened.get_start_panel_id(10, 21))
        reopened.set_start_panel_id(10, 20, 51)
        self.assertEqual(self.store.get_start_panel_id(10, 20), 51)


class ConfigTests(unittest.TestCase):
    def test_insecure_remote_dify_url_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tenants.json"
            path.write_text(json.dumps({"tenants": [{
                "tenant_id": 1,
                "discord_role_id": 101,
                "dify_api_base_url": "http://example.com/v1",
                "dify_api_key_env": "AW5_DIFY_API_KEY_1",
            }]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config({
                    "AW5_DISCORD_BOT_TOKEN": "fake-token",
                    "AW5_DISCORD_GUILD_ID": "10",
                    "AW5_DISCORD_START_CHANNEL_ID": "20",
                    "AW5_TENANTS_FILE": str(path),
                    "AW5_DIFY_API_KEY_1": "fake-key",
                })


class DifyTests(unittest.TestCase):
    def test_chatflow_payload_preserves_thread_conversation(self):
        tenant = Tenant(1, 101, "http://127.0.0.1/v1", "fake-key")

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, *_):
                return b'{"answer":"Answer [1]","conversation_id":"conversation-1"}'

        def fake_open(request, timeout):
            self.assertEqual(timeout, 30.0)
            self.assertEqual(request.full_url, "http://127.0.0.1/v1/chat-messages")
            payload = json.loads(request.data)
            self.assertEqual(payload["conversation_id"], "conversation-0")
            self.assertEqual(payload["user"], "aw5:1:30:40")
            self.assertEqual(payload["response_mode"], "blocking")
            return Response()

        with patch("discord_bot.dify.urllib.request.urlopen", side_effect=fake_open):
            result = ask_dify(tenant, question="Question", user_key="aw5:1:30:40", conversation_id="conversation-0")
        self.assertEqual(result.text, "Answer [1]")
        self.assertEqual(result.conversation_id, "conversation-1")


class ButtonTests(unittest.TestCase):
    def test_start_view_dispatches_when_created_during_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config("fake-token", 10, 20, Path(directory) / "test.sqlite3", {
                1: Tenant(1, 101, "http://127.0.0.1:8080/v1", "fake-key"),
            })

            async def check():
                bot = create_bot(config)
                with patch("discord_bot.bot.app_commands.CommandTree.sync", new_callable=AsyncMock):
                    await bot.setup_hook()
                view = bot.start_view
                self.assertIsNotNone(view)
                self.assertTrue(view.is_persistent())
                task = view._dispatch_item(view.children[0], object())
                self.assertIsNotNone(task)
                task.cancel()

            asyncio.run(check())


class PlainMessageTests(unittest.TestCase):
    def test_only_ticket_owner_text_reaches_dify_and_reuses_conversation(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config("fake-token", 10, 20, Path(directory) / "test.sqlite3", {
                1: Tenant(1, 101, "http://127.0.0.1:8080/v1", "fake-key"),
            })

            async def check():
                bot = create_bot(config)
                self.assertTrue(bot.intents.message_content)
                bot.store.set_membership(10, 30, 1, True)
                bot.store.create_session(Session(40, 10, 30, 1, None))
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.parent_id = 20
                thread.type = discord.ChannelType.private_thread
                thread.send = AsyncMock()
                guild = MagicMock(spec=discord.Guild)
                guild.id = 10
                member = MagicMock(spec=discord.Member)
                member.id = 30
                member.roles = [MagicMock(id=101)]
                guild.fetch_member = AsyncMock(return_value=member)
                message = MagicMock(spec=discord.Message)
                message.guild = guild
                message.channel = thread
                message.author.id = 30
                message.author.bot = False
                message.webhook_id = None
                message.type = discord.MessageType.default
                message.content = "คำถามแรก"

                with patch("discord_bot.bot.ask_dify", side_effect=[
                    DifyAnswer("คำตอบแรก", "conversation-1"),
                    DifyAnswer("คำตอบสอง", "conversation-1"),
                ]) as dify:
                    await bot.on_message(message)
                    message.content = "คำถามสอง"
                    await bot.on_message(message)
                    self.assertEqual(dify.call_count, 2)
                    self.assertIsNone(dify.call_args_list[0].kwargs["conversation_id"])
                    self.assertEqual(dify.call_args_list[1].kwargs["conversation_id"], "conversation-1")
                    self.assertEqual(thread.send.await_count, 2)
                    self.assertEqual(thread.typing.call_count, 2)
                    message.author.id = 31
                    await bot.on_message(message)
                    message.author.id = 30
                    message.author.bot = True
                    await bot.on_message(message)
                    message.author.bot = False
                    member.roles = []
                    await bot.on_message(message)
                    self.assertEqual(dify.call_count, 2)
                    self.assertEqual(thread.send.await_count, 3)

            asyncio.run(check())


class ProjectChoiceTests(unittest.TestCase):
    def test_single_eligible_project_opens_ticket_without_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config("fake-token", 10, 20, Path(directory) / "test.sqlite3", {
                1: Tenant(1, 101, "http://127.0.0.1/v1", "fake-key", "Nature Footprint"),
                2: Tenant(2, 202, "http://127.0.0.1/v1", "fake-key", "Project B"),
            })

            async def check():
                bot = create_bot(config)
                bot.store.set_membership(10, 30, 1, True)
                bot.store.set_membership(10, 30, 2, True)
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
                interaction.user = MagicMock(spec=discord.Member)
                interaction.user.id = 30
                interaction.user.roles = [MagicMock(id=101)]
                interaction.response.defer = AsyncMock()
                interaction.followup.send = AsyncMock()

                await bot.start_ticket_handler(interaction)
                self.assertEqual(channel.create_thread.await_count, 1)
                self.assertEqual(bot.store.get_session(40).tenant_id, 1)
                self.assertIsNone(interaction.followup.send.await_args.kwargs.get("view"))

            asyncio.run(check())

    def test_project_button_rechecks_role_and_binds_ticket_to_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Config("fake-token", 10, 20, Path(directory) / "test.sqlite3", {
                1: Tenant(1, 101, "http://127.0.0.1/v1", "fake-key", "Nature Footprint"),
                2: Tenant(2, 202, "http://127.0.0.1/v1", "fake-key", "Project B"),
            })

            async def check():
                bot = create_bot(config)
                bot.store.set_membership(10, 30, 1, True)
                bot.store.set_membership(10, 30, 2, True)
                guild = MagicMock(spec=discord.Guild)
                guild.id = 10
                guild.get_role.side_effect = lambda role_id: MagicMock(name=f"Role {role_id}")
                member = MagicMock(spec=discord.Member)
                member.id = 30
                member.roles = [MagicMock(id=101), MagicMock(id=202)]
                guild.fetch_member = AsyncMock(return_value=member)
                channel = MagicMock(spec=discord.TextChannel)
                channel.guild = guild
                thread = MagicMock(spec=discord.Thread)
                thread.id = 40
                thread.mention = "<#40>"
                thread.add_user = AsyncMock()
                thread.send = AsyncMock()
                channel.create_thread = AsyncMock(return_value=thread)
                bot.get_channel = MagicMock(return_value=channel)

                def interaction():
                    value = MagicMock(spec=discord.Interaction)
                    value.guild = guild
                    value.guild_id = 10
                    value.channel_id = 20
                    value.user = member
                    value.response.defer = AsyncMock()
                    value.followup.send = AsyncMock()
                    return value

                start = interaction()
                await bot.start_ticket_handler(start)
                view = start.followup.send.await_args.kwargs["view"]
                self.assertEqual({button.tenant_id for button in view.children}, {1, 2})
                self.assertEqual(channel.create_thread.await_count, 0)

                member.roles = [MagicMock(id=202)]
                stale_choice = interaction()
                await view.choose(stale_choice, 1)
                self.assertEqual(channel.create_thread.await_count, 0)
                self.assertIn("สิทธิ์โปรเจกต์นี้เปลี่ยนไป", stale_choice.followup.send.await_args.args[0])

                member.roles = [MagicMock(id=101), MagicMock(id=202)]
                retry = interaction()
                await bot.start_ticket_handler(retry)
                retry_view = retry.followup.send.await_args.kwargs["view"]
                chosen = interaction()
                await next(button for button in retry_view.children if button.tenant_id == 2).callback(chosen)
                self.assertEqual(channel.create_thread.await_count, 1)
                self.assertTrue(channel.create_thread.await_args.kwargs["name"].startswith("aw5-p2-ticket-"))
                self.assertEqual(bot.store.get_session(40).tenant_id, 2)

            asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
