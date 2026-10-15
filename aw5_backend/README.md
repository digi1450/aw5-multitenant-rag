# AW5 backend: project registry and Discord authorization

**Source update 2026-10-10:** the administrator portal now accepts the App API
key without requiring a Dify App ID field. The backend resolves exactly one app
from the existing restricted digest-only key-binding view before provisioning,
then retains the Published workflow, metadata and key-binding checks. The
resolved App ID remains available in registered-project details. This source
change does not establish live deployment or second-project enrollment. The
terminal fallback and private admin API still accept an explicit App ID.

The portal also provides **เปลี่ยนยศที่ผูก** in each project's details. Choose
an unbound safe Discord role, or create a zero-permission role named after the
project, then confirm. This changes only the project's role mapping: tenant ID,
Dify app/key, datasets and ticket/conversation history are retained. It does not
delete the previous Discord role or assign members to the new role. Subsequent
Start/list/question authorization uses the newly registered role; existing
tickets still require their original owner and current project membership.

Role changes require fresh administrator authorization, Origin and CSRF checks.
A separate `project_role_changes` journal reserves the operation before role
creation; the mapping update and journal completion commit together. Incomplete
or ambiguous operations are retained as `needs_attention` and block another
change for that project. Verify the Discord role and mapping before manual
recovery; do not delete the journal or blindly retry. The additive table/index
are created by the normal backend startup schema initialization. Source/offline
tests do not establish live deployment or real role creation.

Each registered project has a red **ลบ** button on its right. The administrator
must type the exact project name to confirm. `DELETE
/v1/admin/portal/projects/{tenant_id}` rechecks the session/current admin role,
Origin/CSRF, guild and displayed app/role binding. One AW5 database transaction
removes that tenant's ticket/conversation mappings, dataset bindings, completed
role-change/enrollment journals and project registration. Re-registration is
then possible; old tickets cannot continue through AW5. Neither Discord roles
or messages nor Dify apps, documents or conversations are deleted. There is no
Portal undo. In-progress/needs-attention provisioning journals block deletion
until inspected and recovered; the delete action must not erase ambiguous
external-operation evidence. This is an administrator-triggered action, not
automatic cleanup when a Discord role disappears.

**Update 2026-10-03:** local administrator onboarding is implemented. Use
`/aw5-admin` in the configured private admin channel to open a one-use link.
The backend checks the current admin role, accepts an explicit stable AW5
`tenant_id`, validates the Dify app/key and Published corpus, and binds an
existing project role or creates a new role with zero server permissions.
App keys are entered directly into the loopback backend and encrypted in AW5
PostgreSQL; they are never sent through Discord. See the
[admin onboarding handoff](../docs/architecture/admin-onboarding-2026-10-03.md)
for configuration, verification and incomplete-operation recovery.

The owner installed and Published v3.2 and reported that Discord answered after
installing the strict-scope seek guard. The admin link/session/model flow,
current key binding, and Discord command registration were checked live.
Actual enrollment of a second real project, role creation and ISO-01 remain
unverified. The 2026-10-15 full offline suite has 100 passing tests; see
[the current checkpoint](../docs/architecture/progress-2026-10-15.md).

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
own PostgreSQL database. An administrator supplies a stable AW5 `tenant_id` when
registering a project; existing document metadata and project IDs are preserved.
Portal registration needs a project role selection (or new-role creation) and
Chatflow API key once; the backend derives the Dify app ID from that key.
Adding or removing members from that role needs no AW5 update.
The bot only receives project names/IDs and answers, never Dify credentials.
Tickets have a `closed_at` timestamp. On backend startup, the schema adds that
column to an existing AW5 PostgreSQL database if necessary. The private bot
API can close a ticket for its owner; later questions and `/list` calls are
denied even if Discord unarchives the thread.

## One-time setup

1. Run `.venv/bin/python -m aw5_backend.bootstrap_local` once from the repo
   root to create a **restricted Dify database reader** with a random password
   and a private `aw5_backend/.env`. Review this script before running it. It
   reads the existing ignored `discord_bot/.env` only for Discord identity/token
   and the Start channel. It prompts for the Knowledge API key with hidden input
   and writes that key only to backend configuration. It never changes a Dify
   app or calls Publish.
   In the Dify PostgreSQL database, an administrator applies
   `dify_read_view.sql`, creates a login role `aw5_sync_reader`, and grants it
   `USAGE` on the `public` schema and `SELECT` on
   `aw5_published_retrieval_v1` and `aw5_app_key_bindings_v1` only. Do not give this role access to Dify base
   tables. This is a database role, not a Dify workspace account. The view
   Published view exposes app ID, workflow ID and retrieval dataset IDs; the
   separate key binding view exposes only app ID and a SHA-256 token digest.
2. Keep the generated `.env` local and secret. It contains independent random
   values for the AW5 PostgreSQL password, bot and admin API tokens, Fernet key,
   and Dify reader password. It also supplies the Discord Start/admin channel
   settings used by bot Compose. The Knowledge API key is workspace scoped;
   authorization happens in AW5. Bot Compose no longer loads `discord_bot/.env`:
   it receives only its explicit Discord/backend environment allowlist from the
   Compose invocation's `aw5_backend/.env`.
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
4. Prefer the local administrator portal described above. For a terminal
   fallback with `AW5_BACKEND_ADMIN_TOKEN` set locally, register each project once:

   ```sh
   .venv/bin/python -m aw5_backend.admin register --tenant-id TENANT_ID --name "Nature Footprint" --discord-role-id ROLE_ID --dify-app-id APP_ID
   ```

   The CLI prompts for the Chatflow API key without displaying it or placing it
   in shell history. `python -m aw5_backend.admin status` reports sync status.
   Registration checks that the role exists; the role does not need to be
   created by AW5. Supply the same tenant ID already used in document metadata.
   The backend checks app/key binding and encrypts the app key at rest. The private admin API also supports
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
