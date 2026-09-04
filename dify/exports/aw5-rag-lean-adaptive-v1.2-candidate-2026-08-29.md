# AW5-RAG Lean Adaptive v1.2 Candidate — 2026-08-29

> **Historical experiment, not the current workflow or next task.** Status and
> proposed checks below are preserved as dated records. Follow [CURRENT.md](CURRENT.md)
> for the owner-confirmed self-hosted main workflow and current direction. The
> candidate YAML and rebuild scripts described here remain separate local artifacts;
> they are not included in this documentation/current-snapshot commit.

## Status

- Input candidate: `aw5-rag-lean-adaptive-v1.1-candidate-2026-08-29.yml`
- Candidate: `aw5-rag-lean-adaptive-v1.2-candidate-2026-08-29.yml`
- Candidate SHA-256: `0c74a9265ab0186370add902400a98dbdd5fc75621c15aa1a2456a52f5358edf`
- Local graph validation: **passed**, 17 nodes / 20 edges / acyclic
- Embedded Python and deterministic fixtures: **passed**
- Retrieval-provenance graph fixture: **passed**
- Dify import and live execution: **not verified**
- Full suite: **not executed**
- Published state: **not published**

## Controlled change from v1.1

v1.2 changes graph dependencies only:

```text
Route Queries -> Retrieve TOR / SDS / ER -> Merge Context
             \-> Lean Route Guard -------> Merge Context
```

Each retrieval node again has the same direct execution predecessor and query
selector as the verified baseline. Merge Context waits for the three retrievals and
the Guard, then includes results only for the guarded source flags.

No prompt, model, Top K, chunking, retrieval query, Answer Contract, coverage rule,
or repair behavior changed from v1.1.

## Why this change is required

Two live v1.1 `ER-01` runs produced complete answers and correct ER-only guarded
routes, but Dify returned zero citations both times. See
`../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.1-smoke.md`.

v1.2 restores baseline retrieval provenance while preserving the guarded Merge
boundary. This is a targeted hypothesis that must be confirmed by a live run; local
graph validation alone cannot prove Dify citation behavior.

## Required next check

Import and Publish v1.2, then rerun only `ER-01`. The run must:

1. execute `LEAN ROUTE GUARD` and normalize to ER-only;
2. include all six required table identifiers;
3. cite `ER_dbdiagram.txt` only;
4. execute two LLM calls without Repair; and
5. expose 15 steps or fewer with no workflow exception.

If citations remain empty, stop modifying the graph and inspect Dify's Last Run
outputs for Merge Context, LLM 2 context resources, and final response metadata
before proposing another change.

## Rebuild

```bash
ruby scripts/build_dify_lean_adaptive_v1_2.rb
```
