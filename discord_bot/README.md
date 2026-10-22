# Discord interface

The bot forwards authorized operations to the AW5 backend; it never reads Dify credentials, databases or the Docker socket. Complete [installation](../docs/installation.md) before starting it.

| Interaction | Behavior |
|---|---|
| Start button or `/start` | Shows eligible projects and opens a private thread |
| Ordinary text or `/ask` | Asks the thread's project-scoped assistant |
| `/list` | Lists files from the currently authorized Published selection |
| `/close` | Closes the AW5 ticket and archives the thread |
| `/aw5-admin` | Offers a one-use loopback portal link in the configured admin channel |

Enable **Message Content Intent** in the Discord Developer Portal for ordinary text. Server Members Intent is not required for the backend's REST membership lookup. In the Start channel, the bot needs View Channel, Send Messages, Create Private Threads, Send Messages in Threads, Read Message History and Embed Links. Use Application Commands must be allowed for users. Creating project roles additionally requires Manage Roles, with the bot's highest role above those roles.

Only the thread owner with the current project role can ask/list. Closing does not retrieve data and remains available to the owner after project-role removal. Server owners and members with Manage Threads may see private threads; they are not a substitute for backend authorization.

Docker settings come from the explicit allowlist in `aw5_backend/compose.yml`, interpolated from `aw5_backend/.env`. `discord_bot/.env` is only used by bootstrap or an optional host/Terminal run; never put Dify keys in it.

The bot's local SQLite file stores the Start-panel record. Tickets and Dify conversation IDs are owned by AW5 PostgreSQL. Keep one bot instance running. Attachment processing is not supported; questions use typed text. The project selector supports at most 25 eligible projects per click.

For commands and setup, see [installation](../docs/installation.md). For known evidence limits, see [limitations](../docs/limitations.md).
