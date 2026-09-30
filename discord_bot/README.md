# AW5 Discord adapter

The bot provides a Start button and `/start` in `#aw5-start`. A private ticket
accepts ordinary text, `/ask`, `/list`, and `/close`. The bot sends user and thread IDs to
the private AW5 backend. The backend looks up the member's current Discord roles,
resolves the project, reads the Published Dify selection, and calls the assigned
Dify app. No manual user-ID enrollment is needed. One eligible project opens a
ticket directly; two or more offer a project choice.

The bot container was started on 2026-09-30. Startup logs confirmed Discord
Gateway connection, guild command sync, and reuse of the existing Start button.
The bot reached the backend health endpoint over its Compose network, and its
mounted SQLite database contained the existing Start-panel record. A live Start
created a ticket, but questions returned HTTP 503. The AW5 API service and
Dify API service both used the Compose name `api`; renaming AW5 to `aw5_api`
fixed the DNS collision. A second failure came from reading only one chunk of
Dify's JSON response. The backend now reads the complete bounded response, and
a preflight plus Dify diagnostic answered successfully. The owner then retried
in Discord and confirmed that the bot answered; AW5 recorded HTTP 200 for that
request. `/close` remains unverified after the Docker move. Read the
[current handoff](../docs/architecture/aw5-backend-discord-handoff-2026-09-30.md)
for current operations and remaining work. The
[2026-09-28 handoff](../docs/architecture/discord-bot-demo-handoff-2026-09-28.md)
preserves earlier live observations.
The backend setup and validation steps are in
[AW5 backend README](../aw5_backend/README.md).

## Run the bot with Docker Compose

1. Start the AW5 backend and register the Nature Footprint project using its
   Discord role ID, Dify app ID, and Dify Chatflow API key. Complete the one-time
   legacy ticket import if existing threads need to keep working.
2. Copy `.env.example` to `discord_bot/.env`. Set the Discord bot token and the
   same `AW5_BACKEND_BOT_TOKEN` configured for the backend. The Compose service
   overrides the API URL with `http://aw5_api:8765` on its private bot network.
   Do not copy keys into Git or chat.
3. Enable **Message Content Intent** for ordinary ticket text. The bot does not
   need Server Members Intent; the backend checks membership through Discord's
   REST API.
4. Stop any bot process running in a Terminal, then start the Compose service
   from the repository root:

   ```sh
   docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml up -d --build bot
   ```

The bot has no published port and can reach only the AW5 API service on its
Compose network. Its source code is mounted read-only for local development.
The existing ignored `output/discord-bot/aw5.sqlite3` is mounted at
`/data/aw5.sqlite3`, preserving the Start panel ID across container recreation.
After changing bot Python code, run
`docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml restart bot`.
Rebuild when bot dependencies or its Dockerfile change. Keep only one bot
instance running.

For a local Terminal run instead, keep `AW5_BACKEND_API_URL` on loopback and
load `discord_bot/.env` before running `.venv/bin/python -m discord_bot.bot`.

The existing Start panel message ID stays in local SQLite. New tickets and
Dify conversation IDs live in AW5 PostgreSQL. Questions require the ticket
owner's current project role, even if the ticket was opened earlier. A role
removed during an already running Dify request does not retract that request.
The bot posts the complete answer after Dify finishes and displays Discord's
typing indicator while waiting. Long fenced code blocks are reopened with their
language in each message, and long Markdown tables repeat their header. An
individual table row longer than the message limit is sent as plain text.
`/close` closes the backend ticket and archives its private thread. A closed
ticket cannot ask or list files, even if its thread is later unarchived; use
Start to begin a new conversation. A ticket owner can close it after losing
the project role, since closing does not retrieve project data.
If `/close` reports that the backend route is missing, restart the `aw5_api` service
from `aw5_backend/compose.yml` to load mounted source changes. A backend HTTP 404
means that its running API lacks the route;
HTTP 403 means the recorded ticket owner does not match the requesting user.

The bot needs View Channel, Send Messages, Create Private Threads, Send
Messages in Threads, Read Message History, and Embed Links in `#aw5-start`.
A server owner or member with Manage Threads can see private threads.

## Limits

- The project selector supports at most 25 eligible projects per click.
- `/list` shows file names from the current Published Knowledge Retrieval
  selection; it does not show Knowledge Base names or select files for `/ask`.
- The bot ignores messages outside its private ticket threads. It warns when a
  ticket message contains attachments, does not read the attachments, and
  answers only the typed text when both are present.
- The Test4.7 Discord demo is separate from the owner-confirmed current-main
  Dify workflow. Multi-project isolation remains unverified until a second
  real project is onboarded and controlled testing is completed.
