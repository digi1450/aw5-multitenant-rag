# Test4.7 v3.2 — owner-supplied export and deployment

The owner supplied `AW5-RAG Test4.7 v3.2.yml`. Its byte-identical preservation is
`aw5-rag-test4-7-v3-2-owner-supplied-2026-10-03.yml`, SHA-256
`f4a7415c06881202a33ed84480e5d01ea33b8fed1bd06117b63e7b504611628e`.

## Configuration and observations

- Ten nodes / nine edges. Registry is now Code 1; the filter builder is Code 2;
  the existing evidence/context preparation is Code 3. Downstream code,
  retrieval and Writer configuration match the prior preserved v3-4 snapshot.
- Required paragraph `aw5_registry_json` feeds Registry `registry_json`.
  Registry output `json` feeds both Resolver and context preparation. The old
  Database Client node and dependency are removed.
- The exported parser passed 15 offline contract tests. The focused
  backend/bot/registry suite passed 44 offline tests before deployment.
- Six owner-initiated Draft turns were inspected: one SDS case; ALL, two-file
  STRICT and unknown-file cases; and SDS followed by TOR with changed JSON in
  the same verified conversation. All executed nodes succeeded. Unknown-file
  handling returned a deterministic clarification without Writer execution.
- These are exploratory diagnostics, not formal quality, repeatability,
  SQL shortlist parity, memory-quality or cross-project isolation evidence.

## Owner-authorized deployment

The owner Published this app and supplied its key locally. App ID:
`59ac4d02-12f9-4da2-8de3-6a4098b51e20`; verified Published workflow ID:
`4b64c99a-250e-46c2-8e46-54e7a4680bb9`.

AW5 tenant 1 was rebound from the previous app while preserving tenant ID,
name, guild and Discord role. The key's app binding was verified in local Dify
without logging its value; selected Knowledge metadata and Published parser
contract were checked. An encrypted rollback registration was saved locally
before a one-time database transaction. This does not implement the planned
admin rebind API, explicit-ID registration or provisioning UI.

The API was paused and restarted to load prepared backend Registry code.
Ten open-ticket conversation IDs pointing at the old app were reset; ticket
rows and Discord messages were preserved. The next question in such a ticket
starts a new Dify conversation. API health and active registration were verified,
and the owner's current role remained eligible. Temporary plaintext key input
was deleted.

Actual Discord Start/ask/list/close and automatic per-question Registry changes
through the backend are still pending owner verification. Draft Preview
multi-turn success does not prove this deployed integration. ISO-01 remains
unverified until two real projects are onboarded and tested.

## Subsequent Discord incident — 19:57 Bangkok time

Start succeeded, but the first owner question returned backend HTTP 503 because
Dify returned HTTP 400. Registry, Resolver, filter builder and Retrieval succeeded;
Code 3 rejected `seek_other_sources = "strict_mode"`. Resolver's configured schema
already requires a Boolean, yet this run produced an invalid string while
`strict = STRICT`. This is a Resolver-output/consumer-contract failure, not a
Registry-input or container connectivity failure. No retry inference was initiated.

Prepared candidate `dify/code/test4_7_v32_context_strict_seek_guard.py` changes
only treatment of this optional flag in STRICT: other sources are prohibited,
so it deterministically becomes false. Valid NON_STRICT behavior is unchanged;
invalid NON_STRICT flags are still rejected. Offline replay reproduced the
incident and verified equality with the original code given explicit false,
plus four valid and three invalid NON_STRICT cases. Candidate installation and
Publish remain pending owner action; the preserved export is unchanged.

Private detailed evidence, graph, encrypted rollback and conversation pointers
remain ignored under `output/research-evidence/experiments/2026-10-03-v32-registry-draft/`.
No secrets or private retrieved content belong in this snapshot record.
