"""Build a query shortlist only from a freshly authorized project inventory."""

import json
import re
from uuid import UUID


REGISTRY_INPUT = "aw5_registry_json"
SCHEMA_VERSION = "aw5.source-registry.v1"
MAX_REGISTRY_BYTES = 65_536
SHORTLIST_LIMIT = 20


def _identifier(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid registry identifier")
    return str(UUID(value))


def registry_payload(*, tenant_id: int, workflow_id: str,
                     dataset_ids: frozenset[str], files: tuple[dict, ...],
                     question: str) -> str:
    """No membership inference, metadata relabeling, or outside-scope lookup.

    The caller must authorize the ticket and scan all selected documents first.
    Scores retain the old Registry's filename/type/token weights. Python's
    Unicode tokenization/collation is not claimed identical to PostgreSQL.
    """
    if type(tenant_id) is not int or tenant_id <= 0:
        raise ValueError("Invalid registry tenant")
    workflow_id = _identifier(workflow_id)
    datasets = {_identifier(value) for value in dataset_ids}
    if not datasets or not isinstance(question, str) or not question.strip():
        raise ValueError("Registry scope or question is absent")
    query = question.lower()
    query_terms = set(re.split(r"[^\w]+|_+", query))
    scored = []
    seen = set()
    for file in files:
        if type(file.get("tenant_id")) is not int or file["tenant_id"] != tenant_id:
            raise ValueError("Registry inventory tenant mismatch")
        dataset_id = _identifier(file.get("dataset_id"))
        document_id = _identifier(file.get("document_id"))
        if dataset_id not in datasets or document_id in seen:
            raise ValueError("Registry inventory scope or identity mismatch")
        seen.add(document_id)
        name, kind = file.get("name"), file.get("document_type")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid registry document name")
        if kind is not None and not isinstance(kind, str):
            raise ValueError("Invalid registry document type")
        if file.get("status") != "available":
            continue
        name_terms = {term for term in re.split(r"[^\w]+|_+", re.sub(r"\.[^.]+$", "", name.lower()))
                      if len(term) >= 3}
        score = (100 if name.lower() in query else 0)
        score += 50 if kind is not None and kind.lower() in query_terms else 0
        score += 10 * len(name_terms & query_terms)
        if score:
            scored.append((score, name, document_id, {
                "document_id": document_id, "document_name": name,
                "document_type": kind, "dataset_id": dataset_id,
            }))
    scored.sort(key=lambda item: (-item[0], item[1], item[2]))
    payload = json.dumps({
        "schema_version": SCHEMA_VERSION, "tenant_id": tenant_id,
        "published_workflow_id": workflow_id, "dataset_ids": sorted(datasets),
        "documents": [item[3] for item in scored[:SHORTLIST_LIMIT]],
    }, ensure_ascii=False, separators=(",", ":"))
    if len(payload.encode()) > MAX_REGISTRY_BYTES:
        raise ValueError("Registry payload exceeds supported size")
    return payload
