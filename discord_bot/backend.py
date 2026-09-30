"""Private AW5 backend API client. No Dify or Docker access belongs here."""

from dataclasses import dataclass
import json
import urllib.error
import urllib.parse
import urllib.request

from .config import Config


class BackendDenied(Exception):
    pass


class BackendUnavailable(Exception):
    pass


class BackendRouteMissing(BackendUnavailable):
    pass


@dataclass(frozen=True)
class Project:
    tenant_id: int
    tenant_name: str


@dataclass(frozen=True)
class File:
    name: str
    dataset_name: str
    status: str


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


class BackendClient:
    def __init__(self, config: Config):
        self.url = config.backend_api_url
        self.token = config.backend_api_token
        self.opener = urllib.request.build_opener(_NoRedirect)

    def _request(self, method: str, path: str, *, query: dict | None = None,
                 data: dict | None = None, timeout: float = 20.0) -> dict:
        url = self.url + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            method=method,
        )
        try:
            with self.opener.open(request, timeout=timeout) as response:
                raw = response.read(2_000_001)
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                raise BackendDenied("Project access denied") from exc
            if exc.code == 404:
                raise BackendRouteMissing("AW5 backend API route not found") from exc
            raise BackendUnavailable(f"AW5 backend returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise BackendUnavailable("AW5 backend is unavailable") from exc
        if len(raw) > 2_000_000:
            raise BackendUnavailable("AW5 backend response is too large")
        try:
            result = json.loads(raw)
        except ValueError as exc:
            raise BackendUnavailable("AW5 backend response is invalid") from exc
        if not isinstance(result, dict):
            raise BackendUnavailable("AW5 backend response is invalid")
        return result

    def eligible_projects(self, guild_id: int, user_id: int) -> list[Project]:
        result = self._request("GET", "/v1/projects/eligible",
                               query={"guild_id": guild_id, "user_id": user_id})
        values = result.get("projects")
        if not isinstance(values, list):
            raise BackendUnavailable("AW5 project list is invalid")
        try:
            return [Project(int(item["tenant_id"]), str(item["tenant_name"])) for item in values]
        except (TypeError, ValueError, KeyError) as exc:
            raise BackendUnavailable("AW5 project list is invalid") from exc

    def create_ticket(self, guild_id: int, user_id: int, thread_id: int, tenant_id: int) -> None:
        self._request("POST", "/v1/tickets", data={"guild_id": guild_id, "user_id": user_id,
                                                   "thread_id": thread_id, "tenant_id": tenant_id})

    def files(self, thread_id: int, guild_id: int, user_id: int) -> tuple[list[File], int | None]:
        result = self._request("GET", f"/v1/tickets/{thread_id}/files",
                               query={"guild_id": guild_id, "user_id": user_id})
        values = result.get("files")
        if not isinstance(values, list):
            raise BackendUnavailable("AW5 file list is invalid")
        try:
            files = [File(item["name"], item["dataset_name"], item["status"]) for item in values]
        except (TypeError, KeyError) as exc:
            raise BackendUnavailable("AW5 file list is invalid") from exc
        return files, result.get("tenant_id")

    def ask(self, thread_id: int, guild_id: int, user_id: int, question: str) -> str:
        result = self._request("POST", f"/v1/tickets/{thread_id}/ask",
                               data={"guild_id": guild_id, "user_id": user_id, "question": question},
                               timeout=45)
        answer = result.get("answer")
        if not isinstance(answer, str) or not answer:
            raise BackendUnavailable("AW5 answer is invalid")
        return answer

    def close_ticket(self, thread_id: int, guild_id: int, user_id: int) -> bool:
        result = self._request("POST", f"/v1/tickets/{thread_id}/close",
                               data={"guild_id": guild_id, "user_id": user_id})
        closed = result.get("closed")
        if type(closed) is not bool:
            raise BackendUnavailable("AW5 close result is invalid")
        return closed
