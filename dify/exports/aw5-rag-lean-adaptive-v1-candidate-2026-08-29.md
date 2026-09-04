# AW5-RAG Lean Adaptive v1 Candidate — 2026-08-29

> **Historical experiment, not the current workflow or next task.** Status and
> proposed checks below are preserved as dated records. Follow [CURRENT.md](CURRENT.md)
> for the owner-confirmed self-hosted main workflow and current direction. The
> candidate YAML and rebuild scripts described here remain separate local artifacts;
> they are not included in this documentation/current-snapshot commit.

## Status

- Source: `aw5-rag-source-routing-final-2026-08-25.yml`
- Source SHA-256: `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`
- Candidate: `aw5-rag-lean-adaptive-v1-candidate-2026-08-29.yml`
- Candidate SHA-256: `31009bd457534bee20a3b1865d425596afb204a6416ca75b86ff63fdddf8367f`
- Local graph validation: **passed**, 16 nodes / 18 edges / acyclic
- Embedded Python compilation and deterministic fixtures: **passed**
- Dify import: **not verified**
- Live Preview or Service API run: **not executed**
- Full 19-case evaluation: **not executed**
- Published state: **not published**

This is a Phase 1 experimental candidate, not a replacement for the verified
baseline or an updated `CURRENT.md` primary pointer.

## Controlled change

The first candidate intentionally preserves the baseline ingestion, LLM 1, Route
Queries, all three retrieval nodes, retrieval configuration, Merge Context, and LLM
2 model. It changes only the post-retrieval answer path so that answer-layer quality
can be measured without mixing in a retrieval architecture change.

Normal path:

```text
Merge Context
  -> Answer Contract (Code)
  -> LLM 2
  -> Answer Coverage Check (Code)
  -> Coverage Gate: pass
  -> Select Final Response
  -> Answer
```

Conditional repair path:

```text
Coverage Gate: fail
  -> Repair Answer (LLM, conditional)
  -> Repair Coverage Check (Code)
  -> Finalize Repair
  -> Select Final Response
  -> Answer
```

The normal path remains two LLM calls: LLM 1 and LLM 2. A third LLM call occurs
only after a deterministic risk check fails.

## Failure classes addressed

### `ER-01` and `XDOC-02` — missing schema identifiers

`ANSWER CONTRACT` extracts exact schema identifiers from the authoritative ER query
and the user question. `ANSWER COVERAGE CHECK` requires every extracted identifier
to occur in the answer. This directly targets the observed omission of
`UM_FUNCTION`, `UM_USER`, and `UM_USER_ORG` after correct routing/retrieval.

The contract does not invent a project-specific table list. It preserves identifiers
already produced by the existing source query or explicitly supplied by the user.

### `EDGE-03` — unsupported provider conclusion

When the question explicitly names AWS, Google Cloud, or Azure, the contract requires
the answer to preserve those names, state the evidence limitation when the provider
is not specified, and reject stronger phrases such as “does not use external cloud.”

### All other questions

When no exact schema identifier or named-provider risk is detected, the deterministic
contract is inactive. Any non-empty LLM 2 answer follows the normal baseline path
without invoking the repair model.

## Local fixtures passed

The build script verified that:

1. the ER query for `ER-01` produces all six required table identifiers;
2. an answer missing `UM_FUNCTION` fails coverage;
3. the provider question produces the AWS / Google Cloud / Azure evidence boundary;
4. a bounded “documents do not specify” answer passes; and
5. a “does not use external cloud” conclusion fails and enters repair.

These fixtures verify deterministic code behavior only. They are not RAG answer or
citation evidence.

## Deliberately deferred from v1

- Conditional execution of TOR/SDS/ER retrieval is deferred so the first comparison
  isolates answer completeness and provider grounding. The baseline still executes
  all three retrievers in parallel.
- No always-on evidence judge, answer verifier, reranker, or facet-decomposition LLM
  was added.
- No Top K, chunking, query-routing prompt, or model change was made.
- No live Dify application was modified or published.

Conditional retrieval can be tested as a separate v1.1 optimization after this
candidate meets the answer-quality gate, because it primarily affects embedding/
retrieval load and cost rather than the demonstrated answer-layer failures.

## Required validation sequence

After importing into a duplicate Dify app:

1. Inspect node variables and run the three deterministic Code nodes individually.
2. Run `ER-01`, `XDOC-02`, and `EDGE-03` at least five times each.
3. Confirm normal cases stay on two LLM calls and failure cases alone execute Repair.
4. Run controls `SDS-03`, `VIS-03`, and `QRY-01` to detect regressions.
5. Run all 19 executable cases under the same knowledge-base state as the baseline.
6. Repeat the full suite enough to report stability rather than a single lucky run.

Record strict correctness, citation precision, p50/p95 latency, model calls, tokens,
recorded price, repair rate, provider failures, and semantic failures. Do not promote
the candidate unless it meets the correctness/citation gate and improves or preserves
the baseline quality/speed/cost balance.

## Rebuild

```bash
ruby scripts/build_dify_lean_adaptive_v1.rb
```

The build is deterministic from the frozen baseline and locally validates graph
references, acyclicity, embedded Python syntax, and the targeted contract fixtures.
