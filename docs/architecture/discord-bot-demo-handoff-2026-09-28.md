# Discord bot demo handoff — 2026-09-28

## Scope and status

`discord_bot/` is a local Python adapter between Discord and a configured Dify
Chatflow API. It is a demo path, separate from the owner-confirmed current-main
Dify workflow in `dify/exports/CURRENT.md`. The demo uses the owner-selected
Test4.7 app; its use in Discord does not promote Test4.7 to current main or
constitute a formal RAG evaluation.

**Verified from repository code and focused unit tests:**

- The Start button and `/start` use one ticket-creation path in the configured
  start channel. An eligible user has both an active local membership row and
  the matching Discord role. With one eligible project, Start opens a private
  ticket directly. With two to 25, it shows ephemeral project buttons; above
  that limit it fails closed. A selection rechecks current role and membership
  before creating a ticket.
- A ticket stores its owner, guild, AW5 `tenant_id`, and Dify conversation ID in
  local SQLite. The chosen tenant is fixed for that ticket. A different project
  needs a different ticket. Project names and button labels are display data,
  never authorization keys.
- Plain text questions and `/ask` use the same per-ticket Dify call. The bot
  ignores other channels, other users' messages, bot messages, and non-text
  messages. Before each Dify call it checks the ticket owner, active local
  membership, and project role. For plain text it fetches the member's current
  Discord role record by ID. The bot shows a typing indicator while Dify works.
- The focused suite in `tests/test_discord_bot.py` has nine passing tests,
  including a mocked two-project choice, a single-project direct start,
  revoked-role denial, and Dify conversation reuse. These tests do not contact
  Discord or Dify. Rechecked on 2026-09-28 with the project's `.venv` Python:
  9 tests passed.

**Verified from read-only local Dify metadata on 2026-09-28:**

- The `AW5-RAG Test4.7` advanced-chat app has ID
  `6647a5da-36d7-4c90-b0e7-a5b37f3e9de2`. Its current Published workflow
  pointer is `534d7def-f332-406d-8a15-6cd8810b6946`; the stored Published
  graph MD5 is `3fa4b4e3b619b5e0b39a33808481f5fe`. At inspection, the
  Draft graph had the same MD5. This identifies local runtime state, not an
  exported DSL file or a promotion to AW5 current main.
- Dify recorded ten successful `app-run` executions for that Published workflow
  on 2026-09-27. This run metadata does not identify the Discord entry point,
  exact questions or answers, or the bot revision used. The earlier local-only
  Draft Top K diagnostic (`output/research-evidence/experiments/2026-09-27-test4-7-topk30-context10-one-run/`)
  reported no Published workflow at its earlier inspection time; it is not a
  statement about the app's later state.
- The owner-supplied Test4.7 export was previously identified by SHA-256
  `35a8192cdcf24bc14147ce7c78f757fa14ca3f58ed5eda7f3496017220df63cb`
  in the local-only six-run Draft review
  (`output/research-evidence/experiments/2026-09-23-test4-7-shortlist-six-run-review/`).
  That file hash is not asserted to identify the later Published workflow.

**Owner-reported live demo observations from this chat:** the owner configured
and published a Test4.7 Dify app, started the local bot, opened private tickets,
received a Dify answer through `/ask`, then confirmed that ordinary ticket text
and the typing indicator worked. These are manual demo observations, not a
frozen evaluation package or an independently repeated runtime test. The
two-project selector was added after those observations and has not been
verified live in Discord. A bot process started before that code change needs
a restart to load the selector; no such restart is confirmed in this record.

## Local implementation map

- `discord_bot/bot.py`: Discord commands, Start/project buttons, private
  threads, message handling, typing state, and Dify response delivery.
- `discord_bot/auth.py`: intersection of backend membership and Discord role;
  per-ticket authorization before retrieval.
- `discord_bot/store.py`: SQLite memberships, tickets, conversation IDs, and
  Start panel message ID.
- `discord_bot/config.py`: configured guild/start channel and per-project role,
  Chatflow API URL/key, and optional display name. AW5 `tenant_id` means one
  software project; it is distinct from Dify's internal workspace tenant ID.
- `discord_bot/dify.py`: server-side Chatflow `/chat-messages` request.
- `discord_bot/README.md`: setup, required Message Content Intent, run command,
  permissions, and current limits. Read `discord_bot/AGENTS.md` before edits.

## Security boundary and remaining work

- A Discord role change does not update the local membership table. Both are
  checked on each new question; removing the project role blocks the next
  question even in an existing ticket. This does not retract answers already
  posted or cancel a Dify request already in flight.
- The present local configuration has Nature Footprint (`tenant_id = 1`) only.
  Project B is not onboarded. Its real role, trusted membership, dedicated
  Dify app, authorized Knowledge Bases, and controlled cross-project evidence
  are required before an isolation claim. The mocked two-project test verifies
  adapter control flow, not Dify retrieval isolation.
- Local SQLite and an owner-run Python process are demo infrastructure. There
  is no deployed membership synchronization service, production operations
  process, or formal quality/latency/cost evaluation for this adapter.
- Keep `.env`, API keys, tokens, local tenant configuration, SQLite files,
  private corpus text, and generated `output/` artifacts out of Git and chat.

## Safe continuation

This handoff belongs to `feature/dify-self-hosted`. Inspect `git status` before
editing and preserve unrelated work. With the project virtual environment
installed, use
`.venv/bin/python -m unittest discover -s tests -p 'test_discord_bot.py'`
for focused offline verification. Do not run a live
Discord/Dify test, alter external roles/apps, publish Dify, or make an
isolation claim without the owner-directed operational step and its evidence.
