# Discord bot scope

- Read `discord_bot/README.md` and
  `docs/architecture/aw5-backend-discord-handoff-2026-09-30.md` for the current
  local adapter flow, owner-reported live observations, and unverified limits.
  The 2026-09-28 handoff describes the historical pre-backend adapter.
- Keep Discord and AW5 backend credentials in local environment variables.
  Never print, commit, or include them in screenshots or test fixtures.
- The bot calls the private AW5 backend API for eligible projects, ticket
  registration, questions, and `/list`. It never reads project JSON, Dify API
  keys, Dify databases, or Docker. The backend fetches current Discord roles
  and derives the authorized AW5 `tenant_id` before Dify access.
- Keep each ticket tied to one Discord user, private thread, and AW5
  `tenant_id`. The backend owns the Dify conversation ID and role checks.
- Run focused unit tests with the project environment:
  `.venv/bin/python -m unittest discover -s tests -p 'test_discord_bot.py'`.
- Do not run the bot against Discord or Dify, install dependencies, or change
  external configuration merely because source code changed. Follow the root
  `AGENTS.md` authorization and evidence rules.
