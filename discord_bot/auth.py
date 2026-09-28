"""Fail-closed membership checks, independent of the Discord adapter."""

from .config import Config, Tenant
from .store import Session, Store


class AccessDenied(Exception):
    pass


def authorized_tenants(config: Config, store: Store, guild_id: int, user_id: int, role_ids: set[int]) -> list[Tenant]:
    if guild_id != config.guild_id:
        raise AccessDenied("This server is not configured for AW5")
    return [
        config.tenants[tenant_id]
        for tenant_id in store.active_tenants(guild_id, user_id)
        if tenant_id in config.tenants and config.tenants[tenant_id].discord_role_id in role_ids
    ]


def authorize_start(config: Config, store: Store, guild_id: int, user_id: int, role_ids: set[int]) -> Tenant:
    matches = authorized_tenants(config, store, guild_id, user_id, role_ids)
    if len(matches) != 1:
        raise AccessDenied("Project membership is missing or ambiguous")
    return matches[0]


def authorize_session(
    config: Config, store: Store, guild_id: int, user_id: int, role_ids: set[int], thread_id: int
) -> tuple[Tenant, Session]:
    session = store.get_session(thread_id)
    if session is None or session.guild_id != guild_id or session.discord_user_id != user_id:
        raise AccessDenied("This ticket is not assigned to you")
    tenant = config.tenants.get(session.tenant_id)
    if tenant is None or guild_id != config.guild_id:
        raise AccessDenied("Project configuration is unavailable")
    if session.tenant_id not in store.active_tenants(guild_id, user_id):
        raise AccessDenied("Project membership has been revoked")
    if tenant.discord_role_id not in role_ids:
        raise AccessDenied("Required Discord role is missing")
    return tenant, session
