"""Local operator command for the trusted membership store."""

import argparse
from pathlib import Path

from .store import Store


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision or revoke AW5 Discord demo membership")
    parser.add_argument("action", choices=("add", "revoke"))
    parser.add_argument("--db", type=Path, default=Path("output/discord-bot/aw5.sqlite3"))
    parser.add_argument("--guild-id", type=int, required=True)
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--tenant-id", type=int, required=True)
    args = parser.parse_args()
    if min(args.guild_id, args.user_id, args.tenant_id) <= 0:
        parser.error("IDs must be positive integers")
    Store(args.db).set_membership(args.guild_id, args.user_id, args.tenant_id, args.action == "add")
    print(f"Membership {args.action} recorded for user {args.user_id}, tenant {args.tenant_id}")


if __name__ == "__main__":
    main()
