"""Discord adapter configuration; project records belong to the AW5 backend."""

from dataclasses import dataclass
import os
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class Config:
    discord_token: str
    guild_id: int
    start_channel_id: int
    database_path: Path
    backend_api_url: str
    backend_api_token: str


def _positive_id(value: object, name: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if result <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return result


def load_config(env: dict[str, str] | None = None) -> Config:
    env = os.environ if env is None else env
    token = env.get("AW5_DISCORD_BOT_TOKEN", "").strip()
    api_token = env.get("AW5_BACKEND_BOT_TOKEN", "").strip()
    api_url = env.get("AW5_BACKEND_API_URL", "").strip().rstrip("/")
    if not token or not api_token or not api_url:
        raise ValueError("Discord token and AW5 backend URL/token are required")
    parsed = urlparse(api_url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
        raise ValueError("AW5 backend URL must be an origin without credentials")
    if not (parsed.scheme == "https" and parsed.hostname or
            parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1", "::1", "aw5_api"}):
        raise ValueError("AW5 backend URL must be HTTPS, local loopback HTTP, or Docker service aw5_api")
    return Config(
        discord_token=token,
        guild_id=_positive_id(env.get("AW5_DISCORD_GUILD_ID"), "AW5_DISCORD_GUILD_ID"),
        start_channel_id=_positive_id(env.get("AW5_DISCORD_START_CHANNEL_ID"), "AW5_DISCORD_START_CHANNEL_ID"),
        database_path=Path(env.get("AW5_STATE_DB", "output/discord-bot/aw5.sqlite3")),
        backend_api_url=api_url,
        backend_api_token=api_token,
    )
