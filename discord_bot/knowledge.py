"""Read-only Dify Knowledge inventory for a trusted AW5 project tenant."""

from dataclasses import dataclass
import json
import urllib.error
import urllib.request
from uuid import UUID

from .config import Tenant


class KnowledgeError(Exception):
    pass


@dataclass(frozen=True)
class KnowledgeFile:
    name: str
    dataset_name: str
    status: str


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _get_page(tenant: Tenant, path: str, page: int, timeout: float) -> dict:
    request = urllib.request.Request(
        f"{tenant.dify_api_base_url}{path}?page={page}&limit=100",
        headers={"Authorization": f"Bearer {tenant.dify_knowledge_api_key}"},
        method="GET",
    )
    try:
        with urllib.request.build_opener(_NoRedirect).open(request, timeout=timeout) as response:
            raw = response.read(2_000_001)
    except urllib.error.HTTPError as exc:
        raise KnowledgeError(f"Knowledge API returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise KnowledgeError("Knowledge API is unavailable") from exc
    if len(raw) > 2_000_000:
        raise KnowledgeError("Knowledge API response is too large")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError) as exc:
        raise KnowledgeError("Knowledge API response is invalid") from exc
    if (
        not isinstance(result, dict)
        or not isinstance(result.get("data"), list)
        or not isinstance(result.get("has_more"), bool)
    ):
        raise KnowledgeError("Knowledge API page is invalid")
    return result


def _pages(tenant: Tenant, path: str, timeout: float):
    # A malformed API must fail rather than returning a partial list forever.
    for page in range(1, 1001):
        result = _get_page(tenant, path, page, timeout)
        yield from result["data"]
        if not result["has_more"]:
            return
    raise KnowledgeError("Knowledge API pagination did not finish")


def _project_metadata(document: dict) -> str | None:
    metadata = document.get("doc_metadata")
    if isinstance(metadata, dict):
        value = metadata.get("tenant_id")
        return str(value) if isinstance(value, (str, int)) and not isinstance(value, bool) else None
    if isinstance(metadata, list):
        for item in metadata:
            if isinstance(item, dict) and item.get("name") == "tenant_id":
                value = item.get("value")
                return str(value) if isinstance(value, (str, int)) and not isinstance(value, bool) else None
    return None


def list_project_files(tenant: Tenant, timeout: float = 15.0) -> list[KnowledgeFile]:
    """List every document explicitly tagged with the authorized AW5 tenant ID.

    Dify's API key is workspace-scoped; metadata is a filter, not a security
    boundary. The caller must first authorize the Discord ticket and role.
    """
    if not tenant.dify_knowledge_api_key:
        raise KnowledgeError("Knowledge API key is not configured")
    files: list[KnowledgeFile] = []
    for dataset in _pages(tenant, "/datasets", timeout):
        if not isinstance(dataset, dict):
            raise KnowledgeError("Knowledge API dataset is invalid")
        try:
            dataset_id = str(UUID(dataset["id"]))
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise KnowledgeError("Knowledge API dataset ID is invalid") from exc
        dataset_name = dataset.get("name")
        if not isinstance(dataset_name, str):
            raise KnowledgeError("Knowledge API dataset name is invalid")
        for document in _pages(tenant, f"/datasets/{dataset_id}/documents", timeout):
            if not isinstance(document, dict):
                raise KnowledgeError("Knowledge API document is invalid")
            if _project_metadata(document) != str(tenant.tenant_id):
                continue
            name = document.get("name")
            if not isinstance(name, str) or not name.strip():
                raise KnowledgeError("Knowledge API document name is invalid")
            if document.get("archived") is True:
                status = "archived"
            elif document.get("enabled") is False:
                status = "disabled"
            elif document.get("enabled") is True and document.get("archived") is False and document.get("indexing_status") == "completed":
                status = "available"
            else:
                status = "indexing"
            files.append(KnowledgeFile(name, dataset_name, status))
    return sorted(files, key=lambda item: (item.name.casefold(), item.dataset_name.casefold()))
