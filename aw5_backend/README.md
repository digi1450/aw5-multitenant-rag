# AW5 backend

Python/aiohttp service for current Discord-role authorization, project registration, Published Dify selection validation and the loopback administrator portal. See the [complete installation guide](../docs/installation.md).

## Modules

- `api.py`, `service.py`: API routes and authorized operations.
- `db.py`, `schema.sql`: PostgreSQL registry and provisioning journals.
- `integrations.py`: Discord and Dify clients; validates every selected document's project metadata.
- `source_registry.py`: query-based shortlist derived from freshly authorized files.
- `onboarding.py`, `static/`: local administrator portal.
- `dify_read_view.sql`: narrow Dify Published selection and digest-only app-key views.
- `bootstrap_local.py`: opt-in local setup of a dedicated Dify reader and AW5 secrets; review before running.
- `admin.py`: loopback terminal registration/status fallback.
- `import_legacy_tickets.py`: optional migration for an existing installation; not required for a new setup.

## Operations

Run from the repository root:

```sh
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml up -d --build
docker compose --env-file aw5_backend/.env -f aw5_backend/compose.yml ps
curl --fail http://127.0.0.1:8765/health
```

Python source is mounted read-only for local development. Restart the affected service to load source changes; recreate it after environment changes and rebuild after dependency/Dockerfile changes. Stop with `docker compose ... stop`; do not delete database volumes as routine cleanup.

The backend alone holds Dify app/Knowledge/database credentials. The Discord bot receives an explicit allowlist of Discord and backend settings. `tenant_id` identifies one AW5 software project and is distinct from Dify's Workspace tenant.

Project deletion affects AW5 registration/ticket records, not Dify apps/documents or Discord roles/messages. Investigate uncertain provisioning journals before retrying. See [architecture](../docs/architecture.md) and [limitations](../docs/limitations.md).
