"""AW5-owned project registry, tickets, and narrow Published Dify projection."""

from dataclasses import dataclass
import hashlib
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
                         app_id: UUID, encrypted_key: bytes, tenant_id: int,
                         enrollment_request: str | None = None) -> Project:
        if type(tenant_id) is not int or not 0 < tenant_id <= 2**63 - 1:
            raise ValueError("Explicit positive AW5 tenant ID required")
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtext('aw5-project-enrollment'))")
            reserved = db.execute("SELECT request_id FROM onboarding_requests WHERE tenant_id=%s OR app_id=%s", (tenant_id, app_id)).fetchone()
            if reserved and (enrollment_request is None or str(reserved["request_id"]) != enrollment_request):
                raise psycopg.errors.UniqueViolation("Enrollment reserved")
            row = db.execute("""
                INSERT INTO projects (tenant_id, tenant_name, guild_id, discord_role_id,
                                      dify_app_id, dify_api_key_ciphertext)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING tenant_id, tenant_name, guild_id, discord_role_id,
                          dify_app_id, dify_api_key_ciphertext,
                          status, published_workflow_id, last_sync_error, synced_at
            """, (tenant_id, name, guild_id, role_id, app_id, encrypted_key)).fetchone()
            if enrollment_request:
                db.execute("UPDATE onboarding_requests SET state='completed',role_id=%s,updated_at=now() WHERE request_id=%s",
                           (role_id, UUID(enrollment_request)))
        return _project(row)

    def delete_project(self, tenant_id, guild_id, confirmation_name, app_id, role_id):
        """Remove AW5-owned bindings/history only, atomically and with stale checks."""
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtext('aw5-project-enrollment'))")
            row = db.execute("SELECT * FROM projects WHERE tenant_id=%s FOR UPDATE", (tenant_id,)).fetchone()
            if row is None:
                raise ValueError('Unknown project')
            if (row['guild_id'], row['tenant_name'], str(row['dify_app_id']), row['discord_role_id']) != (
                    guild_id, confirmation_name, app_id, role_id):
                raise ValueError('Project confirmation changed; refresh first')
            pending = db.execute("""SELECT 1 FROM project_role_changes WHERE tenant_id=%s AND state<>'completed'
                                    UNION ALL SELECT 1 FROM onboarding_requests WHERE tenant_id=%s AND state<>'completed'
                                    LIMIT 1""", (tenant_id, tenant_id)).fetchone()
            if pending:
                raise psycopg.errors.ObjectInUse('Unresolved provisioning operation')
            tickets = db.execute("DELETE FROM tickets WHERE tenant_id=%s", (tenant_id,)).rowcount
            db.execute("DELETE FROM project_datasets WHERE tenant_id=%s", (tenant_id,))
            db.execute("DELETE FROM project_role_changes WHERE tenant_id=%s", (tenant_id,))
            db.execute("DELETE FROM onboarding_requests WHERE tenant_id=%s", (tenant_id,))
            db.execute("DELETE FROM projects WHERE tenant_id=%s", (tenant_id,))
        return {'deleted': True, 'tenant_id': str(tenant_id), 'deleted_tickets': tickets}

    def get_enrollment(self, request_id: str, actor_id: int, fingerprint: str) -> dict | None:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            row = db.execute("SELECT * FROM onboarding_requests WHERE request_id=%s", (UUID(request_id),)).fetchone()
        if row and (row["actor_id"] != actor_id or row["fingerprint"] != fingerprint):
            raise ValueError("Enrollment request changed")
        return dict(row) if row else None

    def begin_role_change(self, request_id, tenant_id, actor_id, fingerprint, old_role_id):
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtext('aw5-project-enrollment'))")
            previous = db.execute("SELECT * FROM project_role_changes WHERE request_id=%s",
                                  (UUID(request_id),)).fetchone()
            if previous:
                if (previous['actor_id'], previous['tenant_id'], previous['fingerprint']) != (actor_id, tenant_id, fingerprint):
                    raise ValueError('Role-change request changed')
                return dict(previous)
            current = db.execute("SELECT discord_role_id FROM projects WHERE tenant_id=%s FOR UPDATE",
                                 (tenant_id,)).fetchone()
            if not current or current['discord_role_id'] != old_role_id:
                raise ValueError('Project role changed; refresh first')
            db.execute("""INSERT INTO project_role_changes
                       (request_id,tenant_id,actor_id,fingerprint,old_role_id,state)
                       VALUES (%s,%s,%s,%s,%s,'in_progress')""",
                       (UUID(request_id), tenant_id, actor_id, fingerprint, old_role_id))
        return None

    def fail_role_change(self, request_id, role_id):
        with psycopg.connect(self.database_url) as db:
            db.execute("UPDATE project_role_changes SET state='needs_attention',role_id=%s WHERE request_id=%s AND state='in_progress'",
                       (role_id, UUID(request_id)))

    def complete_role_change(self, request_id, role_id):
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtext('aw5-project-enrollment'))")
            change = db.execute("SELECT * FROM project_role_changes WHERE request_id=%s FOR UPDATE",
                                (UUID(request_id),)).fetchone()
            if not change or change['state'] != 'in_progress':
                raise ValueError('Role change is not pending')
            row = db.execute("""UPDATE projects SET discord_role_id=%s
                             WHERE tenant_id=%s AND discord_role_id=%s RETURNING *""",
                             (role_id, change['tenant_id'], change['old_role_id'])).fetchone()
            if row is None:
                raise ValueError('Project role changed; refresh first')
            db.execute("UPDATE project_role_changes SET state='completed',role_id=%s WHERE request_id=%s",
                       (role_id, UUID(request_id)))
        return _project({key: row[key] for key in Project.__dataclass_fields__})

    def verify_app_key(self, app_id: str, key: str) -> bool:
        """A separate restricted projection exposes digests, never API tokens."""
        with psycopg.connect(self.dify_read_url) as db:
            row = db.execute("SELECT EXISTS (SELECT 1 FROM aw5_app_key_bindings_v1 WHERE app_id = %s AND token_sha256 = %s)",
                             (UUID(app_id), hashlib.sha256(key.encode()).hexdigest())).fetchone()
        return bool(row[0])

    def resolve_app_key(self, key: str) -> str:
        """Resolve exactly one app using the existing digest-only projection."""
        if not isinstance(key, str) or not 1 <= len(key.strip()) <= 512:
            raise ValueError("Invalid Dify app key")
        with psycopg.connect(self.dify_read_url) as db:
            rows = db.execute(
                "SELECT DISTINCT app_id FROM aw5_app_key_bindings_v1 "
                "WHERE token_sha256 = %s LIMIT 2",
                (hashlib.sha256(key.strip().encode()).hexdigest(),),
            ).fetchall()
        if len(rows) != 1 or rows[0][0] is None:
            raise ValueError("Dify app key must resolve to exactly one app")
        return str(UUID(str(rows[0][0])))

    def begin_enrollment(self, request_id: str, tenant_id: int, app_id: str,
                         actor_id: int, fingerprint: str) -> dict | None:
        with psycopg.connect(self.database_url, row_factory=dict_row) as db:
            db.execute("SELECT pg_advisory_xact_lock(hashtext('aw5-project-enrollment'))")
            previous = db.execute("SELECT * FROM onboarding_requests WHERE request_id=%s", (UUID(request_id),)).fetchone()
            if previous:
                if previous["actor_id"] != actor_id or previous["fingerprint"] != fingerprint:
                    raise ValueError("Enrollment request changed")
                return dict(previous)
            if db.execute("SELECT 1 FROM projects WHERE tenant_id=%s OR dify_app_id=%s", (tenant_id, UUID(app_id))).fetchone():
                raise psycopg.errors.UniqueViolation("Project already registered")
            db.execute("INSERT INTO onboarding_requests (request_id,tenant_id,app_id,actor_id,fingerprint,state) VALUES (%s,%s,%s,%s,%s,'in_progress')",
                       (UUID(request_id), tenant_id, UUID(app_id), actor_id, fingerprint))
        return None

    def finish_enrollment(self, request_id: str, state: str, role_id: int | None = None) -> None:
        with psycopg.connect(self.database_url) as db:
            db.execute("UPDATE onboarding_requests SET state=%s, role_id=COALESCE(%s,role_id),updated_at=now() WHERE request_id=%s AND state != 'completed'",
                       (state, role_id, UUID(request_id)))

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
