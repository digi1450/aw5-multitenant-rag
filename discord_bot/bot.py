"""Guild slash commands for the AW5 Discord demo."""

import asyncio
import logging
import re
import sqlite3
from collections.abc import Awaitable, Callable
from uuid import uuid4

import discord
from discord import app_commands

from .backend import BackendClient, BackendDenied, BackendRouteMissing, BackendUnavailable, Project
from .config import Config, load_config
from .store import Store


LOG = logging.getLogger(__name__)
START_BUTTON_ID = "aw5:start:v1"
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^\r\n]*)$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


def _ticket_thread(config: Config, guild_id: int | None, channel: object) -> bool:
    return (
        guild_id == config.guild_id
        and isinstance(channel, discord.Thread)
        and channel.type == discord.ChannelType.private_thread
        and channel.parent_id == config.start_channel_id
    )


def _split_plain(message: str, limit: int) -> list[str]:
    parts: list[str] = []
    while message:
        if len(message) <= limit:
            parts.append(message)
            break
        cut = message.rfind("\n", 0, limit + 1)
        if cut < limit // 2:
            cut = limit
        parts.append(message[:cut])
        message = message[cut:].lstrip("\n")
    return parts


def _split_code(header: str, marker: str, body: str, limit: int) -> list[str]:
    prefix = header + "\n"
    budget = limit - len(prefix) - len(marker) - 1
    if budget < 1:
        return _split_plain(prefix + body + marker, limit)
    parts: list[str] = []
    while body:
        cut = min(len(body), budget)
        if cut < len(body):
            newline = body.rfind("\n", 0, cut + 1)
            if newline >= max(1, cut // 2):
                cut = newline + 1
        piece, body = body[:cut], body[cut:]
        parts.append(prefix + piece + ("" if piece.endswith("\n") else "\n") + marker)
    return parts or [prefix + marker]


def _split_table(header: str, separator: str, rows: list[str], limit: int) -> list[str]:
    repeated_header = header.rstrip("\n") + "\n" + separator.rstrip("\n") + "\n"
    if len(repeated_header) >= limit:
        return _split_plain(repeated_header + "".join(rows), limit)
    parts: list[str] = []
    current = repeated_header
    for row in rows:
        if len(repeated_header) + len(row) > limit:
            if current != repeated_header:
                parts.append(current.rstrip("\n"))
            parts.extend(_split_plain(row, limit))
            current = repeated_header
            continue
        if len(current) + len(row) > limit:
            parts.append(current.rstrip("\n"))
            current = repeated_header
        current += row
    if current != repeated_header or not parts:
        parts.append(current.rstrip("\n"))
    return parts


def _chunks(message: str, limit: int = 1900) -> list[str]:
    """Keep fenced code and ordinary Markdown table headers intact across sends."""
    if not message:
        return []
    lines = message.splitlines(keepends=True)
    parts: list[str] = []
    plain: list[str] = []

    def flush_plain() -> None:
        if plain:
            parts.extend(_split_plain("".join(plain), limit))
            plain.clear()

    index = 0
    while index < len(lines):
        line = lines[index]
        opener = FENCE_RE.fullmatch(line.rstrip("\r\n"))
        if opener:
            flush_plain()
            marker = opener.group(1)
            header = line.rstrip("\r\n")
            index += 1
            body: list[str] = []
            while index < len(lines):
                candidate = lines[index].rstrip("\r\n").strip()
                if (candidate.startswith(marker[0] * len(marker))
                        and set(candidate) == {marker[0]}):
                    index += 1
                    break
                body.append(lines[index])
                index += 1
            parts.extend(_split_code(header, marker, "".join(body), limit))
            continue
        if (index + 1 < len(lines) and "|" in line
                and TABLE_SEPARATOR_RE.fullmatch(lines[index + 1].rstrip("\r\n"))):
            flush_plain()
            header, separator = line, lines[index + 1]
            index += 2
            rows: list[str] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(lines[index])
                index += 1
            parts.extend(_split_table(header, separator, rows, limit))
            continue
        plain.append(line)
        index += 1
    flush_plain()

    return [part for part in parts if part]


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
        self.backend = BackendClient(config)
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

    async def create_ticket(interaction: discord.Interaction, project: Project) -> None:
        try:
            channel = bot.get_channel(config.start_channel_id)
            if channel is None:
                channel = await bot.fetch_channel(config.start_channel_id)
            if not isinstance(channel, discord.TextChannel) or channel.guild.id != config.guild_id:
                raise RuntimeError("configured start channel is not a guild text channel")
            thread = await channel.create_thread(
                name=f"aw5-p{project.tenant_id}-ticket-{uuid4().hex[:8]}",
                type=discord.ChannelType.private_thread,
                invitable=False,
                auto_archive_duration=60,
            )
            try:
                await thread.add_user(interaction.user)
                await asyncio.to_thread(bot.backend.create_ticket, config.guild_id,
                                        interaction.user.id, thread.id, project.tenant_id)
            except Exception:
                try:
                    await thread.edit(archived=True)
                except discord.DiscordException:
                    LOG.exception("Could not archive failed ticket")
                raise
            await thread.send(
                f"เริ่ม session ของ {project.tenant_name} แล้ว "
                "พิมพ์คำถามได้เลยใน thread นี้ หรือใช้ `/ask`",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            await interaction.followup.send(f"สร้าง ticket แล้ว: {thread.mention}", ephemeral=True)
        except (discord.DiscordException, OSError, RuntimeError, sqlite3.Error,
                BackendDenied, BackendUnavailable):
            LOG.exception("Could not create ticket")
            await interaction.followup.send("สร้าง ticket ไม่สำเร็จ กรุณาตรวจสิทธิ์ของ bot", ephemeral=True)

    async def select_project(interaction: discord.Interaction, tenant_id: int) -> None:
        if interaction.guild_id != config.guild_id or interaction.channel_id != config.start_channel_id:
            await interaction.followup.send("กรุณากด Start ในห้อง #aw5-start ใหม่", ephemeral=True)
            return
        try:
            eligible = await asyncio.to_thread(bot.backend.eligible_projects,
                                               interaction.guild_id, interaction.user.id)
        except (BackendDenied, BackendUnavailable, OSError):
            LOG.exception("Could not recheck project access")
            await interaction.followup.send("ตรวจสิทธิ์โปรเจกต์ไม่สำเร็จ กรุณากด Start ใหม่", ephemeral=True)
            return
        project = next((item for item in eligible if item.tenant_id == tenant_id), None)
        if project is None:
            await interaction.followup.send("สิทธิ์โปรเจกต์นี้เปลี่ยนไป กรุณากด Start ใหม่", ephemeral=True)
            return
        await create_ticket(interaction, project)

    async def start_ticket(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        if interaction.guild_id != config.guild_id or interaction.channel_id != config.start_channel_id:
            await interaction.followup.send("ใช้ /start ในห้อง #aw5-start เท่านั้น", ephemeral=True)
            return
        try:
            eligible = await asyncio.to_thread(bot.backend.eligible_projects,
                                               interaction.guild_id, interaction.user.id)
        except (BackendDenied, BackendUnavailable, OSError):
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
        for project in eligible:
            choices.append((project.tenant_id, f"{project.tenant_name} ({project.tenant_id})"))
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
        except BackendDenied:
            await interaction.followup.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน", ephemeral=True)
        except BackendUnavailable as exc:
            LOG.warning("AW5 backend request failed: %s", exc)
            await interaction.followup.send("ระบบตอบกลับไม่สำเร็จ กรุณาลองใหม่ภายหลัง", ephemeral=True)
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
            files, tenant_id = await asyncio.to_thread(
                bot.backend.files, thread.id, interaction.guild_id, interaction.user.id
            )
            if not files:
                await interaction.followup.send("ไม่พบไฟล์ที่ติด tenant_id ของโปรเจกต์นี้", ephemeral=True)
                return
            lines = [f"ไฟล์ของโปรเจกต์ {tenant_id} ({len(files)} รายการ):"]
            for item in files:
                name = discord.utils.escape_markdown(item.name.replace("\n", " ").replace("\r", " "))
                lines.append(f"• {name}")
            for chunk in _chunks("\n".join(lines)):
                await interaction.followup.send(chunk, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
        except BackendDenied:
            await interaction.followup.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน", ephemeral=True)
        except BackendUnavailable as exc:
            LOG.warning("AW5 file inventory failed: %s", exc)
            await interaction.followup.send("ดึงรายการไฟล์ไม่สำเร็จ กรุณาลองใหม่ภายหลัง", ephemeral=True)
        except (discord.DiscordException, OSError, sqlite3.Error):
            LOG.exception("Could not list project files")
            await interaction.followup.send("ดึงรายการไฟล์ไม่สำเร็จ กรุณาติดต่อผู้ดูแล", ephemeral=True)

    @bot.tree.command(name="close", description="ปิด ticket ส่วนตัวนี้")
    async def close(interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        thread = interaction.channel
        if not _ticket_thread(config, interaction.guild_id, thread):
            await interaction.followup.send("ใช้ /close ใน private ticket ที่ bot สร้างเท่านั้น", ephemeral=True)
            return
        lock = bot.ticket_locks.setdefault(thread.id, asyncio.Lock())
        try:
            async with lock:
                if interaction.guild_id is None:
                    raise BackendDenied("Discord guild unavailable")
                await asyncio.to_thread(bot.backend.close_ticket, thread.id,
                                        interaction.guild_id, interaction.user.id)
                try:
                    await thread.edit(archived=True)
                except discord.DiscordException:
                    LOG.exception("Ticket closed in backend but thread archival failed")
                    await interaction.followup.send(
                        "ปิด ticket ในระบบแล้ว แต่ archive เธรดไม่สำเร็จ กรุณาติดต่อผู้ดูแล",
                        ephemeral=True,
                    )
                    return
            await interaction.followup.send("ปิด ticket แล้ว หากต้องการถามใหม่ให้กด Start", ephemeral=True)
        except BackendDenied:
            await interaction.followup.send("คุณไม่ใช่เจ้าของ ticket นี้", ephemeral=True)
        except BackendRouteMissing as exc:
            LOG.warning("AW5 backend close route is missing: %s", exc)
            await interaction.followup.send(
                "backend ที่กำลังรันยังไม่มีคำสั่ง /close กรุณาอัปเดตและเริ่ม backend ใหม่",
                ephemeral=True,
            )
        except BackendUnavailable as exc:
            LOG.warning("AW5 backend close failed: %s", exc)
            await interaction.followup.send("ปิด ticket ไม่สำเร็จ กรุณาลองใหม่", ephemeral=True)
        except (discord.DiscordException, OSError):
            LOG.exception("Could not close ticket")
            await interaction.followup.send("ปิด ticket ไม่สำเร็จ กรุณาติดต่อผู้ดูแล", ephemeral=True)

    async def answer_ticket(thread: discord.Thread, guild: discord.Guild | None, user_id: int, question: str) -> None:
        lock = bot.ticket_locks.setdefault(thread.id, asyncio.Lock())
        async with lock:
            if guild is None:
                raise BackendDenied("Discord guild unavailable")
            async with thread.typing():
                answer = await asyncio.to_thread(
                    bot.backend.ask, thread.id, guild.id, user_id, question,
                )
            for chunk in _chunks(answer):
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
        thread = message.channel
        try:
            if message.attachments:
                await thread.send(
                    "ระบบยังไม่รองรับการอ่านไฟล์แนบ กรุณาพิมพ์คำถามเป็นข้อความ"
                    + (" (จะตอบจากข้อความที่พิมพ์เท่านั้น)" if question else ""),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            if not question:
                return
            if len(question) > 2000:
                await thread.send("คำถามต้องมีความยาว 1–2000 ตัวอักษร")
                return
            await answer_ticket(thread, message.guild, message.author.id, question)
        except BackendDenied:
            await thread.send("ไม่มีสิทธิ์ใช้งาน ticket นี้หรือสมาชิกถูกเพิกถอน")
        except BackendUnavailable as exc:
            LOG.warning("AW5 backend request failed: %s", exc)
            await thread.send("ระบบตอบกลับไม่สำเร็จ กรุณาลองใหม่ภายหลัง")
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
