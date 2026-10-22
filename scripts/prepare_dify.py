"""Prepare a fresh pinned Dify checkout; never start containers or overwrite config."""

import argparse
import base64
import json
from pathlib import Path
import secrets
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def replace_env(template: str, values: dict[str, str]) -> str:
    remaining = dict(values)
    lines = []
    for line in template.splitlines():
        key = line.split("=", 1)[0]
        if not line.lstrip().startswith("#") and "=" in line and key in remaining:
            line = key + "=" + remaining.pop(key)
        lines.append(line)
    lines.extend(key + "=" + value for key, value in remaining.items())
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "output/vendor/dify")
    args = parser.parse_args()
    pin = json.loads((ROOT / "deploy/dify/version.json").read_text())
    target = args.source_dir.resolve()
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", "--branch", pin["tag"],
                        pin["repository"], str(target)], check=True)
    if not (target / ".git").is_dir():
        raise SystemExit("Target is not a Git checkout; choose a new source directory")
    if run("git", "-C", str(target), "rev-parse", "HEAD") != pin["commit"]:
        raise SystemExit("Dify commit does not match the pin; existing checkout was not changed")
    if run("git", "-C", str(target), "status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Dify has tracked local edits; choose a fresh directory")
    docker = target / "docker"
    env_path = docker / ".env"
    override = docker / "docker-compose.override.yaml"
    if env_path.exists() or override.exists():
        raise SystemExit("Existing Dify configuration was preserved; choose a fresh directory")

    values = {key: secrets.token_hex(32) for key in (
        "SECRET_KEY", "DB_PASSWORD", "REDIS_PASSWORD", "SANDBOX_API_KEY",
        "PLUGIN_DAEMON_KEY", "PLUGIN_DIFY_INNER_API_KEY", "INNER_API_KEY",
        "DIFY_AGENT_API_TOKEN",
    )}
    vector_key = secrets.token_hex(32)
    values.update({
        "COMPOSE_PROJECT_NAME": pin["compose_project"],
        "TRIGGER_URL": "http://localhost:8080",
        "NEXT_PUBLIC_SOCKET_URL": "ws://localhost:8080",
        "WEAVIATE_API_KEY": vector_key,
        "WEAVIATE_AUTHENTICATION_APIKEY_ALLOWED_KEYS": vector_key,
        "WEAVIATE_AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED": "false",
        "WEAVIATE_DISABLE_TELEMETRY": "true",
        "DIFY_AGENT_SERVER_SECRET_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("="),
    })
    with env_path.open("x", encoding="utf-8") as stream:
        env_path.chmod(0o600)
        stream.write(replace_env((docker / ".env.example").read_text(), values))
    shutil.copyfile(ROOT / "deploy/dify/compose.override.yml", override)
    print("Prepared Dify", pin["tag"], "at", target)
    print("Configuration is local. No containers were started and no model calls were made.")
    print("Next: cd", docker)
    print("Then: docker compose -p", pin["compose_project"], "up -d")


if __name__ == "__main__":
    main()
