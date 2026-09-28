# Discord bot scope

- Read `discord_bot/README.md` and the dated
  `docs/architecture/discord-bot-demo-handoff-2026-09-28.md` for the current
  local adapter flow, owner-reported live observations, and unverified limits.
- Keep Discord and Dify credentials in local environment variables. Never print,
  commit, or include them in screenshots or test fixtures.
- The local membership store and a current Discord role must both authorize a
  user. A thread ID, Discord message, or slash-command argument never grants an
  AW5 project tenant.
- Keep each Dify conversation tied to one Discord user, private thread, and AW5
  `tenant_id`. Deny absent or revoked membership before contacting Dify.
- Run focused unit tests with the project environment:
  `.venv/bin/python -m unittest discover -s tests -p 'test_discord_bot.py'`.
- Do not run the bot against Discord or Dify, install dependencies, or change
  external configuration merely because source code changed. Follow the root
  `AGENTS.md` authorization and evidence rules.
