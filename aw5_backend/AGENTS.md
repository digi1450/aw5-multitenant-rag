# AW5 backend scope

- The root `AGENTS.md` applies. AW5 `tenant_id` identifies one project; Dify's
  internal workspace tenant ID is unrelated.
- Current state and review findings are recorded in
  `docs/architecture/aw5-backend-discord-handoff-2026-09-30.md`. Read it before
  using an older Discord handoff as implementation guidance.
- Run `.venv/bin/python -m unittest tests.test_aw5_backend tests.test_discord_bot`
  for the focused backend/adapter suite. A passing suite is offline evidence.
- Derive project access from the current Discord guild member record and the
  backend's registered role ID on every Start, list, and question. A user ID,
  role name, ticket ID, or client-supplied tenant ID is never sufficient.
- Only this backend may hold Dify app and Knowledge API credentials. Never send
  credentials, retrieved chunks, or Dify graph contents to the Discord bot.
- Read Published dataset IDs through the restricted Dify database view. Do not
  give the bot Docker access or grant the sync reader access to Dify base tables.
- On a changed Published workflow, validate every selected Knowledge Base and
  document's AW5 `tenant_id` before activation. Fail closed on missing metadata,
  API failure, or a mismatch. Do not silently retain a previously authorized
  workflow after Dify publishes a different one.
- Keep any database migrations and service configuration reviewable. Do not
  create external accounts, publish Dify apps, start containers, or expose the
  backend beyond loopback without owner authorization.
