"""Guild slash commands for the AW5 Discord demo."""

import asyncio
import logging
import sqlite3
from collections.abc import Awaitable, Callable
from uuid import uuid4

import discord
from discord import app_commands

from .auth import AccessDenied, authorize_session, authorized_tenants
from .config import Config, Tenant, load_config
from .dify import DifyError, ask_dify
from .knowledge import KnowledgeError, list_project_files
from .store import Session, Store


LOG = logging.getLogger(__name__)
START_BUTTON_ID = "aw5:start:v1"


async def _current_role_ids(guild: discord.Guild | None, user_id: int) -> set[int]:
    if guild is None:
        raise AccessDenied("Discord server identity is unavailable")
    try:
        member = await guild.fetch_member(user_id)
    except discord.NotFound as exc:
        raise AccessDenied("Discord member is unavailable") from exc
    return {role.id for role in member.roles}


def _ticket_thread(config: Config, guild_id: int | None, channel: object) -> bool:
    return (
        guild_id == config.guild_id
        and isinstance(channel, discord.Thread)
        and channel.type == discord.ChannelType.private_thread
        and channel.parent_id == config.start_channel_id
    )


def _project_label(guild: discord.Guild | None, tenant: Tenant) -> str:
    role = guild.get_role(tenant.discord_role_id) if guild else None
    return tenant.tenant_name or (role.name if role else f"Project {tenant.tenant_id}")


def _chunks(message: str, limit: int = 1900) -> list[str]:
    chunks: list[str] = []
    while message:
        if len(message) <= limit:
            chunks.append(message)
            break
        cut = message.rfind("\n", 0, limit + 1)
        if cut < limit // 2:
            cut = limit
        chunks.append(message[:cut])
        message = message[cut:].lstrip("\n")
    return chunks


class StartView(discord.ui.View):
    def __init__(self, start_ticket: Callable[[discord.Interaction], Awaitable[None]]):
        super().__init__(timeout=None)
        self.start_ticket = start_ticket

    @discord.ui.button(label="Start", style=discord.ButtonStyle.primary, custom_id=START_BUTTON_ID)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        LOG.info("Start button received in guild %s channel %s", interaction.guild_id, interaction.channel_id)
        await self.start_ticket(interaction)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ) -> None:
        LOG.error("Start button failed", exc_info=(type(error), error, error.__traceback__))
        try:
            if interaction.response.is_done():
                await interaction.followup.send("เปิด ticket ไม่สำเร็จ กรุณาลองใหม่", ephemeral=True)
            else:
                await interaction.response.send_message("เปิด ticket ไม่สำเร็จ กรุณาลองใหม่", ephemeral=True)
        except discord.DiscordException:
            LOG.exception("Could not report Start button failure")


class ProjectButton(discord.ui.Button):
    def __init__(self, tenant_id: int, label: str):
        super().__init__(label=label[:80], style=discord.ButtonStyle.primary)
        self.tenant_id = tenant_id

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, ProjectChoiceView):
            raise RuntimeError("Project selector is unavailable")
        await view.choose(interaction, self.tenant_id)


class ProjectChoiceView(discord.ui.View):
    def __init__(
        self,
        owner_user_id: int,
        choices: list[tuple[int, str]],
        on_select: Callable[[discord.Interaction, int], Awaitable[None]],
    ):
        super().__init__(timeout=180)
        self.owner_user_id = owner_user_id
        self.on_select = on_select
        self.selection_lock = asyncio.Lock()
        self.used = False
        for tenant_id, label in choices:
            self.add_item(ProjectButton(tenant_id, label))

    async def choose(self, interaction: discord.Interaction, tenant_id: int) -> None:
        if interaction.user.id != self.owner_user_id:
            await interaction.response.send_message("ปุ่มนี้ไม่ใช่ของคุณ", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        async with self.selection_lock:
            if self.used:
                await interaction.followup.send("เลือกโปรเจกต์ไปแล้ว กด Start ใหม่หากต้องการ ticket เพิ่ม", ephemeral=True)
                return
            self.used = True
        await self.on_select(interaction, tenant_id)

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ) -> None:
        LOG.error("Project selection failed", exc_info=(type(error), error, error.__traceback__))
        try:
            if interaction.response.is_done():
                await interaction.followup.send("เลือกโปรเจกต์ไม่สำเร็จ กรุณากด Start ใหม่", ephemeral=True)
            else:
                await interaction.response.send_message("เลือกโปรเจกต์ไม่สำเร็จ กรุณากด Start ใหม่", ephemeral=True)
        except discord.DiscordException:
            LOG.exception("Could not report project selection failure")


