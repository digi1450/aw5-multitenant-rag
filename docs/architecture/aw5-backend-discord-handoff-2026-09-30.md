# AW5 backend and Discord handoff — 2026-09-30

This is the current implementation handoff for the Discord adapter and AW5
backend. The 2026-09-28 handoff describes the earlier adapter and is historical.
This record does not promote Test4.7 or change the owner-confirmed main Dify DSL.

## Current flow and owner decisions

- Discord is the demo entry point: Start or `/start` in the configured channel
  opens a private ticket. One eligible project opens directly; multiple eligible
  projects show buttons. A ticket belongs to one member and one AW5 `tenant_id`.
- Ordinary ticket text and `/ask` call the same answer path. The bot shows typing
  while waiting and posts the complete answer. Progressive text rendering was
  tried and rolled back at the owner's request.
- `/list` displays file names only from the project's Published Retrieval
  selection. File selection buttons and explicit selection forwarding are not
  implemented. Attachments receive an unsupported-file notice. Long code blocks
  and Markdown tables are split with their formatting boundaries preserved.
- `/close` records closure in the backend and archives the Discord thread. An
  owner can close after project-role revocation; closed tickets cannot ask/list.
- The backend checks current Discord roles for each authorized operation. There
  is no manual user-ID membership enrollment. Role IDs are registered per project;
  role names, user input and client-supplied tenant IDs do not grant access.
- AW5 owns a separate PostgreSQL database for projects, role mappings, tickets
  and Dify conversation IDs. App keys are encrypted using the local Fernet key.
  The bot receives no Dify credentials, graph or retrieved chunks.
- The administrator still Publishes in Dify's UI. AW5 reads app/workflow/dataset
  IDs through the restricted `aw5_published_retrieval_v1` database view. It uses
  the Knowledge API to validate each selected document's AW5 `tenant_id`.
  Missing/mismatched metadata or unavailable dependencies deny access.
- New projects are registered once using the admin CLI/API. New files still need
  correct project metadata and inclusion in Published Retrieval; automatic
  metadata assignment and an admin UI are not implemented.

## Runtime and operating instructions

The existing `aw5_backend/compose.yml` runs separate `postgres`, `aw5_api` and
`bot` containers. Dify stays in its own Compose deployment. AW5 API joins the
Dify network; bot reaches AW5 on its bot network and has no Docker socket or
Dify database connection. The AW5 API port is bound to loopback only.

Backend and bot source directories are mounted read-only for development.
Restart the relevant Python service after code changes; bind mounts do not
reload Python automatically. Rebuild when Dockerfiles/dependencies change.
Preserve PostgreSQL volumes and the local Fernet key; never use volume deletion
as a routine restart. Run only one bot instance.

```sh
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml up -d --build bot
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml restart aw5_api bot
.venv/bin/python -m unittest tests.test_aw5_backend tests.test_discord_bot
```

Local `.env` files remain ignored. SQLite under `output/discord-bot/` preserves
the Start panel ID and legacy sessions; new ticket/conversation state lives in
PostgreSQL. `import_legacy_tickets` is a one-time, repeat-safe metadata migration.
`bootstrap_local` is a local migration helper tied to the existing Dify container
and old environment layout; do not run it on an already configured installation.

## Verified evidence

- On 2026-09-29 the backend was started, Nature Footprint registered, and 13
  legacy tickets imported. The restricted reader could read the projection but
  could not read Dify base tables. These are local checks, not isolation proof.
- On 2026-09-30 the bot connected to Discord, synced commands, reused the Start
  panel and opened a live ticket. Its network health request returned HTTP 200.
- Two integration issues were observed: AW5 and Dify both used network name
  `api`, and one `aiohttp` read returned only part of a JSON response. Renaming
  AW5 to `aw5_api` removed the DNS ambiguity; reading all bounded response chunks
  corrected the reproducible JSON truncation. DNS ambiguity alone was not shown
  to explain all failed questions.
- After correction the owner confirmed a live Discord answer. AW5 recorded an
  ask HTTP 200 at 2026-09-30 01:24:38 Asia/Bangkok. One backend timing was 0.58 s
  preflight, 5.56 s Dify and 6.15 s total. This is an incident confirmation,
  not a latency, reliability or answer-quality evaluation.
- The latest focused suite passed 27 offline tests (13 backend, 14 bot), including
  a response split across network chunks. Tests are not live Discord/Dify proof.
- Latest read-only status check: one active project, three dataset mappings,
  no stored sync error; API/PostgreSQL healthy and bot running.

The local-only incident package is under
`output/research-evidence/experiments/2026-09-30-discord-ask-api-name-collision/`.
Keep it ignored; this handoff contains sanitized metadata only.

## Remaining limitations and proposed priorities

These items are review findings/proposals, not implemented changes or automatic
authorization to change Dify, infrastructure, or evaluation protocols.

1. Registration does not yet prove that the supplied app API key belongs to the
   registered Dify app ID. Fix this binding before onboarding more projects.
2. Dify Publish and document changes can race an in-flight ask. AW5 cannot pin
   its Chatflow call to the workflow it just validated. Keep one project corpus
   per assigned app; do not claim strict isolation from preflight alone.
3. Project B and ISO-01 remain unverified. Use another real organizational
   project and owner-approved controlled evidence for cross-project tests.
   Live multi-role selection, revocation and `/close` after Docker migration
   also need targeted confirmation.
4. There is no admin UI or project update/key-rotation endpoint. Registration is
   currently CLI/API based; automatic file metadata provisioning is absent.
5. HTTP sessions are pooled; PostgreSQL connections are opened per operation.
   Document validation runs on every request, and `/list` scans again for its
   inventory. No document TTL cache is enabled. A cache would need an explicit
   freshness/isolation policy for files added without a new Publish.
6. Dify ask timeout is 35 s and bot ask timeout 45 s; there is no whole-request
   deadline, bounded global question queue, or ticket-lock cleanup. The service
   assumes one API process and one bot instance.
7. `/health` confirms process liveness only. Dependency readiness, backup/restore
   verification and durable operational monitoring remain to be developed.

Read `aw5_backend/AGENTS.md`, its README and `discord_bot/AGENTS.md` before edits.
Keep workflow promotion, formal evaluation and tenant isolation evidence separate
from this implementation handoff.
