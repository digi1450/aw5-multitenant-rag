"""Paste into the replacement GET FILE REGISTRY Code node.

Input: registry_json <- User Input.aw5_registry_json (required paragraph).
Output: json (Array[Object]), preserving the Database Client wrapper.
Parsing a payload does not authenticate its sender. AW5 owns authorization;
direct Dify entry must be controlled separately before an isolation claim.
"""

import json
import re


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate registry field")
        result[key] = value
    return result


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", value
    ):
        raise ValueError("Invalid registry identifier")
    return value.lower()


def main(registry_json: str) -> dict:
    if not isinstance(registry_json, str) or len(registry_json.encode()) > 65_536:
        raise ValueError("Registry input is missing or too large")
    payload = json.loads(registry_json, object_pairs_hook=_unique_object)
    if not isinstance(payload, dict) or payload.get("schema_version") != "aw5.source-registry.v1":
        raise ValueError("Unsupported registry schema")
    tenant = payload.get("tenant_id")
    if type(tenant) is not int or tenant <= 0:
        raise ValueError("Invalid registry tenant")
    _identifier(payload.get("published_workflow_id"))
    values = payload.get("dataset_ids")
    if not isinstance(values, list) or not values:
        raise ValueError("Registry dataset selection is missing")
    datasets = {_identifier(value) for value in values}
    if len(datasets) != len(values):
        raise ValueError("Duplicate registry dataset")
    documents = payload.get("documents")
    if not isinstance(documents, list) or len(documents) > 20:
        raise ValueError("Invalid registry shortlist")
    rows = []
    seen = set()
    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("Invalid registry document")
        document_id = _identifier(document.get("document_id"))
        if document_id in seen or _identifier(document.get("dataset_id")) not in datasets:
            raise ValueError("Registry document is duplicated or outside selection")
        seen.add(document_id)
        name, kind = document.get("document_name"), document.get("document_type")
        if not isinstance(name, str) or not name.strip() or (kind is not None and not isinstance(kind, str)):
            raise ValueError("Invalid registry document metadata")
        rows.append({"document_id": document_id, "document_name": name, "document_type": kind})
    return {"json": [{"data": rows}]}
