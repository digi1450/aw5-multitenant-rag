"""Local configuration for the Discord adapter."""

from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Tenant:
    tenant_id: int
    discord_role_id: int
    dify_api_base_url: str
    dify_api_key: str
    tenant_name: str = ""
    dify_knowledge_api_key: str = ""


@dataclass(frozen=True)
class Config:
    discord_token: str
    guild_id: int
    start_channel_id: int
    database_path: Path
    tenants: dict[int, Tenant]


def _positive_id(value: object, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if result <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return result


def _safe_api_base(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("dify_api_base_url must be a URL")
    url = value.rstrip("/")
    parsed = urlparse(url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Dify API URL must not contain credentials, query, or fragment")
    if parsed.scheme == "https" and parsed.hostname:
        return url
    if parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        return url
    raise ValueError("Dify API URL must use HTTPS or local loopback HTTP")


def load_config(env: dict[str, str] | None = None) -> Config:
    env = os.environ if env is None else env
    token = env.get("AW5_DISCORD_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("AW5_DISCORD_BOT_TOKEN is required")
    config_file = env.get("AW5_TENANTS_FILE", "").strip()
    if not config_file:
        raise ValueError("AW5_TENANTS_FILE is required")
    data = json.loads(Path(config_file).read_text(encoding="utf-8"))
    entries = data.get("tenants") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("tenant configuration must contain a nonempty tenants list")
    tenants: dict[int, Tenant] = {}
    role_ids: set[int] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each tenant must be an object")
        tenant_id = _positive_id(entry.get("tenant_id"), "tenant_id")
        role_id = _positive_id(entry.get("discord_role_id"), "discord_role_id")
        tenant_name = entry.get("tenant_name", "")
        if not isinstance(tenant_name, str) or len(tenant_name) > 70 or ("tenant_name" in entry and not tenant_name.strip()):
            raise ValueError("tenant_name must be a nonempty string of at most 70 characters")
        key_name = entry.get("dify_api_key_env")
        if not isinstance(key_name, str) or not key_name.startswith("AW5_DIFY_API_KEY_"):
            raise ValueError("dify_api_key_env must name an AW5_DIFY_API_KEY_* variable")
        key = env.get(key_name, "").strip()
        if not key:
            raise ValueError(f"{key_name} is required")
        if tenant_id in tenants or role_id in role_ids:
            raise ValueError("tenant IDs and Discord role IDs must be unique")
        knowledge_key_name = entry.get("dify_knowledge_api_key_env", f"AW5_DIFY_KNOWLEDGE_API_KEY_{tenant_id}")
        if not isinstance(knowledge_key_name, str) or not knowledge_key_name.startswith("AW5_DIFY_KNOWLEDGE_API_KEY_"):
            raise ValueError("dify_knowledge_api_key_env must name an AW5_DIFY_KNOWLEDGE_API_KEY_* variable")
        tenants[tenant_id] = Tenant(
            tenant_id=tenant_id,
            discord_role_id=role_id,
            dify_api_base_url=_safe_api_base(entry.get("dify_api_base_url")),
            dify_api_key=key,
            tenant_name=tenant_name.strip(),
            dify_knowledge_api_key=env.get(knowledge_key_name, "").strip(),
        )
        role_ids.add(role_id)
    return Config(
        discord_token=token,
        guild_id=_positive_id(env.get("AW5_DISCORD_GUILD_ID"), "AW5_DISCORD_GUILD_ID"),
        start_channel_id=_positive_id(env.get("AW5_DISCORD_START_CHANNEL_ID"), "AW5_DISCORD_START_CHANNEL_ID"),
        database_path=Path(env.get("AW5_STATE_DB") or env.get("AW5_MEMBERSHIP_DB", "output/discord-bot/aw5.sqlite3")),
        tenants=tenants,
    )
