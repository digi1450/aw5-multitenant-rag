# Discord bot demo handoff — 2026-09-28

## Scope and status

`discord_bot/` is a local Python adapter between Discord and a configured Dify
Chatflow API. It is a demo path, separate from the owner-confirmed current-main
Dify workflow in `dify/exports/CURRENT.md`. The demo uses the owner-selected
Test4.7 app; its use in Discord does not promote Test4.7 to current main or
constitute a formal RAG evaluation.

**Verified from repository code and focused unit tests:**

- The Start button and `/start` use one ticket-creation path in the configured
  start channel. The bot fetches the user's current Discord member roles from
  the configured guild; a configured project role grants demo access without a
  manually entered user ID. With one eligible project, Start opens a private
  ticket directly. With two to 25, it shows ephemeral project buttons; above
  that limit it fails closed. A selection rechecks the current role
  before creating a ticket.
- A ticket stores its owner, guild, AW5 `tenant_id`, and Dify conversation ID in
  local SQLite. The chosen tenant is fixed for that ticket. A different project
  needs a different ticket. Project names and button labels are display data,
  never authorization keys.
- Plain text questions and `/ask` use the same per-ticket Dify call. The bot
  ignores other channels, other users' messages, bot messages, and non-text
  messages. Before each Dify call it checks the ticket owner and fetches the
  member's current Discord roles by user ID. The ID identifies the user but is
  not an additional allowlist. The bot shows a typing indicator while Dify works.
- The local adapter waits for Dify's complete answer, then posts it in the
  ticket. It stores the Dify conversation ID per ticket and shows Discord's
  typing indicator while waiting.
- The focused suite in `tests/test_discord_bot.py` has fourteen passing tests,
  including a mocked two-project choice, a single-project direct start,
  revoked-role denial for ordinary text, `/ask`, and `/list`, paginated
  tenant-filtered inventory, and Dify conversation reuse.
  These tests do not contact
  Discord or Dify. Recheck with the project's `.venv` Python after changes.

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

**Owner-reported live demo observations from this chat, before role-only access:** the owner configured
and published a Test4.7 Dify app, started the local bot, opened private tickets,
received a Dify answer through `/ask`, then confirmed that ordinary ticket text
and the typing indicator worked. These are manual demo observations, not a
frozen evaluation package or an independently repeated runtime test. The
two-project selector was added after those observations and has not been
verified live in Discord. The role-only revision also needs a bot restart and
live confirmation; offline tests do not establish its runtime behavior.
The owner reported that the trial streaming display showed a few words, paused,
and then showed the rest at once. At the owner's request, the trial was rolled
back to the complete-answer behavior. Restarting the bot is needed to use this
revision; the rollback has offline verification only.

## Local implementation map

- `discord_bot/bot.py`: Discord commands, Start/project buttons, private
  threads, message handling, typing state, and Dify response delivery.
- `discord_bot/auth.py`: configured guild and project-role checks;
  per-ticket authorization before retrieval.
- `discord_bot/store.py`: SQLite tickets, conversation IDs, and Start panel
  message ID. Legacy membership rows are ignored and not deleted.
- `discord_bot/config.py`: configured guild/start channel and per-project role,
  Chatflow API URL/key, and optional display name. AW5 `tenant_id` means one
  software project; it is distinct from Dify's internal workspace tenant ID.
- `discord_bot/dify.py`: server-side Chatflow `/chat-messages` request.
- `discord_bot/knowledge.py`: read-only, paginated Knowledge API inventory for
  `/list`; exact AW5 document `tenant_id` metadata filter after role and ticket
  authorization. It includes disabled/archived matches with status and omits
  documents missing metadata. An inventory entry does not prove the Published
  Chatflow retrieves that document.
- `discord_bot/README.md`: setup, required Message Content Intent, run command,
  permissions, and current limits. Read `discord_bot/AGENTS.md` before edits.

## Security boundary and remaining work

- Discord roles are the demo membership authority. The bot fetches the current
  member record at Start, selection, and each question; removing the project
  role blocks the next request even in an existing ticket. If Discord cannot be
  checked, the bot does not contact Dify. A change does not retract answers
  already posted or cancel a Dify request already in flight.
- The present local configuration has Nature Footprint (`tenant_id = 1`) only.
  Project B is not onboarded. Its real role, dedicated
  Dify app, authorized Knowledge Bases, and controlled cross-project evidence
  are required before an isolation claim. The mocked two-project test verifies
  adapter control flow, not Dify retrieval isolation.
- Local SQLite and an owner-run Python process are demo infrastructure. There
  is no production role governance or operations
  process, or formal quality/latency/cost evaluation for this adapter.
- Keep `.env`, API keys, tokens, local tenant configuration, SQLite files,
  private corpus text, and generated `output/` artifacts out of Git and chat.
- `/list` needs a separate Knowledge API key in the local environment. The
  Chatflow app key alone is insufficient for Knowledge management endpoints.
  This source change has offline test coverage only; it has not been tested
  against live Discord or the Dify Knowledge API.

## Proposed file selection in tickets — not implemented

The owner proposed making `/list` interactive so the ticket owner can select one
or more files before asking a question, including a two-file comparison. The
current `/list` only displays a metadata inventory; no selection is stored, and
the Chatflow client sends `inputs: {}`. The bot does not yet constrain retrieval
to selected files.

An implementation would show only eligible, available files connected to the
ticket's authorized project's active Chatflow. It would store selected stable
file identifiers per ticket, allow changing or clearing the selection, and
recheck the current Discord role, ticket owner, project scope, and file
eligibility before every question. Unselected mode would retain the existing
project-wide behavior. The Dify Chatflow would need a trusted structured input
and a retrieval filter that enforces the selected set before evidence reaches
the answer model; merely adding file names to the question is insufficient.
The selected set must stay within the authorized AW5 `tenant_id` and must not
bypass the workflow's existing source-resolution rules. Exact Dify input and
filter behavior, multi-file comparisons, revocation, and live performance still
need a separate design and bounded validation. This proposal does not establish
tenant isolation or promote Test4.7 to current main.

## Safe continuation

This handoff belongs to `feature/dify-self-hosted`. Inspect `git status` before
editing and preserve unrelated work. With the project virtual environment
installed, use
`.venv/bin/python -m unittest discover -s tests -p 'test_discord_bot.py'`
for focused offline verification. Do not run a live
Discord/Dify test, alter external roles/apps, publish Dify, or make an
isolation claim without the owner-directed operational step and its evidence.
