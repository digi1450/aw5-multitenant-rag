"""Environment-only service configuration; project records live in PostgreSQL."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    dify_read_url: str
    discord_bot_token: str
    bot_api_token: str
    admin_api_token: str
    encryption_key: str
    knowledge_api_base_url: str
    knowledge_api_key: str
    guild_id: int

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Settings":
        env = dict(os.environ if env is None else env)
        names = (
            "AW5_DATABASE_URL", "AW5_DIFY_READ_URL", "AW5_DISCORD_BOT_TOKEN",
            "AW5_BACKEND_BOT_TOKEN", "AW5_BACKEND_ADMIN_TOKEN",
            "AW5_BACKEND_ENCRYPTION_KEY", "AW5_DIFY_KNOWLEDGE_API_BASE_URL",
            "AW5_DIFY_KNOWLEDGE_API_KEY", "AW5_DISCORD_GUILD_ID",
        )
        missing = [name for name in names if not env.get(name, "").strip()]
        if missing:
            raise ValueError("Missing backend configuration: " + ", ".join(missing))
        guild_id = int(env["AW5_DISCORD_GUILD_ID"])
        if guild_id <= 0:
            raise ValueError("AW5_DISCORD_GUILD_ID must be positive")
        return cls(
            database_url=env["AW5_DATABASE_URL"],
            dify_read_url=env["AW5_DIFY_READ_URL"],
            discord_bot_token=env["AW5_DISCORD_BOT_TOKEN"],
            bot_api_token=env["AW5_BACKEND_BOT_TOKEN"],
            admin_api_token=env["AW5_BACKEND_ADMIN_TOKEN"],
            encryption_key=env["AW5_BACKEND_ENCRYPTION_KEY"],
            knowledge_api_base_url=env["AW5_DIFY_KNOWLEDGE_API_BASE_URL"].rstrip("/"),
            knowledge_api_key=env["AW5_DIFY_KNOWLEDGE_API_KEY"],
            guild_id=guild_id,
        )
