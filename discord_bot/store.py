"""Backend-owned project membership and ticket state."""

from dataclasses import dataclass
from contextlib import closing
from pathlib import Path
import sqlite3


@dataclass(frozen=True)
class Session:
    thread_id: int
    guild_id: int
    discord_user_id: int
    tenant_id: int
    dify_conversation_id: str | None


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def _initialize(self) -> None:
        with closing(self._connect()) as db, db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS memberships (
                    guild_id INTEGER NOT NULL,
                    discord_user_id INTEGER NOT NULL,
                    tenant_id INTEGER NOT NULL,
                    active INTEGER NOT NULL CHECK (active IN (0, 1)),
                    PRIMARY KEY (guild_id, discord_user_id, tenant_id)
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    thread_id INTEGER PRIMARY KEY,
                    guild_id INTEGER NOT NULL,
                    discord_user_id INTEGER NOT NULL,
                    tenant_id INTEGER NOT NULL,
                    dify_conversation_id TEXT
                );
                CREATE TABLE IF NOT EXISTS start_panels (
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    PRIMARY KEY (guild_id, channel_id)
                );
            """)

    def set_membership(self, guild_id: int, user_id: int, tenant_id: int, active: bool) -> None:
        with closing(self._connect()) as db, db:
            db.execute("""
                INSERT INTO memberships (guild_id, discord_user_id, tenant_id, active)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (guild_id, discord_user_id, tenant_id)
                DO UPDATE SET active = excluded.active
            """, (guild_id, user_id, tenant_id, int(active)))

    def active_tenants(self, guild_id: int, user_id: int) -> list[int]:
        with closing(self._connect()) as db, db:
            rows = db.execute("""
                SELECT tenant_id FROM memberships
                WHERE guild_id = ? AND discord_user_id = ? AND active = 1
            """, (guild_id, user_id)).fetchall()
        return [int(row["tenant_id"]) for row in rows]

    def create_session(self, session: Session) -> None:
        with closing(self._connect()) as db, db:
            db.execute("""
                INSERT INTO sessions (thread_id, guild_id, discord_user_id, tenant_id)
                VALUES (?, ?, ?, ?)
            """, (session.thread_id, session.guild_id, session.discord_user_id, session.tenant_id))

    def get_session(self, thread_id: int) -> Session | None:
        with closing(self._connect()) as db, db:
            row = db.execute("SELECT * FROM sessions WHERE thread_id = ?", (thread_id,)).fetchone()
        if row is None:
            return None
        return Session(**dict(row))

    def set_conversation(self, thread_id: int, conversation_id: str) -> None:
        with closing(self._connect()) as db, db:
            db.execute("UPDATE sessions SET dify_conversation_id = ? WHERE thread_id = ?", (conversation_id, thread_id))

    def get_start_panel_id(self, guild_id: int, channel_id: int) -> int | None:
        with closing(self._connect()) as db, db:
            row = db.execute("""
                SELECT message_id FROM start_panels WHERE guild_id = ? AND channel_id = ?
            """, (guild_id, channel_id)).fetchone()
        return int(row["message_id"]) if row else None

    def set_start_panel_id(self, guild_id: int, channel_id: int, message_id: int) -> None:
        with closing(self._connect()) as db, db:
            db.execute("""
                INSERT INTO start_panels (guild_id, channel_id, message_id)
                VALUES (?, ?, ?)
                ON CONFLICT (guild_id, channel_id)
                DO UPDATE SET message_id = excluded.message_id
            """, (guild_id, channel_id, message_id))
