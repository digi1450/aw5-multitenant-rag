# AW5-RAG Route Guard + Merge Fix — Full Regression — 2026-08-27

## Evidence boundary

- App: `AW5-RAG Conditional Gating Test`
- Revision: Published after adding `ROUTE GUARD`, ER Top K 7, and changing all three `Merge Context.use_*` selectors to `ROUTE GUARD`
- Suite: `evaluation-suite-v1-executable.json`; 19 executable cases
- Execution: Dify Service API streaming mode with sanitized node traces
- Primary trace: `output/evaluation/aw5-rag-route-guard-merge-fixed-full-2026-08-27.json` (Git-ignored)
- Controlled retry: `output/evaluation/aw5-rag-route-guard-sds03-retry-2026-08-27.json` (Git-ignored)
- `ISO-01`: excluded; trusted tenant/project filtering and Project B do not exist

## Summary

| Metric | Result |
|---|---:|
| `ROUTE GUARD` present | 19/19 |
| Workflow success on primary run | 18/19 |
| Authoritative Guard route match | 18/19 |
| Strict quality after one provider retry | 15/19 |
| Total primary-run tokens | 102,805 |
| Median latency | 6.463 s |
| Average latency | 8.176 s |
| Maximum latency | 29.494 s (`ER-01`) |

The original runner incorrectly preferred the `Route Queries` output over `ROUTE GUARD`. It was corrected after this run so future reports retain planner, normalized, and Guard routes separately and score the Guard as authoritative.

## Verified improvements

- `SDS-02`: SDS-only retrieval and citation; complete upload/validation answer.
- `ER-01`: Guard changed planner SDS+ER to ER-only; ER Top K 7 added the rank-7 `UM_USER` segment and the answer returned all six required tables.
- `ER-02`: ER-only retrieval/citation and all three required columns.
- `ER-03`: ER-only and complete relationships.
- Every disabled retriever stayed unexecuted.
- The maximum latency fell from 133.530 seconds in the immediately preceding Published revision to 29.494 seconds in this run, but one run is not an SLA.

## Remaining strict failures

### `SDS-03` — routing and retrieval instability

- Primary run: LLM 1 enabled TOR+SDS+ER; the Guard retained that route because `Security Design` was not one of its deterministic SDS signals. LLM 2 then failed with a Google provider `PluginInvokeError`.
- Controlled retry: planner and Guard selected SDS-only and the workflow succeeded, but retrieval omitted the detailed Audit Log event chunk. The answer incorrectly stated that no specific Audit Log detail was available.
- The retry query also duplicated matched expansion terms, which wastes query budget and can weaken retrieval precision.

### `VIS-02` — wrong visual evidence accepted

The correct figure route and SDS citation were present, but the answer returned Carbon Footprint, Water Footprint, and Land Use instead of the expected four SUCCESS rows. The retrieved top segment describes a conflicting/nearby UI representation and there is no independent exact-reference evidence check.

### `VIS-03` — requested figure values not retrieved

The correct SDS route executed, but the retrieved chunks exposed only the figure caption/nearby text. The system safely returned insufficient evidence instead of the required Scope 1–3 values.

### `XDOC-01` — cross-document comparison used wrong SDS figure evidence

TOR evidence was correct, but SDS evidence led the model to report only three UI indicators and incorrectly conclude that Biodiversity Footprint was missing.

## Production-core requirements derived from this run

1. Use one authoritative route from planner validation through Gate, Retriever, Merge, diagnostics, and scoring.
2. Normalize and de-duplicate source queries before retrieval.
3. Add a deterministic SDS signal for explicit `Security Design` questions without treating generic `Audit Log` as SDS-only.
4. Add evidence sufficiency checking before answer generation, especially for exact figures/tables/sections.
5. Add post-generation claim/evidence verification so a citation to the right document cannot legitimize unsupported figure values.
6. Fail safely when exact visual evidence is absent; separately improve visual/OCR ingestion and retrieval recall.
7. Retain a controlled provider retry and deterministic terminal error response in the eventual runtime architecture.

## Promotion status

This revision is a stronger functional baseline but is not production-grade. Keep the frozen 2026-08-25 `19/19` snapshot as correctness rollback and use this run as before evidence for the production-core candidate.
