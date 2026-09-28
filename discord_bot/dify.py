"""Minimal server-side Dify Chatflow client."""

from dataclasses import dataclass
import json
import urllib.error
import urllib.request

from .config import Tenant


class DifyError(Exception):
    pass


@dataclass(frozen=True)
class DifyAnswer:
    text: str
    conversation_id: str


def ask_dify(
    tenant: Tenant, *, question: str, user_key: str, conversation_id: str | None, timeout: float = 30.0
) -> DifyAnswer:
    payload: dict[str, object] = {
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
        "user": user_key,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    request = urllib.request.Request(
        f"{tenant.dify_api_base_url}/chat-messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {tenant.dify_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise DifyError(f"Dify returned HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise DifyError("Dify did not return a valid response") from exc
    if not isinstance(data, dict):
        raise DifyError("Dify returned an invalid response")
    answer = data.get("answer")
    result_conversation_id = data.get("conversation_id")
    if not isinstance(answer, str) or not answer.strip():
        raise DifyError("Dify returned no answer")
    if not isinstance(result_conversation_id, str) or not result_conversation_id:
        raise DifyError("Dify returned no conversation ID")
    return DifyAnswer(answer, result_conversation_id)
