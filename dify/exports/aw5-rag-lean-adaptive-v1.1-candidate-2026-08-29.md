# AW5-RAG Lean Adaptive v1.1 Candidate — 2026-08-29

> **Historical experiment, not the current workflow or next task.** Status and
> proposed checks below are preserved as dated records. Follow [CURRENT.md](CURRENT.md)
> for the owner-confirmed self-hosted main workflow and current direction. The
> candidate YAML and rebuild scripts described here remain separate local artifacts;
> they are not included in this documentation/current-snapshot commit.

## Status

- Input candidate: `aw5-rag-lean-adaptive-v1-candidate-2026-08-29.yml`
- Candidate: `aw5-rag-lean-adaptive-v1.1-candidate-2026-08-29.yml`
- Candidate SHA-256: `96bfa846e27845e1091231dc016425f41fb1e05d2ede42578fd349bd582d3a94`
- Local graph validation: **passed**, 17 nodes / 19 edges / acyclic
- Embedded Python compilation: **passed**
- Answer-contract, coverage, and Route Guard fixtures: **passed**
- Dify import and live execution: **not verified**
- Full suite: **not executed**
- Published state: **not published**

This v1.1 artifact addresses the live v1 `ER-01` citation-boundary failure recorded
in `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1-smoke.md`.

## Controlled change from v1

One deterministic `LEAN ROUTE GUARD` Code node is inserted after `Route Queries`.
It preserves explicit document requests, forces unambiguous database/schema
questions to ER-only, preserves unambiguous SDS design questions as SDS-only, and
preserves unambiguous TOR requirement questions as TOR-only. Ambiguous hosting/
provider questions retain the authoritative LLM 1 route.

The Guard outputs control which retrieved results enter Merge Context and which
queries feed the Answer Contract. This prevents an unrelated source from reaching
LLM 2 or appearing as a citation.

## Important v1.1 boundary

All three baseline retrieval nodes still execute with the original non-empty LLM 1
queries. Only Merge Context uses the guarded source flags. This isolates citation
precision and answer-context behavior from conditional-retrieval changes and avoids
passing a blank query to a retrieval node.

Therefore v1.1 is expected to fix the ER-only citation boundary, but it does not yet
reduce the three-retriever embedding/retrieval load. Conditional retrieval remains
a separate v1.2 optimization after v1.1 proves correctness.

## Local fixtures passed

- The observed `ER-01` route (`SDS + ER`) is normalized to ER-only.
- Explicit `TOR + SDS + ER` in `XDOC-02` remains three-source.
- Explicit `TOR ข้อ 14` remains TOR-only.
- Ambiguous AWS / Google Cloud / Azure hosting remains TOR + SDS when LLM 1 selects
  those sources.
- Graph endpoints, selectors, acyclicity, and all embedded Python compile checks pass.

These are deterministic code fixtures, not live answer/citation evidence.

## Required next check

Import v1.1 into the test app, Publish it, point the local Service API key to that
app, and rerun only `ER-01`. It must:

1. execute `LEAN ROUTE GUARD`;
2. output guarded `use_sds=false`, `use_er=true`;
3. include all six required schema identifiers;
4. cite only `ER_dbdiagram.txt`;
5. remain on two LLM calls; and
6. avoid executing the conditional Repair LLM.

Only after this check passes should `XDOC-02` and `EDGE-03` be run.

## Rebuild

```bash
ruby scripts/build_dify_lean_adaptive_v1_1.rb
```
