# Installation

This guide targets a fresh **single-host local demo** on macOS/Linux or Windows with WSL. It requires manual configuration of Discord, Dify and your model provider. Do not apply bootstrap to an existing shared Dify deployment without reviewing the database changes.

## 1. Prerequisites and Python environment

- Git and Python 3.14.
- Docker Engine/Desktop with Compose **2.24.4+**. Allow at least 2 CPU cores and 8 GiB of Docker memory; more may be needed for indexing.
- A Discord server where you can create an application/bot, roles and channels.
- Your own provider account/API credentials for the selected embedding and answer models. Indexing and questions can incur provider charges.
- Free localhost ports 8080 (Dify) and 8765 (AW5 portal/API).

Clone this repository and run all commands from its root unless otherwise stated:

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r aw5_backend/requirements.txt -r discord_bot/requirements.txt
.venv/bin/python -m unittest discover -s tests
```

Dependency versions are pinned from the development environment. Python/OS binary wheels, upstream infrastructure image tags and hosted model behavior are not bit-for-bit immutable. No live setup is performed by the tests.

## 2. Prepare pinned Dify

```sh
.venv/bin/python scripts/prepare_dify.py
```

This clones upstream Dify **1.17.0** into ignored `output/vendor/dify`, verifies commit `09a855dcef24c0edc7431c46c0cfaa494481daf5`, generates local random service secrets and copies the loopback Compose override. It refuses to overwrite existing configuration or use a checkout with tracked changes. It does not start Docker. Use `--source-dir /your/new/path` if needed; adjust subsequent paths accordingly.

Start Dify explicitly:

```sh
cd output/vendor/dify/docker
docker compose -p aw5-dify up -d
docker compose -p aw5-dify ps
```

Open `http://localhost:8080/install`, create your local account and sign in. Return to the AW5 repository root for the next steps. The Compose project name must remain `aw5-dify` for the default backend bootstrap/container/network names to match.

