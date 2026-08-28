#!/usr/bin/env python3
"""Run the AW5 Dify diagnostic suite and retain a sanitized node trace.

The output intentionally omits API keys, dataset IDs, complete node prompts,
and retrieved chunk text. It is written under the ignored output/ directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT / "knowledge_base/nature_footprint/evaluation/evaluation-suite-v2-diagnostic.json"


def load_env(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing environment file: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    return None


def route_from_outputs(outputs: Any) -> dict[str, Any] | None:
    if not isinstance(outputs, dict):
        return None
    candidate = outputs.get("structured_output")
    if isinstance(candidate, str):
        try:
            candidate = json.loads(candidate)
        except json.JSONDecodeError:
            candidate = None
    if not isinstance(candidate, dict):
        candidate = outputs
    keys = ("use_tor", "use_sds", "use_er", "tor_query", "sds_query", "er_query")
    if not any(key in candidate for key in keys):
        return None
    result: dict[str, Any] = {}
    for key in keys:
        value = candidate.get(key)
        if key.startswith("use_"):
            value = boolish(value)
        elif value is not None:
            value = str(value)[:500]
        result[key] = value
    return result


def result_rows(outputs: Any) -> list[Any]:
    if not isinstance(outputs, dict):
        return []
    for key in ("result", "results", "retriever_resources"):
        rows = outputs.get(key)
        if isinstance(rows, list):
            return rows
    return []


def compact_retrieval(outputs: Any) -> dict[str, Any]:
    rows = result_rows(outputs)
    scores: list[float] = []
    documents: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        score = row.get("score", metadata.get("score"))
        if isinstance(score, (int, float)):
            scores.append(round(float(score), 6))
        name = (
            row.get("title")
            or row.get("document_name")
            or metadata.get("document_name")
            or metadata.get("title")
        )
        if name and str(name) not in documents:
            documents.append(str(name)[:180])
    return {"count": len(rows), "scores": scores, "documents": documents}


def compact_node(data: dict[str, Any]) -> dict[str, Any]:
    title = str(data.get("title") or data.get("node_type") or "unknown")
    metadata = data.get("execution_metadata") if isinstance(data.get("execution_metadata"), dict) else {}
    node: dict[str, Any] = {
        "title": title,
        "type": data.get("node_type"),
        "status": data.get("status"),
        "elapsed_seconds": data.get("elapsed_time"),
        "error": str(data.get("error"))[:3000] if data.get("error") else None,
        "tokens": metadata.get("total_tokens"),
        "price": metadata.get("total_price"),
        "currency": metadata.get("currency"),
    }
    outputs = data.get("outputs")
    route = route_from_outputs(outputs)
    if route is not None:
        node["route"] = route
    if "retrieve" in title.lower() or data.get("node_type") == "knowledge-retrieval":
        node["retrieval"] = compact_retrieval(outputs)
    return node


def post_stream(url: str, api_key: str, payload: dict[str, Any], timeout: int) -> list[dict[str, Any]]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": "AW5-Dify-Diagnostic/2.0",
        },
    )
    events: list[dict[str, Any]] = []
    with urllib.request.urlopen(request, timeout=timeout) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data_text = line[5:].strip()
            if not data_text or data_text == "[DONE]":
                continue
            try:
                event = json.loads(data_text)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)
    return events


def summarize_case(case: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    answer_parts: list[str] = []
    nodes: list[dict[str, Any]] = []
    conversation_id = None
    message_id = None
    workflow: dict[str, Any] = {}
    citations: list[dict[str, Any]] = []
    api_error = None
    for event in events:
        event_name = event.get("event")
        conversation_id = event.get("conversation_id") or conversation_id
        message_id = event.get("message_id") or event.get("id") or message_id
        data = event.get("data") if isinstance(event.get("data"), dict) else {}
        if event_name in {"message", "agent_message"} and isinstance(event.get("answer"), str):
            answer_parts.append(event["answer"])
        elif event_name == "node_finished":
            nodes.append(compact_node(data))
        elif event_name == "workflow_finished":
            workflow = {
                "status": data.get("status"),
                "elapsed_seconds": data.get("elapsed_time"),
                "tokens": data.get("total_tokens"),
                "steps": data.get("total_steps"),
                "exceptions": data.get("exceptions_count"),
            }
        elif event_name == "message_end":
            metadata = event.get("metadata") if isinstance(event.get("metadata"), dict) else {}
            resources = metadata.get("retriever_resources")
            if isinstance(resources, list):
                for resource in resources:
                    if not isinstance(resource, dict):
                        continue
                    citations.append({
                        "document_name": resource.get("document_name"),
                        "segment_position": resource.get("segment_position"),
                        "score": resource.get("score"),
                    })
        elif event_name in {"error", "workflow_failed"}:
            api_error = str(event.get("message") or data.get("error") or event)[:2000]

    routes_by_title = {
        str(node.get("title")): node["route"]
        for node in nodes
        if isinstance(node.get("route"), dict)
    }
    planner_route = routes_by_title.get("LLM 1")
    normalized_route = routes_by_title.get("Route Queries")
    guard_route = routes_by_title.get("ROUTE GUARD")
    route = guard_route or normalized_route or planner_route
    expected_route = case.get("expected_route", {})
    route_match = None
    if route is not None:
        route_match = all(route.get(key) == expected for key, expected in expected_route.items())
    executed_retrievals = [
        node["title"] for node in nodes
        if "retrieve" in str(node.get("title", "")).lower()
    ]
    expected_enabled = [name for name, enabled in expected_route.items() if enabled]
    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "expected_behavior": case["expected_behavior"],
        "expected_route": expected_route,
        "planner_route": planner_route,
        "normalized_route": normalized_route,
        "guard_route": guard_route,
        "observed_route": route,
        "route_match": route_match,
        "expected_enabled_sources": expected_enabled,
        "executed_retrieval_nodes": executed_retrievals,
        "answer": "".join(answer_parts).strip(),
        "citations": citations,
        "conversation_id_present": bool(conversation_id),
        "message_id_present": bool(message_id),
        "workflow": workflow,
        "nodes": nodes,
        "api_error": api_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--env", type=Path, default=ROOT / ".env.aw5.local")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--start", type=int, default=1, help="1-based first case")
    parser.add_argument("--limit", type=int, help="maximum number of cases")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--pause", type=float, default=0.5)
    parser.add_argument(
        "--env-prefix",
        default="DIFY_AW5",
        help="environment variable prefix, for example DIFY_AW5_FIX",
    )
    args = parser.parse_args()

    load_env(args.env)
    env_prefix = args.env_prefix.strip()
    api_key = os.environ.get(f"{env_prefix}_API_KEY", "").strip()
    base_url = os.environ.get(f"{env_prefix}_API_BASE_URL", "").strip().rstrip("/")
    user = os.environ.get(f"{env_prefix}_TEST_USER", "aw5-codex-diagnostic-v2").strip()
    if not api_key or not base_url:
        raise SystemExit(f"{env_prefix}_API_KEY and {env_prefix}_API_BASE_URL must be non-empty")

    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    all_cases = suite["cases"]
    selected = all_cases[max(args.start - 1, 0):]
    if args.limit is not None:
        selected = selected[: args.limit]
    if not selected:
        raise SystemExit("No cases selected")

    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    safe_suite_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", str(suite["suite_id"])).strip("-")
    output_path = args.output or ROOT / "output/evaluation" / f"{safe_suite_id}-{timestamp}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    conversations: dict[str, str] = {}
    results: list[dict[str, Any]] = []
    endpoint = f"{base_url}/chat-messages"

    for index, case in enumerate(selected, start=1):
        group = case.get("conversation_group")
        payload = {
            "inputs": {},
            "query": case["question"],
            "response_mode": "streaming",
            "user": user,
        }
        if group and conversations.get(group):
            payload["conversation_id"] = conversations[group]
        print(f"[{index}/{len(selected)}] {case['id']}", flush=True)
        try:
            events = post_stream(endpoint, api_key, payload, args.timeout)
            result = summarize_case(case, events)
            for event in events:
                conversation_id = event.get("conversation_id")
                if group and conversation_id:
                    conversations[group] = str(conversation_id)
                    break
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read(2000).decode("utf-8", errors="replace")
            except OSError:
                detail = ""
            result = {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "expected_behavior": case["expected_behavior"],
                "expected_route": case.get("expected_route"),
                "api_error": f"HTTPError {exc.code}: {detail}"[:2500],
                "nodes": [],
            }
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            result = {
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "expected_behavior": case["expected_behavior"],
                "expected_route": case.get("expected_route"),
                "api_error": f"{type(exc).__name__}: {exc}",
                "nodes": [],
            }
        results.append(result)
        output = {
            "suite_id": suite["suite_id"],
            "generated_at": datetime.now().astimezone().isoformat(),
            "service_api_base_redacted": True,
            "sanitization": "No API key, dataset IDs, full prompts, or retrieved chunk text retained.",
            "selected_start": args.start,
            "selected_count": len(selected),
            "completed_count": len(results),
            "results": results,
        }
        output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if index < len(selected):
            time.sleep(args.pause)

    print(f"Saved sanitized run: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
