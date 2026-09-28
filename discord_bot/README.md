# AW5 Discord demo bot

This local adapter implements `/start` in one configured text channel and
accepts ordinary text messages, `/ask`, or `/list` in a bot-created private thread. The
bot fetches the member's current project roles from the configured Discord
server before Start, project selection, and every question. It derives the AW5
`tenant_id` from a configured role-to-tenant mapping and selects the corresponding
Dify app from local operator configuration. The Discord user ID identifies the
ticket owner and conversation; there is no manual user-ID allowlist. Command
text cannot supply an arbitrary app, dataset, or tenant.

For the dated implementation and evidence handoff, see
[Discord bot demo handoff](../docs/architecture/discord-bot-demo-handoff-2026-09-28.md).

This is demo source code, not tenant-isolation evidence. The current Nature
Footprint workflow does not by itself enforce cross-tenant retrieval. Each
configured Dify app must contain only its authorized project Knowledge Bases;
Project B must be onboarded and tested separately before making an isolation
claim.

## Local setup

1. Use Python with `discord.py` installed from `requirements.txt`. Keep the
   virtual environment outside Git or in `.venv/`.
2. Copy `.env.example` to `discord_bot/.env`. The example already has the IDs
   supplied for `AW5 Demo Test` and `#aw5-start`; fill the bot token locally.
3. Copy `tenants.example.json` to
   `output/discord-bot/tenants.local.json`. The example already has the supplied
   Nature Footprint Member role ID; verify the **Chatflow API** base URL for the
   intended tenant-specific Dify app.
   `tenant_name` is an optional display label for the project-selection button;
   if omitted, the bot displays the configured Discord role name.
   Set its app API key in `AW5_DIFY_API_KEY_1` in `.env`. The local file is under
   ignored `output/` and must not contain the API key itself.
   To enable `/list`, also create a Dify **Knowledge API** key in the same
   workspace and set `AW5_DIFY_KNOWLEDGE_API_KEY_1` in `.env`. Add a
   `dify_knowledge_api_key_env` field to the ignored local JSON only if a
   different environment variable name is needed; by default the bot reads
   `AW5_DIFY_KNOWLEDGE_API_KEY_<tenant_id>`. This is separate from the Chatflow
   app key. If the Knowledge key is absent, questions continue to work but
   `/list` reports that inventory is unavailable. Do not paste keys into chat.
   The supplied `AW5-RAG Test4.7.yml` is an `advanced-chat` Chatflow whose
   Start node has no extra inputs, so the adapter's `inputs: {}` request fits
   its exported interface. The owner later reported publishing Test4.7 and
   demonstrated the Discord-to-Dify path in this chat. That demo does not
   promote Test4.7 to the current-main Dify workflow or prove tenant isolation.
   The export does not include a usable API credential.
4. Have an authorized Discord server administrator grant the configured project
   role to each approved member. Removing that role denies new requests; no
   `discord_bot.members add` command is needed. Restrict who can manage the role.
5. In Discord Developer Portal, open **AW5-Bot → Bot → Privileged Gateway
   Intents** and enable **Message Content Intent**, then save. The bot needs
   this to receive ordinary question text. Leave **Server Members Intent**
   disabled; the bot fetches the current member record by ID on each request.
6. From the repository root, load the local env file and run the adapter:

   ```sh
   set -a
   source discord_bot/.env
   set +a
   .venv/bin/python -m discord_bot.bot
   ```

The bot registers guild-scoped slash commands and posts a persistent **Start**
button in `#aw5-start` on startup. It records the panel message ID in local
SQLite so a restart reuses the existing button instead of posting another.
The button and `/start` use the same authorization and ticket creation path.
If exactly one configured project matches the user's current Discord role,
the bot opens a ticket directly. If multiple
projects match, it shows private buttons to choose one. Clicking a project
rechecks the current role before creating a private thread.
The chosen AW5 `tenant_id` is stored in that ticket; another project requires
another ticket. The bot adds the authorized requester and stores a ticket
record. Plain text messages and `/ask` work only for that requester in that
thread, recheck the current role, and forward the question to the
tenant-specific Dify Chatflow. The Dify conversation ID is stored per thread.
`/list` works only for the ticket owner in that ticket. It rechecks the current
Discord role, reads the paginated Knowledge Base and document lists, and shows
only documents whose Dify document metadata has the exact AW5 `tenant_id` for
the ticket. It shows disabled/archived documents with their status. Documents
without that metadata are omitted. The result is private to the requester and
does not send a Chatflow question or change the conversation. A listed document
is not necessarily connected to the currently Published Chatflow retrieval node;
`/list` is a metadata inventory, not a guarantee that `/ask` can cite the file.
Messages outside bot-created private tickets, bot messages, and messages
without text are ignored. Attachments are not forwarded to Dify.
The answer is posted in the private thread after Dify returns it. Discord shows
the bot's typing indicator while Dify is processing. The bot does not invent
or append source citations; the selected Dify workflow remains
responsible for grounding and citation text.

The app needs `View Channels`, `Send Messages`, `Create Private Threads`,
`Send Messages in Threads`, `Read Message History`, and `Embed Links` in the
start channel. A server owner or anyone with Discord `Manage Threads` can
view private threads. Do not place private corpus text or credentials in the
public start channel.

## Current limits

- Project buttons cover up to 25 eligible projects and expire after 3 minutes.
  Each project still needs its own configured Discord role and tenant-specific
  Dify app. The button label does not grant access.
- Local SQLite stores tickets, Dify conversation IDs, and the Start panel ID.
  Old membership rows in an existing database are ignored and left intact.
  Existing `.env` files using `AW5_MEMBERSHIP_DB` still work; new setups use
  `AW5_STATE_DB` for the same file.
- The configured Discord server and its role administrators are the demo trust
  boundary. This does not verify Dify cross-project retrieval isolation or
  provide production identity governance.
- Dify requests use a 30-second HTTP timeout. Errors return a generic message
  in Discord; they are not scored as RAG quality evidence.
- Knowledge API access uses a separate server-side credential with workspace
  scope. The backend filters the response by AW5 project metadata after
  authorizing Discord membership. This is a demo filter, not verified
  database-level tenant isolation. Listing traverses paginated Knowledge Bases
  and documents, so large workspaces can take longer.
- Installing dependencies, running live Discord/Dify calls, onboarding Project
  B, and isolation testing are separate operational steps.
