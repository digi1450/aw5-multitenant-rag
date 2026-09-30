# AW5 backend: project registry and Discord authorization

**Recorded status: local backend started and Nature Footprint registered on
2026-09-29. On 2026-09-30, live Discord questions returned HTTP 503 after Start
succeeded; an AW5/Dify `api` service-name collision was also observed. Renaming the
AW5 service to `aw5_api` restored unique Dify API DNS resolution and the AW5
healthcheck passed. A subsequent live question still returned HTTP 503 because
the HTTP client read only the first chunk of Dify's JSON response. The client
now reads the complete response within its 2 MB limit; a preflight plus Dify
diagnostic succeeded. The owner then confirmed a live Discord answer, and the
AW5 API recorded HTTP 200 for that request.**
Read the [current implementation handoff](../docs/architecture/aw5-backend-discord-handoff-2026-09-30.md)
for operating instructions, evidence limits and proposed next work.
The administrator still clicks Publish in
the Dify UI. AW5 reads the current Published workflow and synchronizes its
Knowledge Retrieval dataset IDs in the background and before each request.
There is no Dify publishing account or publish API call in this service.

AW5 stores projects, role mappings, tickets, and Dify conversation IDs in its
own PostgreSQL database. A new project receives an AW5 `tenant_id` when
registered. Registration needs its Discord role ID, Dify app ID, and Chatflow
API key once; adding or removing members from that role needs no AW5 update.
The bot only receives project names/IDs and answers, never Dify credentials.
Tickets have a `closed_at` timestamp. On backend startup, the schema adds that
column to an existing AW5 PostgreSQL database if necessary. The private bot
API can close a ticket for its owner; later questions and `/list` calls are
denied even if Discord unarchives the thread.

## One-time setup

1. Run `.venv/bin/python -m aw5_backend.bootstrap_local` once from the repo
   root to create a **restricted Dify database reader** with a random password
   and a private `aw5_backend/.env`. Review this script before running it. It
   reads the existing ignored `discord_bot/.env` for the bot and Knowledge API
   keys. It never changes a Dify app or calls Publish.
   In the Dify PostgreSQL database, an administrator applies
   `dify_read_view.sql`, creates a login role `aw5_sync_reader`, and grants it
   `USAGE` on the `public` schema and `SELECT` on
   `aw5_published_retrieval_v1` only. Do not give this role access to Dify base
   tables. This is a database role, not a Dify workspace account. The view
   exposes only app ID, Published workflow ID, and retrieval dataset IDs.
2. Keep the generated `.env` local and secret. It contains independent random
   values for the AW5 PostgreSQL password, bot and admin API tokens, Fernet key,
   and Dify reader password. The Knowledge API key is workspace scoped;
   authorization happens in AW5.
3. After reviewing the configuration, start `aw5_backend/compose.yml`. It
   creates a separate AW5 PostgreSQL database and binds the API to
   `127.0.0.1:8765`. The API container joins the existing Dify Docker network
   to reach Dify's read view and Knowledge/Chatflow APIs. Schema tables are
   created on backend startup. Do not expose port 8765 to a public interface.
   This Compose file mounts backend source read-only into the API container.
   Start it from the repository root with
   `docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml up -d aw5_api`.
   After editing backend Python code, run
   `docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml restart aw5_api`
   to load the changes. The mount alone does not reload a running Python process.
   Rebuild the image when `requirements.txt` or `Dockerfile` changes.
4. With `AW5_BACKEND_ADMIN_TOKEN` set locally, register each project once:

   ```sh
   .venv/bin/python -m aw5_backend.admin register --name "Nature Footprint" --discord-role-id ROLE_ID --dify-app-id APP_ID
   ```

   The CLI prompts for the Chatflow API key without displaying it or placing it
   in shell history. `python -m aw5_backend.admin status` reports sync status.
   Registration checks that the role exists; the role does not need to be
   created by AW5. The backend generates the AW5 `tenant_id` and encrypts the
   app key at rest. The private admin API also supports
   `POST /v1/admin/projects` and `GET /v1/admin/projects`.
5. For the existing demo's private threads, run
   `.venv/bin/python -m aw5_backend.import_legacy_tickets` from the repository
   root after setting `AW5_BACKEND_ADMIN_TOKEN`. It reads the old SQLite file
   in read-only mode and imports only ticket metadata and Dify conversation
   IDs. It is safe to rerun: existing thread IDs are skipped. It does not copy
   messages or private corpus data.
6. Configure and start the Discord bot Compose service as described in
   [its README](../discord_bot/README.md).

The backend checks current Discord member roles for every Start, `/list`, and
question. It verifies that every document in each selected Published Knowledge
Base has the exact AW5 `tenant_id` metadata before permitting an answer.
Missing metadata, a mismatch, or an unavailable API suspends that project's
access. Published changes are picked up automatically, without updating a
tenant JSON file.

## Limits and evidence

- This does not prove Dify retrieval isolation. The Dify app must have only
  Knowledge Bases for its project. A Publish can race an in-flight question;
  AW5 cannot atomically pin Dify's Chatflow call to the workflow it just
  checked. A strict cross-project security claim needs a controlled publish
  path or another enforced retrieval boundary and a two-project test.
- The service currently runs as one API process. Its per-ticket request lock is
  local to that process. Scaling to multiple replicas requires a shared lock.
- Metadata validation calls the Knowledge API on each request. This favors
  detecting document changes before answering, but increases latency and API
  load. The backend reuses one HTTP client session for Discord and Dify while
  running, checks up to four Knowledge Bases concurrently while still validating
  every document, and logs Published-view, document-validation, preflight, and
  Dify answer durations. Use these timings before choosing a different
  validation strategy. A time-based document cache is not enabled because
  adding a file to an existing Knowledge Base would not change the Published
  workflow ID.
- Existing role changes take effect at the next request. Already posted
  answers and requests in flight cannot be recalled.
- Local verification on 2026-09-29: AW5 API health responded; the restricted
  Dify reader could read its Published projection but could not read Dify base
  tables; Nature Footprint registered as AW5 `tenant_id = 1`; an authorized
  Discord member saw one project; one imported ticket listed three files; and
  PostgreSQL contained one project, 13 migrated tickets, and three dataset
  mappings. No Dify question was sent during this verification.
- One live Start and a post-fix Discord answer are confirmed. Project B,
  live multi-role/revocation and post-Docker `/close` checks, cross-project
  isolation, and formal quality, latency, reliability and cost remain unverified.
