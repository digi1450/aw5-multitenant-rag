"""One-time local setup for the narrow Dify reader and AW5 service secrets."""

from pathlib import Path
import os
import secrets
import subprocess
from urllib.parse import quote

from cryptography.fernet import Fernet


ROOT = Path(__file__).resolve().parent.parent


def _read_env(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def main() -> None:
    backend_env = ROOT / "aw5_backend/.env"
    bot_env = ROOT / "discord_bot/.env"
    if backend_env.exists():
        raise SystemExit("Backend environment already exists; bootstrap will not overwrite it")
    if not bot_env.is_file():
        raise SystemExit("Existing Discord bot environment is missing")
    existing = _read_env(bot_env)
    required = ("AW5_DISCORD_BOT_TOKEN", "AW5_DISCORD_GUILD_ID",
                "AW5_DIFY_KNOWLEDGE_API_KEY_1")
    if any(not existing.get(key) for key in required):
        raise SystemExit("Discord bot environment lacks a required token, guild ID, or Knowledge API key")

    role_password = secrets.token_hex(24)
    db_password = secrets.token_hex(24)
    bot_api_token = secrets.token_hex(32)
    admin_api_token = secrets.token_hex(32)
    reader_url = f"postgresql://aw5_sync_reader:{quote(role_password)}@db_postgres:5432/dify"
    view = (ROOT / "aw5_backend/dify_read_view.sql").read_text(encoding="utf-8")
    role_check = subprocess.run(
        ["docker", "exec", "aw5-dify-db_postgres-1", "psql", "-X", "-Atq",
         "-U", "postgres", "-d", "dify", "-c",
         "SELECT count(*) FROM pg_roles WHERE rolname = 'aw5_sync_reader'"],
        capture_output=True, text=True, check=False,
    )
    if role_check.returncode or role_check.stdout.strip() not in ("0", "1"):
        raise SystemExit("Cannot inspect Dify reader role")
    role_verb = "ALTER" if role_check.stdout.strip() == "1" else "CREATE"
    sql = ("BEGIN;\n" + view + "\n"
           f"{role_verb} ROLE aw5_sync_reader LOGIN PASSWORD '{role_password}';\n"
           "GRANT USAGE ON SCHEMA public TO aw5_sync_reader;\n"
           "GRANT SELECT ON aw5_published_retrieval_v1 TO aw5_sync_reader;\n"
           "COMMIT;\n")
    result = subprocess.run(
        ["docker", "exec", "-i", "aw5-dify-db_postgres-1", "psql", "-X", "-q",
         "-v", "ON_ERROR_STOP=1", "-U", "postgres", "-d", "dify"],
        input=sql, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise SystemExit("Dify read-view setup failed; transaction rolled back. Check role/view permissions")

    entries = {
        "AW5_POSTGRES_PASSWORD": db_password,
        "AW5_DIFY_READ_URL": reader_url,
        "AW5_DISCORD_BOT_TOKEN": existing["AW5_DISCORD_BOT_TOKEN"],
        "AW5_BACKEND_BOT_TOKEN": bot_api_token,
        "AW5_BACKEND_ADMIN_TOKEN": admin_api_token,
        "AW5_BACKEND_ENCRYPTION_KEY": Fernet.generate_key().decode(),
        "AW5_DIFY_KNOWLEDGE_API_BASE_URL": "http://api:5001/v1",
        "AW5_DIFY_KNOWLEDGE_API_KEY": existing["AW5_DIFY_KNOWLEDGE_API_KEY_1"],
        "AW5_DISCORD_GUILD_ID": existing["AW5_DISCORD_GUILD_ID"],
    }
    descriptor = open(backend_env, "x", encoding="utf-8", opener=lambda path, flags: os.open(path, flags, 0o600))
    with descriptor:
        descriptor.writelines(f"{key}={value}\n" for key, value in entries.items())
    print("Created restricted Dify reader and private AW5 backend environment")


if __name__ == "__main__":
    main()
