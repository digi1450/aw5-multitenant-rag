"""AW5-owned project registry, tickets, and narrow Published Dify projection."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import psycopg
from psycopg.rows import dict_row


@dataclass(frozen=True)
class Project:
    tenant_id: int
    tenant_name: str
    guild_id: int
    discord_role_id: int
    dify_app_id: str
    dify_api_key_ciphertext: bytes
    status: str
    published_workflow_id: str | None
    last_sync_error: str | None
    synced_at: datetime | None


@dataclass(frozen=True)
class Ticket:
    thread_id: int
    guild_id: int
    discord_user_id: int
    tenant_id: int
    dify_conversation_id: str | None
    closed_at: datetime | None = None


def _project(row: dict | None) -> Project | None:
    if row is None:
        return None
    row = dict(row)
    row["dify_app_id"] = str(row["dify_app_id"])
    row["published_workflow_id"] = str(row["published_workflow_id"]) if row["published_workflow_id"] else None
    row["dify_api_key_ciphertext"] = bytes(row["dify_api_key_ciphertext"])
    return Project(**row)


class Registry:
    def __init__(self, database_url: str, dify_read_url: str):
        self.database_url = database_url
        self.dify_read_url = dify_read_url

    def initialize(self, schema: str) -> None:
        with psycopg.connect(self.database_url) as db:
            db.execute(schema)

    def register_project(self, *, name: str, guild_id: int, role_id: int,
                         app_id: UUID, encrypted_key: bytes) -> Project:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            row = db.execute("""
                INSERT INTO projects (tenant_name, guild_id, discord_role_id,
                                      dify_app_id, dify_api_key_ciphertext)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING tenant_id, tenant_name, guild_id, discord_role_id,
                          dify_app_id, dify_api_key_ciphertext,
                          status, published_workflow_id, last_sync_error, synced_at
            """, (name, guild_id, role_id, app_id, encrypted_key)).fetchone()
        return _project(row)

    def projects(self) -> list[Project]:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            rows = db.execute("""
                SELECT tenant_id, tenant_name, guild_id, discord_role_id,
                       dify_app_id, dify_api_key_ciphertext,
                       status, published_workflow_id, last_sync_error, synced_at
                FROM projects ORDER BY tenant_id
            """).fetchall()
        return [_project(row) for row in rows]

    def get_project(self, tenant_id: int) -> Project | None:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            row = db.execute("""
                SELECT tenant_id, tenant_name, guild_id, discord_role_id,
                       dify_app_id, dify_api_key_ciphertext,
                       status, published_workflow_id, last_sync_error, synced_at
                FROM projects WHERE tenant_id = %s
            """, (tenant_id,)).fetchone()
        return _project(row)

    def published_selection(self, app_id: str) -> tuple[str, set[str]] | None:
        # The reader can SELECT this view, never Dify's apps/workflows tables.
        with psycopg.connect(self.dify_read_url, row_factory=dict_row) as db:
            row = db.execute("""
                SELECT workflow_id, dataset_ids
                FROM aw5_published_retrieval_v1 WHERE app_id = %s
            """, (UUID(app_id),)).fetchone()
        if not row:
            return None
        values = row["dataset_ids"]
        if not isinstance(values, list) or not values:
            return None
        ids = {str(UUID(value)) for value in values}
        if len(ids) != len(values):
            return None
        return str(row["workflow_id"]), ids

    def activate_project(self, tenant_id: int, workflow_id: str, dataset_ids: set[str]) -> None:
        with psycopg.connect(self.database_url) as db:
            db.execute("DELETE FROM project_datasets WHERE tenant_id = %s", (tenant_id,))
            for dataset_id in sorted(dataset_ids):
                db.execute("INSERT INTO project_datasets (tenant_id, dataset_id) VALUES (%s, %s)",
                           (tenant_id, UUID(dataset_id)))
            db.execute("""
                UPDATE projects SET status = 'active', published_workflow_id = %s,
                    last_sync_error = NULL, synced_at = now() WHERE tenant_id = %s
            """, (UUID(workflow_id), tenant_id))

    def suspend_project(self, tenant_id: int, reason: str) -> None:
        with psycopg.connect(self.database_url) as db:
            db.execute("""
                UPDATE projects SET status = 'suspended', last_sync_error = %s,
                    synced_at = now() WHERE tenant_id = %s
            """, (reason[:200], tenant_id))

    def datasets(self, tenant_id: int) -> set[str]:
        with psycopg.connect(self.database_url) as db:
            rows = db.execute("SELECT dataset_id FROM project_datasets WHERE tenant_id = %s", (tenant_id,)).fetchall()
        return {str(row[0]) for row in rows}

    def create_ticket(self, ticket: Ticket) -> None:
        with psycopg.connect(self.database_url) as db:
            db.execute("""
                INSERT INTO tickets (thread_id, guild_id, discord_user_id, tenant_id)
                VALUES (%s, %s, %s, %s)
            """, (ticket.thread_id, ticket.guild_id, ticket.discord_user_id, ticket.tenant_id))

    def import_tickets(self, tickets: list[Ticket]) -> int:
        with psycopg.connect(self.database_url) as db:
            imported = 0
            for ticket in tickets:
                owner_project = db.execute(
                    "SELECT 1 FROM projects WHERE tenant_id = %s AND guild_id = %s",
                    (ticket.tenant_id, ticket.guild_id),
                ).fetchone()
                if owner_project is None:
                    raise ValueError("Legacy ticket project is not registered")
                result = db.execute("""
                    INSERT INTO tickets (thread_id, guild_id, discord_user_id,
                                         tenant_id, dify_conversation_id)
                    SELECT %s, %s, %s, p.tenant_id, %s
                    FROM projects AS p
                    WHERE p.tenant_id = %s AND p.guild_id = %s
                    ON CONFLICT (thread_id) DO NOTHING
                """, (ticket.thread_id, ticket.guild_id, ticket.discord_user_id,
                      ticket.dify_conversation_id, ticket.tenant_id, ticket.guild_id))
                imported += result.rowcount
            return imported

    def get_ticket(self, thread_id: int) -> Ticket | None:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            row = db.execute("""
                SELECT thread_id, guild_id, discord_user_id, tenant_id,
                       dify_conversation_id, closed_at
                FROM tickets WHERE thread_id = %s
            """, (thread_id,)).fetchone()
        return Ticket(**row) if row else None

    def close_ticket(self, thread_id: int, guild_id: int, user_id: int) -> bool:
        with psycopg.connect(self.database_url) as db:
            result = db.execute("""
                UPDATE tickets SET closed_at = now()
                WHERE thread_id = %s AND guild_id = %s AND discord_user_id = %s
                  AND closed_at IS NULL
            """, (thread_id, guild_id, user_id))
            return result.rowcount == 1

    def set_conversation(self, thread_id: int, conversation_id: str) -> bool:
        with psycopg.connect(self.database_url) as db:
            result = db.execute("""
                UPDATE tickets SET dify_conversation_id = %s
                WHERE thread_id = %s AND closed_at IS NULL
            """, (conversation_id, thread_id))
            return result.rowcount == 1