The override binds Dify's web interface to loopback port 8080 and removes the plugin debugging port. Use the pinned upstream [Docker deployment documentation](https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose) for host-specific prerequisites. Review [Dify's license](https://github.com/langgenius/dify/blob/1.17.0/LICENSE); AW5 project tenants are distinct from Dify Workspaces.

## 3. Configure models, documents and Chatflow

1. In Dify settings, install/configure the official Gemini provider referenced by the template (0.9.10). Enter your own provider key locally. The reference resolver/answer models are recorded in [the workflow README](../dify/README.md); use models available to your account and record any substitutions.
2. Create one Knowledge Base per primary file. To try public synthetic data, upload `examples/documents/requirements.md`, `design.md` and `schema.md` to three separate Knowledge Bases. Do not upload the examples' README as project evidence.
3. Choose an embedding model supported by your installed provider and complete indexing. The original private embedding plugin is not required by the portable template. These example files are text only; a standard text embedding provider is sufficient to exercise the integration, but is not a reproduction of the original corpus/embedding results.
4. Add a custom **Number** metadata field named exactly `tenant_id` to every Knowledge Base, then set it to the same positive integer on **every document** belonging to that AW5 project. Use `1` for a first synthetic demo. Optional `document_type` is a String field. Metadata is document data, not a default prompt value.
5. Import `dify/exports/aw5-rag.yml` as a Chatflow. Resolve the provider dependency, select the available models, and connect all of this project's Knowledge Bases to its **single Knowledge Retrieval node**. Keep the required `aw5_registry_json` input and Code-node bindings.
6. Verify the node inputs, structured-output schema and metadata-filter binding. The template intentionally has no Knowledge Base IDs; it is incomplete until this step. Do not add another project's Knowledge Bases.
7. Publish the configured Chatflow yourself and create its **App API key**. In the Knowledge API section, create a **Knowledge API key** for the same Dify Workspace. These are different keys; keep both private.

The backend supplies the registry input. A question entered alone in Dify's preview is not an end-to-end AW5 test. No full-document summary or automatic traceability feature is implied by importing this template.

## 4. Configure Discord

Create a Discord application/bot, enable **Message Content Intent**, and invite it using the `bot` and `applications.commands` scopes. Use your own bot token, server (guild) ID and Start text-channel ID.

In the Start channel, grant the bot View Channel, Send Messages, Create Private Threads, Send Messages in Threads, Read Message History and Embed Links. Allow Use Application Commands for intended users. Keep one bot instance active.

For the local portal, create a private administrator text channel and an application admin role. Allow that role and the bot to view/use commands in the channel. If you want AW5 to create project roles, grant the bot Manage Roles and place its highest role above project roles. A pre-existing safe project role can also be selected. The application admin role does not require Discord's Administrator permission.

```sh
cp discord_bot/.env.example discord_bot/.env
chmod 600 discord_bot/.env
```

Edit the local file and set:

```dotenv
AW5_DISCORD_BOT_TOKEN=<your bot token>
AW5_DISCORD_GUILD_ID=<your server ID>
AW5_DISCORD_START_CHANNEL_ID=<your start channel ID>
```

Leave Dify credentials out of this file. Bootstrap reads these Discord fields only; no host bot process needs to be started.

## 5. Initialize AW5 secrets and Dify read views

With Dify's PostgreSQL container running:

```sh
.venv/bin/python -m aw5_backend.bootstrap_local
```

Review the script before execution. It uses `docker exec aw5-dify-db_postgres-1` with the fresh deployment's default PostgreSQL admin/database names. It applies `aw5_backend/dify_read_view.sql`, creates or updates the dedicated `aw5_sync_reader` login and grants only its two views. It prompts privately for the **Knowledge API key**, then creates `aw5_backend/.env` with fresh AW5 database/service/encryption secrets. It refuses to overwrite an existing backend `.env`. It does not Publish a Dify app or send model requests.

Do not grant the reader access to Dify base tables. The views expose Published app/workflow/dataset IDs and digest-only app-key binding, not plaintext Dify tokens. Existing/nondefault database deployments need a reviewed manual equivalent rather than blindly running this bootstrap.

Edit the generated `aw5_backend/.env` to set both portal fields:

```dotenv
AW5_DISCORD_ADMIN_CHANNEL_ID=<your private admin channel ID>
AW5_DISCORD_ADMIN_ROLE_ID=<your application admin role ID>
AW5_ADMIN_PORTAL_ORIGIN=http://127.0.0.1:8765
```

The API URL/network defaults assume `aw5-dify`. For a deliberately different Compose project, set `AW5_DIFY_DOCKER_NETWORK` accordingly and adapt the bootstrap container reference. Keep `AW5_DIFY_KNOWLEDGE_API_BASE_URL=http://api:5001/v1` for the default Docker network.

## 6. Start AW5 and register a project

```sh
mkdir -p output/discord-bot
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml up -d --build
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml ps
curl --fail http://127.0.0.1:8765/health
```

AW5 uses its own PostgreSQL database. The backend API binds to `127.0.0.1:8765`; the bot has no published port. Docker receives its bot settings only through the Compose allowlist, not through `discord_bot/.env`.

Run `/aw5-admin` in the configured private admin channel. Open the ephemeral one-use link on the **host computer**; the portal is loopback-only. Supply a project name, stable numeric AW5 tenant ID, the Published Chatflow's **App API key**, and a safe existing/new project role. The tenant ID must exactly match the documents' metadata. The portal resolves App ID from the key and checks the binding before enrollment.

Assign the project role to intended members in Discord. In the Start channel, click Start or run `/start`, choose the project if prompted, then ask in the private thread. `/list` lists currently authorized files; `/close` closes that conversation. Adding a second project requires a separate app/corpus/role/tenant ID and testing; merely registering it is not proof of isolation.

Terminal registration is available through `python -m aw5_backend.admin --help`. It requires the local admin token and explicit App ID. The portal avoids putting keys into shell history and is the normal setup path.

## 7. Check and troubleshoot

| Symptom | Check |
|---|---|
| No project is offered | Registration, current member role, guild ID and project sync status |
| Project becomes unavailable | Every selected document's `tenant_id`, active Published selection, Knowledge API and reader permissions |
| Registry input error | Imported `aw5_registry_json` input and Code 1 binding; calls must go through AW5 |
| Model/plugin error | Provider credentials, available model name and resolved import dependencies |
| Admin link does not open | Open on the host, check loopback API health and use a fresh one-use link |
| New source/env changes are not reflected | Restart for Python source; recreate for env changes; rebuild for dependencies |
| Dify API DNS is ambiguous | AW5 service is named `aw5_api`; do not rename it `api` on the shared network |

Health checks do not exercise retrieval or prove isolation. Record actual outcomes of your own demo; do not reuse historical scores.

## Stop and preserve data

From the AW5 root:

```sh
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml stop
```

From the Dify Docker directory, use `docker compose -p aw5-dify stop`. Keep environment/encryption keys, AW5 PostgreSQL, Dify PostgreSQL/files/vector/plugin data and bot state backed up privately. Neither a DSL export nor a Git clone is a full data backup. Do not use `down -v`, Docker volume prune or delete the Dify working directory as routine cleanup.
