"""HTTP clients used only by the trusted AW5 backend."""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from uuid import UUID

import aiohttp

LOG = logging.getLogger(__name__)


class IntegrationError(Exception):
    pass


@asynccontextmanager
async def _client_session(shared: aiohttp.ClientSession | None):
    if shared is not None:
        yield shared
    else:
        async with aiohttp.ClientSession() as session:
            yield session


def _metadata_tenant(document: dict) -> str | None:
    metadata = document.get("doc_metadata")
    if isinstance(metadata, dict):
        value = metadata.get("tenant_id")
        return str(value) if type(value) in (str, int) else None
    if isinstance(metadata, list):
        for item in metadata:
            if isinstance(item, dict) and item.get("name") == "tenant_id":
                value = item.get("value")
                return str(value) if type(value) in (str, int) else None
    return None


class DiscordAccess:
    def __init__(self, token: str, session: aiohttp.ClientSession | None = None):
        self.token = token
        self.session = session

    async def member_roles(self, guild_id: int, user_id: int) -> set[int]:
        url = f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}"
        try:
            async with _client_session(self.session) as session:
                async with session.get(url, headers={"Authorization": f"Bot {self.token}"},
                                       timeout=aiohttp.ClientTimeout(total=8)) as response:
                    if response.status == 404:
                        return set()
                    if response.status != 200:
                        raise IntegrationError("Discord member lookup failed")
                    payload = await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            raise IntegrationError("Discord member lookup unavailable") from exc
        values = payload.get("roles") if isinstance(payload, dict) else None
        if not isinstance(values, list):
            raise IntegrationError("Discord member roles are invalid")
        try:
            return {int(value) for value in values}
        except (TypeError, ValueError) as exc:
            raise IntegrationError("Discord member roles are invalid") from exc

    async def role_exists(self, guild_id: int, role_id: int) -> bool:
        url = f"https://discord.com/api/v10/guilds/{guild_id}/roles"
        try:
            async with _client_session(self.session) as session:
                async with session.get(url, headers={"Authorization": f"Bot {self.token}"},
                                       timeout=aiohttp.ClientTimeout(total=8)) as response:
                    if response.status != 200:
                        raise IntegrationError("Discord role lookup failed")
                    roles = await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            raise IntegrationError("Discord role lookup unavailable") from exc
        return isinstance(roles, list) and any(isinstance(role, dict) and role.get("id") == str(role_id) for role in roles)


class DifyAccess:
    def __init__(self, base_url: str, knowledge_key: str,
                 session: aiohttp.ClientSession | None = None):
        self.base_url = base_url.rstrip("/")
        self.knowledge_key = knowledge_key
        self.session = session

    async def _json(self, method: str, path: str, key: str, *, params: dict | None = None,
                    payload: dict | None = None, timeout: float = 15.0) -> dict:
        headers = {"Authorization": f"Bearer {key}"}
        try:
            async with _client_session(self.session) as session:
                async with session.request(method, self.base_url + path, headers=headers,
                                           params=params, json=payload, allow_redirects=False,
                                           timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status != 200:
                        raise IntegrationError(f"Dify API returned HTTP {response.status}")
                    if response.content_length is not None and response.content_length > 2_000_000:
                        raise IntegrationError("Dify API response is too large")
                    chunks = []
                    size = 0
                    async for chunk in response.content.iter_chunked(64 * 1024):
                        size += len(chunk)
                        if size > 2_000_000:
                            raise IntegrationError("Dify API response is too large")
                        chunks.append(chunk)
                    raw = b"".join(chunks)
                    content_type = response.headers.get("Content-Type", "")
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise IntegrationError("Dify API unavailable") from exc
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            LOG.warning("Dify %s response was invalid JSON: bytes=%s content_type=%s first_byte=%s last_byte=%s parse_error=%s",
                        path, len(raw), content_type.split(";", 1)[0], raw[:1].hex(), raw[-1:].hex(), exc)
            raise IntegrationError("Dify API response is invalid") from exc
        if not isinstance(data, dict):
            raise IntegrationError("Dify API response is invalid")
        return data

    async def _pages(self, path: str):
        for page in range(1, 1001):
            data = await self._json("GET", path, self.knowledge_key,
                                    params={"page": page, "limit": 100})
            if not isinstance(data.get("data"), list) or not isinstance(data.get("has_more"), bool):
                raise IntegrationError("Dify Knowledge page is invalid")
            for value in data["data"]:
                if not isinstance(value, dict):
                    raise IntegrationError("Dify Knowledge item is invalid")
                yield value
            if not data["has_more"]:
                return
        raise IntegrationError("Dify Knowledge pagination did not finish")

    async def project_files(self, tenant_id: int, dataset_ids: set[str]) -> list[dict]:
        """Fail closed if a selected base or any document lacks exact project metadata."""
        datasets: dict[str, str] = {}
        async for dataset in self._pages("/datasets"):
            try:
                dataset_id = str(UUID(dataset["id"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise IntegrationError("Dify Knowledge Base ID is invalid") from exc
            if dataset_id in dataset_ids:
                name = dataset.get("name")
                if not isinstance(name, str):
                    raise IntegrationError("Dify Knowledge Base name is invalid")
                datasets[dataset_id] = name
        if set(datasets) != dataset_ids:
            raise IntegrationError("A Published Knowledge Base is unavailable")
        limit = asyncio.Semaphore(4)

        async def checked_files(dataset_id: str, dataset_name: str) -> list[dict]:
            async with limit:
                result: list[dict] = []
                async for document in self._pages(f"/datasets/{dataset_id}/documents"):
                    if _metadata_tenant(document) != str(tenant_id):
                        raise IntegrationError("Document tenant metadata is missing or mismatched")
                    name = document.get("name")
                    if not isinstance(name, str) or not name.strip():
                        raise IntegrationError("Dify document name is invalid")
                    if document.get("archived") is True:
                        status = "archived"
                    elif document.get("enabled") is False:
                        status = "disabled"
                    elif (document.get("enabled") is True and document.get("archived") is False
                          and document.get("indexing_status") == "completed"):
                        status = "available"
                    else:
                        status = "indexing"
                    result.append({"name": name, "dataset_name": dataset_name, "status": status})
                return result

        batches = await asyncio.gather(*(checked_files(dataset_id, dataset_name)
                                         for dataset_id, dataset_name in datasets.items()),
                                       return_exceptions=True)
        for batch in batches:
            if isinstance(batch, BaseException):
                raise batch
        files = [file for batch in batches for file in batch]
        return sorted(files, key=lambda value: (value["name"].casefold(), value["dataset_name"].casefold()))

    async def ask(self, app_key: str, *, question: str, user_key: str,
                  conversation_id: str | None) -> tuple[str, str]:
        request: dict[str, object] = {
            "inputs": {}, "query": question, "response_mode": "blocking", "user": user_key,
        }
        if conversation_id:
            request["conversation_id"] = conversation_id
        data = await self._json("POST", "/chat-messages", app_key, payload=request, timeout=35)
        answer, new_id = data.get("answer"), data.get("conversation_id")
        if not isinstance(answer, str) or not answer.strip() or not isinstance(new_id, str) or not new_id:
            raise IntegrationError("Dify returned no valid answer or conversation ID")
        return answer, new_id
