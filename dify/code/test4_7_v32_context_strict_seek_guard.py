import json

MAX_CONTEXT_CHUNKS = 15

def _registry_document_ids(source_registry: list) -> dict:
    if not isinstance(source_registry, list):
        raise ValueError("source_registry must be an array")

    by_name = {}
    for entry in source_registry:
        if not isinstance(entry, dict):
            raise ValueError("source_registry entries must be objects")
        rows = entry.get("data", [entry])
        if not isinstance(rows, list):
            raise ValueError("source_registry data must be an array")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("source_registry rows must be objects")
            name = row.get("document_name")
            document_id = row.get("document_id")
            if (
                isinstance(name, str)
                and name
                and isinstance(document_id, str)
                and document_id.strip()
            ):
                by_name.setdefault(name, set()).add(document_id)
    return by_name


def _finish(entries: list, report: dict) -> dict:
    enriched_results = []
    for entry in entries:
        source = {}
        for key in ("document_id", "document_name", "dataset_id", "dataset_name"):
            value = entry["metadata"].get(key)
            if isinstance(value, str) and value.strip():
                source[key] = value.strip()

        enriched_item = dict(entry["item"])
        enriched_item["content"] = (
            "SOURCE_METADATA: "
            + json.dumps(source, ensure_ascii=False, separators=(",", ":"))
            + "\n\n"
            + entry["content"]
        )
        enriched_results.append(enriched_item)

    if report["candidate_coverage"] == "unresolved":
        fallback_message = (
            "ยังระบุไฟล์ที่อ้างถึงไม่ได้แน่ชัด "
            "กรุณาระบุชื่อไฟล์เต็มหรือรายละเอียดที่ช่วยแยกไฟล์ที่ต้องการ"
        )
    elif not enriched_results:
        fallback_message = (
            "ยังไม่พบหลักฐานที่เพียงพอจากการค้นหาครั้งนี้ "
            "กรุณาระบุหัวข้อ เลขข้อ หรือรายละเอียดที่ต้องการเพิ่มเติม"
        )
    else:
        fallback_message = ""

    return {
        "fallback_message": fallback_message,
        "result": enriched_results,
        "has_evidence": bool(enriched_results),
        "evidence_count": len(enriched_results),
        "selection_report": json.dumps(report, ensure_ascii=False, separators=(",", ":")),
    }


def main(
    results: list,
    scope_mode: str,
    document_names_csv: str,
    source_registry: list,
    strict: str,
    seek_other_sources: bool,
) -> dict:
    if results is None:
        results = []
    if not isinstance(results, list):
        raise ValueError("results must be an array")
    if not isinstance(scope_mode, str):
        raise ValueError("scope_mode must be a string")

    mode = scope_mode.strip().upper()
    if mode not in ("ALL", "SELECTED", "UNRESOLVED"):
        raise ValueError("invalid scope_mode")

    if not isinstance(strict, str):
        raise ValueError("strict must be a string")
    restriction = strict.strip().upper()
    if restriction not in ("STRICT", "NON_STRICT"):
        raise ValueError("invalid strict")
    # STRICT excludes other sources regardless of the Resolver's optional flag.
    # Ignore this irrelevant flag in STRICT; validate it in other modes.
    if restriction == "STRICT":
        seek_other_sources = False
    # Dify forms may submit JSON Boolean literals as text; never use bool(text).
    if isinstance(seek_other_sources, str):
        literal = seek_other_sources.strip()
        if literal in ("true", "false"):
            seek_other_sources = literal == "true"
    if not isinstance(seek_other_sources, bool):
        raise ValueError("seek_other_sources must be a boolean or true/false text")

    report = {
        "scope_mode": mode,
        "candidate_coverage": "not_required",
        "required_sources": [],
        "required_sources_present": [],
        "required_sources_not_retrieved": [],
        "required_sources_omitted_by_limit": [],
        "required_sources_unresolved": [],
        "other_source_status": "not_requested",
    }
    if mode == "UNRESOLVED":
        report["candidate_coverage"] = "unresolved"
        return _finish([], report)

    valid_items = []
    best_by_document_id = {}
    for original_index, item in enumerate(results):
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            continue
        metadata = item.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        valid_items.append({
            "original_index": original_index,
            "item": item,
            "content": content.strip(),
            "metadata": metadata,
        })
        document_id = metadata.get("document_id")
        if isinstance(document_id, str) and document_id.strip():
            best_by_document_id.setdefault(document_id, original_index)

    if mode == "ALL":
        return _finish(valid_items[:MAX_CONTEXT_CHUNKS], report)

    if not isinstance(document_names_csv, str) or not document_names_csv.strip():
        raise ValueError("SELECTED requires document_names_csv")
    required_names = list(dict.fromkeys(document_names_csv.split(",")))
    if any(not name.strip() for name in required_names):
        raise ValueError("document_names_csv contains an empty source")

    # Names are copied exactly; IDs come from the supplied runtime registry.
    by_name = _registry_document_ids(source_registry)
    unresolved = [name for name in required_names if len(by_name.get(name, set())) != 1]
    if unresolved:
        report["candidate_coverage"] = "unresolved"
        report["required_sources_unresolved"] = unresolved
        return _finish([], report)

    required_ids = {name: next(iter(by_name[name])) for name in required_names}
    report["required_sources"] = [
        {"document_name": name, "document_id": required_ids[name]}
        for name in required_names
    ]

    # Overflow is decided by retrieval rank, not the resolver's name order.
    anchors = sorted({
        best_by_document_id[document_id]
        for document_id in required_ids.values()
        if document_id in best_by_document_id
    })
    selected_indices = set(anchors[:MAX_CONTEXT_CHUNKS])
    required_id_set = set(required_ids.values())
    eligible_items = valid_items
    if restriction == "STRICT":
        # Keep only identifiable required-source candidates, including during fill.
        eligible_items = [
            entry for entry in valid_items
            if isinstance(entry["metadata"].get("document_id"), str)
            and entry["metadata"]["document_id"] in required_id_set
        ]

    if seek_other_sources and restriction == "NON_STRICT":
        # At most one anchor outside the selected source set; no extra retrieval.
        other_anchor = next((
            entry for entry in eligible_items
            if isinstance(entry["metadata"].get("document_id"), str)
            and entry["metadata"]["document_id"].strip()
            and entry["metadata"]["document_id"] not in required_id_set
        ), None)
        if other_anchor is None:
            report["other_source_status"] = "not_retrieved"
        elif len(selected_indices) >= MAX_CONTEXT_CHUNKS:
            report["other_source_status"] = "omitted_by_limit"
        else:
            selected_indices.add(other_anchor["original_index"])
            report["other_source_status"] = "present"

    for entry in eligible_items:
        if len(selected_indices) >= MAX_CONTEXT_CHUNKS:
            break
        selected_indices.add(entry["original_index"])

    # Iterating the original ranked list preserves order and selects each item once.
    selected_items = [
        entry for entry in eligible_items
        if entry["original_index"] in selected_indices
    ]
    for name in required_names:
        best_index = best_by_document_id.get(required_ids[name])
        if best_index is None:
            report["required_sources_not_retrieved"].append(name)
        elif best_index not in selected_indices:
            report["required_sources_omitted_by_limit"].append(name)
        else:
            report["required_sources_present"].append(name)

    report["candidate_coverage"] = (
        "partial"
        if report["required_sources_not_retrieved"] or report["required_sources_omitted_by_limit"]
        else "complete"
    )
    return _finish(selected_items, report)