class AW5Bot(discord.Client):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.members = False
        intents.message_content = True
        super().__init__(intents=intents, allowed_mentions=discord.AllowedMentions.none())
        self.config = config
        self.store = Store(config.database_path)
        self.tree = app_commands.CommandTree(self)
        self.ticket_locks: dict[int, asyncio.Lock] = {}
        self.start_ticket_handler: Callable[[discord.Interaction], Awaitable[None]] | None = None
        self.start_view: StartView | None = None

    async def setup_hook(self) -> None:
        if self.start_ticket_handler is None:
            raise RuntimeError("Start handler has not been configured")
        self.start_view = StartView(self.start_ticket_handler)
        self.add_view(self.start_view)
        guild = discord.Object(id=self.config.guild_id)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        LOG.info("Synced AW5 commands for configured guild")


def create_bot(config: Config) -> AW5Bot:
    bot = AW5Bot(config)

    async def create_ticket(interaction: discord.Interaction, tenant: Tenant) -> None:
        try:
            channel = bot.get_channel(config.start_channel_id)
            if channel is None:
                channel = await bot.fetch_channel(config.start_channel_id)
            if not isinstance(channel, discord.TextChannel) or channel.guild.id != config.guild_id:
                raise RuntimeError("configured start channel is not a guild text channel")
            thread = await channel.create_thread(
                name=f"aw5-p{tenant.tenant_id}-ticket-{uuid4().hex[:8]}",
                type=discord.ChannelType.private_thread,
                invitable=False,
                auto_archive_duration=60,
            )
            try:
                await thread.add_user(interaction.user)
                bot.store.create_session(Session(thread.id, config.guild_id, interaction.user.id, tenant.tenant_id, None))
            except Exception:
                try:
                    await thread.edit(archived=True)
                except discord.DiscordException:
                    LOG.exception("Could not archive failed ticket")
                raise
            await thread.send(
                f"เริ่ม session ของ {_project_label(channel.guild, tenant)} แล้ว "
                "พิมพ์คำถามได้เลยใน thread นี้ หรือใช้ `/ask`",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            await interaction.followup.send(f"สร้าง ticket แล้ว: {thread.mention}", ephemeral=True)
        except (discord.DiscordException, OSError, RuntimeError, sqlite3.Error):
            LOG.exception("Could not create ticket")
            await interaction.followup.send("สร้าง ticket ไม่สำเร็จ กรุณาตรวจสิทธิ์ของ bot", ephemeral=True)

    async def select_project(interaction: discord.Interaction, tenant_id: int) -> None:
        if interaction.guild_id != config.guild_id or interaction.channel_id != config.start_channel_id:
            await interaction.followup.send("กรุณากด Start ในห้อง #aw5-start ใหม่", ephemeral=True)
            return
        try:
            role_ids = await _current_role_ids(interaction.guild, interaction.user.id)
            eligible = authorized_tenants(config, interaction.guild_id, role_ids)
        except (AccessDenied, discord.DiscordException, OSError, sqlite3.Error):
            LOG.exception("Could not recheck project access")
            await interaction.followup.send("ตรวจสิทธิ์โปรเจกต์ไม่สำเร็จ กรุณากด Start ใหม่", ephemeral=True)
            return
        tenant = next((item for item in eligible if item.tenant_id == tenant_id), None)
        if tenant is None:
            await interaction.followup.send("สิทธิ์โปรเจกต์นี้เปลี่ยนไป กรุณากด Start ใหม่", ephemeral=True)
            return
        await create_ticket(interaction, tenant)

    async def start_ticket(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        if interaction.guild_id != config.guild_id or interaction.channel_id != config.start_channel_id:
            await interaction.followup.send("ใช้ /start ในห้อง #aw5-start เท่านั้น", ephemeral=True)
            return
        try:
            role_ids = await _current_role_ids(interaction.guild, interaction.user.id)
            eligible = authorized_tenants(config, interaction.guild_id, role_ids)
        except (AccessDenied, discord.DiscordException, OSError):
            await interaction.followup.send("ไม่พบสิทธิ์สมาชิกโปรเจกต์ที่ใช้งานได้", ephemeral=True)
            return
        if not eligible:
            await interaction.followup.send("ไม่พบสิทธิ์สมาชิกโปรเจกต์ที่ใช้งานได้", ephemeral=True)
            return
        if len(eligible) == 1:
            await create_ticket(interaction, eligible[0])
            return
        if len(eligible) > 25:
            await interaction.followup.send("มีโปรเจกต์มากเกินจำนวนปุ่มที่รองรับ กรุณาติดต่อผู้ดูแล", ephemeral=True)
            return
        choices = []
        for tenant in eligible:
            choices.append((tenant.tenant_id, f"{_project_label(interaction.guild, tenant)} ({tenant.tenant_id})"))
        await interaction.followup.send(
            "เลือกโปรเจกต์ที่ต้องการถาม:",
            view=ProjectChoiceView(interaction.user.id, choices, select_project),
            ephemeral=True,
        )

    @bot.tree.command(name="start", description="เปิด ticket ส่วนตัวสำหรับถาม AW5")
    async def start(interaction: discord.Interaction) -> None:
        await start_ticket(interaction)

    bot.start_ticket_handler = start_ticket
    panel_lock = asyncio.Lock()

    @bot.event
    async def on_interaction(interaction: discord.Interaction) -> None:
        if interaction.type == discord.InteractionType.component:
            LOG.info(
                "Component interaction received in guild %s channel %s",
                interaction.guild_id,
                interaction.channel_id,
            )

    @bot.event
    async def on_ready() -> None:
        async with panel_lock:
            try:
                if bot.start_view is None:
                    raise RuntimeError("Start button view is unavailable")
                channel = bot.get_channel(config.start_channel_id)
                if channel is None:
                    channel = await bot.fetch_channel(config.start_channel_id)
                if not isinstance(channel, discord.TextChannel) or channel.guild.id != config.guild_id:
                    raise RuntimeError("configured start channel is not a guild text channel")
                panel_id = bot.store.get_start_panel_id(config.guild_id, config.start_channel_id)
                if panel_id is not None:
                    try:
                        message = await channel.fetch_message(panel_id)
                    except discord.NotFound:
                        pass
                    else:
                        has_button = any(
                            getattr(component, "custom_id", None) == START_BUTTON_ID
                            for row in message.components for component in row.children
                        )
                        if message.author.id == bot.user.id and has_button:
                            LOG.info("Start button is available in configured channel")
                            return
                message = await channel.send(
                    "กด **Start** เพื่อเปิด private ticket สำหรับถาม AW5",
                    view=bot.start_view,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
                bot.store.set_start_panel_id(config.guild_id, config.start_channel_id, message.id)
                LOG.info("Posted Start button in configured channel")
            except (discord.DiscordException, OSError, RuntimeError, sqlite3.Error):
                LOG.exception("Could not ensure Start button")

    @bot.tree.command(name="ask", description="ถาม AW5 ภายใน ticket ส่วนตัว")
    @app_commands.describe(question="คำถามเกี่ยวกับเอกสารของโปรเจกต์")
    async def ask(interaction: discord.Interaction, question: str) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        thread = interaction.channel
        if not _ticket_thread(config, interaction.guild_id, thread):
            await interaction.followup.send("ใช้ /ask ใน private ticket ที่ bot สร้างเท่านั้น", ephemeral=True)
            return
        question = question.strip()
        if not question or len(question) > 2000:
            await interaction.followup.send("คำถามต้องมีความยาว 1–2000 ตัวอักษร", ephemeral=True)
            return
        try:
            await answer_ticket(thread, interaction.guild, interaction.user.id, question)
            await interaction.followup.send("ส่งคำตอบใน ticket แล้ว", ephemeral=True)
        except AccessDenied:
            await interaction.followup.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน", ephemeral=True)
        except DifyError as exc:
            LOG.warning("Dify request failed: %s", exc)
            await interaction.followup.send("Dify ตอบกลับไม่สำเร็จ กรุณาลองใหม่ภายหลัง", ephemeral=True)
        except (discord.DiscordException, OSError, sqlite3.Error):
            LOG.exception("Could not deliver Dify answer")
            await interaction.followup.send("ส่งคำตอบไม่สำเร็จ กรุณาติดต่อผู้ดูแล", ephemeral=True)

    @bot.tree.command(name="list", description="ดูรายการไฟล์ของโปรเจกต์ใน ticket ส่วนตัว")
    async def list_files(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        thread = interaction.channel
        if not _ticket_thread(config, interaction.guild_id, thread):
            await interaction.followup.send("ใช้ /list ใน private ticket ที่ bot สร้างเท่านั้น", ephemeral=True)
            return
        try:
            role_ids = await _current_role_ids(interaction.guild, interaction.user.id)
            tenant, _ = authorize_session(
                config, bot.store, interaction.guild_id, interaction.user.id, role_ids, thread.id
            )
            files = await asyncio.to_thread(list_project_files, tenant)
            if not files:
                await interaction.followup.send("ไม่พบไฟล์ที่ติด tenant_id ของโปรเจกต์นี้", ephemeral=True)
                return
            lines = [f"ไฟล์ที่ติด tenant_id = {tenant.tenant_id} ({len(files)} รายการ):"]
            for item in files:
                name = discord.utils.escape_markdown(item.name.replace("\n", " ").replace("\r", " "))
                dataset = discord.utils.escape_markdown(item.dataset_name.replace("\n", " ").replace("\r", " "))
                label = {"available": "พร้อมใช้งาน", "disabled": "ปิดใช้งาน", "archived": "เก็บถาวร", "indexing": "ยังไม่พร้อม"}[item.status]
                lines.append(f"• {name} — {dataset} ({label})")
            for chunk in _chunks("\n".join(lines)):
                await interaction.followup.send(chunk, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
        except AccessDenied:
            await interaction.followup.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน", ephemeral=True)
        except KnowledgeError as exc:
            LOG.warning("Knowledge inventory failed: %s", exc)
            await interaction.followup.send("ดึงรายการไฟล์ไม่สำเร็จ กรุณาตรวจการตั้งค่า Knowledge API", ephemeral=True)
        except (discord.DiscordException, OSError, sqlite3.Error):
            LOG.exception("Could not list project files")
            await interaction.followup.send("ดึงรายการไฟล์ไม่สำเร็จ กรุณาติดต่อผู้ดูแล", ephemeral=True)

    async def answer_ticket(thread: discord.Thread, guild: discord.Guild | None, user_id: int, question: str) -> None:
        lock = bot.ticket_locks.setdefault(thread.id, asyncio.Lock())
        async with lock:
            role_ids = await _current_role_ids(guild, user_id)
            tenant, session = authorize_session(config, bot.store, guild.id, user_id, role_ids, thread.id)
            user_key = f"aw5:{tenant.tenant_id}:{user_id}:{thread.id}"
            async with thread.typing():
                result = await asyncio.to_thread(
                    ask_dify,
                    tenant,
                    question=question,
                    user_key=user_key,
                    conversation_id=session.dify_conversation_id,
                )
            bot.store.set_conversation(thread.id, result.conversation_id)
            for chunk in _chunks(result.text):
                await thread.send(chunk, allowed_mentions=discord.AllowedMentions.none())

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if (
            message.author.bot
            or message.webhook_id is not None
            or message.type != discord.MessageType.default
            or not _ticket_thread(config, message.guild.id if message.guild else None, message.channel)
        ):
            return
        question = message.content.strip()
        if not question:
            return
        thread = message.channel
        try:
            session = bot.store.get_session(thread.id)
            if session is None or session.discord_user_id != message.author.id:
                return
            if len(question) > 2000:
                await thread.send("คำถามต้องมีความยาว 1–2000 ตัวอักษร")
                return
            await answer_ticket(thread, message.guild, message.author.id, question)
        except AccessDenied:
            await thread.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน")
        except DifyError as exc:
            LOG.warning("Dify request failed: %s", exc)
            await thread.send("Dify ตอบกลับไม่สำเร็จ กรุณาลองใหม่ภายหลัง")
        except (discord.DiscordException, OSError, sqlite3.Error):
            LOG.exception("Could not deliver Dify answer")
            try:
                await thread.send("ส่งคำตอบไม่สำเร็จ กรุณาติดต่อผู้ดูแล")
            except discord.DiscordException:
                LOG.exception("Could not report ticket error")

    return bot


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = load_config()
    create_bot(config).run(config.discord_token)


if __name__ == "__main__":
    main()
