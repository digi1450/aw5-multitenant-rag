# AW5 backend scope

- The root `AGENTS.md` applies. AW5 `tenant_id` identifies one project; Dify's
  internal workspace tenant ID is unrelated.
- Latest owner-confirmed tenant/onboarding contract and prepared Registry change:
  `docs/architecture/tenant-registry-contract-2026-10-03.md`. Admin-selected IDs
  and the local provisioning portal are implemented; read
  `docs/architecture/admin-onboarding-2026-10-03.md` for its trust boundary. The owner installed/tested and Published v3.2;
  tenant 1 was rebound and backend Registry code loaded. Read
  `dify/exports/aw5-rag-test4-7-v3-2-owner-supplied-2026-10-03.md` for bounded Draft
  evidence and deployment checks. The owner reported a Discord answer after installing the strict seek guard;
  this is an observation, not isolation proof. The portal now implements Discord
  role changes and AW5 registration deletion, but not arbitrary Dify app/key
  rebinding or automatic orphan repair. Read
  `docs/architecture/progress-2026-10-15.md` for the current source/offline checkpoint.
- Current state and review findings are recorded in
  `docs/architecture/aw5-backend-discord-handoff-2026-09-30.md`. Read it before
  using an older Discord handoff as implementation guidance.
- Run `.venv/bin/python -m unittest tests.test_aw5_backend tests.test_discord_bot tests.test_backend_source_registry tests.test_admin_onboarding`
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

- `/aw5-admin` issues an ephemeral, one-use capability only in the configured
  admin channel after a fresh role lookup. Portal mutations require same-origin
  requests, the HttpOnly session cookie and CSRF token; recheck admin membership.
- Reserve onboarding before external role creation. App registration and journal
  completion commit together. Do not blindly retry or delete an incomplete
  journal record: verify the external role and project first. No new Dify app
  or live workflow is created or Published by this portal.
