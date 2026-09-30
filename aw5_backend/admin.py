"""Local project administration without putting Dify keys in shell history."""

import argparse
import getpass
import json
import os
import urllib.error
import urllib.request


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ.get("AW5_BACKEND_ADMIN_TOKEN", "")
    if not token:
        raise SystemExit("AW5_BACKEND_ADMIN_TOKEN is required")
    base = os.environ.get("AW5_BACKEND_API_URL", "http://127.0.0.1:8765").rstrip("/")
    if base != "http://127.0.0.1:8765":
        raise SystemExit("Admin CLI requires the loopback AW5 backend URL")
    request = urllib.request.Request(
        base + path,
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"AW5 backend returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit("AW5 backend is unavailable") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage AW5 project registrations")
    subcommands = parser.add_subparsers(dest="command", required=True)
    register = subcommands.add_parser("register", help="register a project once")
    register.add_argument("--name", required=True)
    register.add_argument("--discord-role-id", type=int, required=True)
    register.add_argument("--dify-app-id", required=True)
    subcommands.add_parser("status", help="show project sync status")
    args = parser.parse_args()
    if args.command == "register":
        key = getpass.getpass("Dify Chatflow API key (hidden): ")
        result = _request("POST", "/v1/admin/projects", {
            "tenant_name": args.name,
            "discord_role_id": args.discord_role_id,
            "dify_app_id": args.dify_app_id,
            "dify_app_api_key": key,
        })
    else:
        result = _request("GET", "/v1/admin/projects")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
