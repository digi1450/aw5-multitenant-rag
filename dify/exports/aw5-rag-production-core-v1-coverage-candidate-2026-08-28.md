# AW5-RAG Production Core v1 Coverage Candidate — 2026-08-28

## Artifact

- DSL: `aw5-rag-production-core-v1-coverage-candidate-2026-08-28.yml`
- SHA-256: `92f4a0ae72eafd826c509d27e9dd4b957f3bfcfba3b72008789579c9b7f7b7d9`
- App name inside DSL: `AW5-RAG Production Core v1 Candidate`
- Graph: 27 nodes / 32 edges
- Working branch: `codex/rag-production-core-v1`
- Status: owner-exported experimental candidate; not the verified correctness baseline

## Architecture

```text
START
  -> LLM 1
  -> Route Queries
  -> ROUTE GUARD
  -> conditional TOR / SDS / ER retrieval
  -> Merge Context
  -> EVIDENCE SUFFICIENCY
  -> NORMALIZE EVIDENCE DECISION
  -> EVIDENCE GATE
       IF answerable
         -> LLM 2
         -> ANSWER VERIFIER
         -> FINALIZE VERIFIED ANSWER
         -> FINAL ANSWER COVERAGE CHECK
       ELSE
         -> INSUFFICIENT EVIDENCE RESPONSE
  -> SELECT FINAL RESPONSE
  -> Answer
```

## Changes from the 2026-08-27 Production Core candidate

- Evidence structured output contains `decision`, `missing_facts`, `required_answer_terms`, and `reason`.
- `NORMALIZE EVIDENCE DECISION` normalizes the decision and removes duplicate required terms.
- `ANSWER VERIFIER` receives the required answer terms and is instructed to preserve supported terms verbatim.
- `FINAL ANSWER COVERAGE CHECK` deterministically rejects an answer that omits a required term.
- `SELECT FINAL RESPONSE` now receives the coverage-checked answer or the insufficient-evidence response.
- Verified visual extraction text for figures 3-8 and 4-11 was added to the SDS knowledge base outside this Git repository; the private corpus remains excluded from Git.

## Validation evidence

- YAML parsed successfully with 27 unique node IDs and 32 valid edges.
- The final path is wired as `FINALIZE VERIFIED ANSWER -> FINAL ANSWER COVERAGE CHECK -> SELECT FINAL RESPONSE`.
- The coverage node receives `question`, finalized `answer_text`, `approved`, normalized `decision`, and `required_answer_terms`.
- Pass and fail fixtures for the coverage node behaved as expected.
- Repeated targeted Service API runs for `SDS-03` and `XDOC-02` completed 10/10 with correct answers and citations.
- In the full 19-case regression, authoritative routes and citation boundaries matched 19/19.
- The primary run completed 11/19 workflows; eight executions failed in Gemini provider/model calls. Bounded retries eventually produced one successful execution for every case.
- Strict semantic quality was 18/19. `SDS-03` omitted requested Audit Log events in one successful full-suite execution while the generated coverage contract still passed.

## Promotion boundary

Do not promote this export over `aw5-rag-source-routing-final-2026-08-25.yml` yet. The deterministic checker currently validates only terms supplied by an upstream LLM. It cannot detect an omitted factual facet when that LLM also omits the corresponding required term. The next candidate should combine the evidence-generated terms with deterministic anchors for exact identifiers, figures, sections, numeric values, and high-risk security facets, then rerun repeated controls and the full suite.

This artifact does not implement trusted tenant/project isolation, conversation memory, backend authorization, or `ISO-01`.
