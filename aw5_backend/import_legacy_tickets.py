"""One-time metadata-only migration from the old Discord bot SQLite store."""

import json
import os
from pathlib import Path
import sqlite3
import sys
import urllib.error
import urllib.request


def main() -> None:
    source = Path(os.environ.get("AW5_LEGACY_STATE_DB", "output/discord-bot/aw5.sqlite3"))
    token = os.environ["AW5_BACKEND_ADMIN_TOKEN"]
    url = os.environ.get("AW5_BACKEND_API_URL", "http://127.0.0.1:8765").rstrip("/")
    if not source.is_file() or url != "http://127.0.0.1:8765":
        raise SystemExit("Expected an existing SQLite file and loopback AW5 backend URL")
    with sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True) as db:
        rows = db.execute("""
            SELECT thread_id, guild_id, discord_user_id, tenant_id, dify_conversation_id
            FROM sessions ORDER BY thread_id
        """).fetchall()
    if not rows:
        print("No legacy tickets to import")
        return
    names = ("thread_id", "guild_id", "discord_user_id", "tenant_id", "dify_conversation_id")
    imported = 0
    for index in range(0, len(rows), 100):
        payload = {"tickets": [dict(zip(names, row)) for row in rows[index:index + 100]]}
        request = urllib.request.Request(
            url + "/v1/admin/tickets/import", method="POST",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                imported += json.load(response)["imported"]
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            raise SystemExit(f"Ticket import stopped at batch {index // 100 + 1}: {type(exc).__name__}") from exc
    print(f"Imported {imported} of {len(rows)} legacy ticket records")


if __name__ == "__main__":
    main()
