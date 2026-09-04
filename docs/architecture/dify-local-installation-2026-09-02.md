# Local Dify installation — 2026-09-02

## Authorization and scope

The owner approved installing Dify with Docker Compose in
`/Users/digital/Documents/Code/dify-local`, using localhost port 8080 and the
release's PostgreSQL/Weaviate services. They requested the latest stable version.
This supersedes the installation-specific undecided status in the earlier
[direction record](current-direction-2026-09-02.md).

The AW5 repository remains `/Users/digital/Documents/Code/AW5Project`. The sibling
directory holds the upstream Dify runtime, not a replacement AW5 repository.
Workflow changes saved in Dify's database do not automatically update Git;
reviewed DSL exports belong in this repository.

## Version selection

- Latest stable Dify checked against the official GitHub release API: **1.17.0**.
- Upstream checkout: tag `1.17.0`, commit
  `09a855dcef24c0edc7431c46c0cfaa494481daf5`.
- Docker Desktop **4.89.0**, matching the latest official release notes checked
  on 2026-09-02; Engine/CLI **29.7.2**, Compose **5.5.0**, Apple Silicon.
- Dependency image tags follow Dify's release Compose file. They are not a claim
  that every dependency independently uses its newest major release. Fresh image
  pulls obtain the current images for those supported tags.

Sources: [Dify release](https://github.com/langgenius/dify/releases/tag/1.17.0),
[Docker release notes](https://docs.docker.com/desktop/release-notes/),
[Dify Compose guide](https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose).

## Local configuration

- Compose project: `aw5-dify`.
- Runtime working directory: `/Users/digital/Documents/Code/dify-local/docker`.
- Browser URL: `http://localhost:8080`; initial setup: `/install`.
- The local `docker-compose.override.yaml` replaces nginx's published ports with
  `127.0.0.1:8080:80` and removes the host-published plugin debugging port.
- Upstream Compose and `.env.example` remain unchanged. The local `.env` contains
  generated internal credentials and has file mode `0600`; never commit or print it.
- Websocket and trigger URLs include localhost port 8080. Weaviate anonymous
  access is disabled; Weaviate/Next.js telemetry is disabled.
- PostgreSQL, Redis, Weaviate, application files and plugin storage use bind
  mounts under `docker/volumes/`. Dify's Agent sandbox additionally uses two
  Docker named volumes for `/home/dify` and `/workspace`; those live in Docker
  Desktop's storage, not in the sibling source directory.
- The only published host port in the resolved Compose configuration is nginx
  on loopback port 8080. This is a local installation, not a shared LAN/VPN service.

## Verification status

Verified on 2026-09-02 after installation:

- Configuration validation, image pull and `docker compose up -d` succeeded.
- All 15 long-running services were running with zero restarts at the final
  check. The one-shot `init_permissions` container exited successfully (code 0).
- API, PostgreSQL, Redis, code sandbox and Agent local sandbox health checks
  were healthy. Services without configured health checks are only described
  as running, not independently health-tested.
- All 12 distinct images are native `arm64`.
- `GET http://localhost:8080/install` returned HTTP 200.
- `GET /console/api/setup` returned `{"step":"not_started","setup_at":null}`.
- Browser UI displayed **Setting up an admin account**, with email, username,
  password and **Set up** fields/button. The page was left open for the owner.
- Plugin database initialization and Agent backend startup completed. Worker
  logs showed successful routine scheduled tasks; no model workload was tested.
- The actual nginx binding is `127.0.0.1:8080`; no other host port is published.

Container states and image digests are recorded in
[installation evidence](dify-local-installation-2026-09-02-evidence.json).
This proves initial installation readiness, not long-term stability, recovery,
RAG quality or tenant isolation.

No administrator account has been created by the agent. No provider selected,
API key configured, Nature Footprint corpus imported, model inference performed,
workflow imported/published, or RAG evaluation run by this installation.

## Operating the installation

Run these commands in `/Users/digital/Documents/Code/dify-local/docker` with
Docker Desktop running:

```sh
docker compose ps
docker compose stop
docker compose start
```

`stop` stops services and preserves data. `start` restarts the existing containers.
Use `docker compose up -d` when containers need to be created or configuration
changes applied. Do not use `down -v`, prune volumes, or delete the runtime folder
as a routine stop procedure.

Before an upgrade, preserve the local `.env`, override, PostgreSQL data/database
backup, application/plugin/vector data and Agent named volumes. A Git checkout or
DSL export alone is not a full backup. Backup/restore has not been tested here.

## Remaining work

The owner subsequently created the administrator account and configured the
official Gemini provider. The custom Gemini Embedding 2 (AW5) 0.1.4 provider was
then installed using [third-party signature verification](gemini-embedding-2-local-signing-2026-09-02.md).
The owner subsequently configured its credentials and approved a synthetic PDF
pilot. [The pilot record](gemini-embedding-2-local-pilot-2026-09-02.md) documents
successful text/image indexing and three queries ranking the expected source
first; this does not establish answer quality or real-corpus readiness.
Further model configuration and private document transfer approval remain
separate. The target single
Knowledge Retrieval workflow, trusted project-tenant authorization and isolation
tests remain unimplemented/unverified. Old DSL files and evaluation scores remain
historical controls.
