# AW5 layer-separation diagnostic — 2026-09-09

**Exploratory diagnostic; not formal evaluation, promotion, or production validation.**

The owner authorized an isolated workflow copy, bounded model calls, local-only detailed traces, fixed-context replay and an offline Code 1 candidate. Timeout-root-cause investigation was explicitly deferred.

## Verified results

- Six end-to-end Draft-debugger runs and six frozen/golden-evidence replays completed: 12 answer-model calls, no timeouts, reported 45,807 answer-model tokens / USD 0.0856305. Six retrieval executions additionally used the existing embedding provider; its calls/cost and internal retries were not fully measured.
- Full filename in Thai retrieved TOR and answered correctly twice. Two frozen-context replays also answered correctly. All four recorded rendered prompts had the same hash.
- An alias-only query failed to resolve the intended document and returned only SDS evidence.
- An English query triggered the confirmed Regex sentence-prefix overcapture, yielding an empty retrieval result. The model fabricated an identifier. A replay with the identical empty-context rendered prompt fabricated a different identifier.
- The factor-history use case again lacked ER evidence. Replaying the same evidence did not recover the missing structure.
- Supplying verbatim relevant DBML tables recovered the core history/source-reference fields in two runs, while unsupported schema interpretation remained. This demonstrates the importance of evidence coverage without establishing that generation is fully corrected.
- A generic registry-backed reference resolver passed ten synthetic offline cases. It is an undeployed candidate; its aliases come from caller-supplied registry data and do not grant access or automatically impose exclusive source scope.

## Runtime boundary

Execution froze the source app's then-active Published workflow, which had a newer identity than the September 7 evaluation. Source ID/graph and secret-free export are recorded locally. The source system prompt matched the archived September 7 evaluated system prompt. Results remain attached to the newly captured identity and do not update the historical 13/20 score.

The isolated app `AW5 Diagnostic 2026-09-09 (isolated draft)` was created through normal Dify export/import services and tested using the internal Draft debugger path. It was never Published and was restored to its starting graph after fixture replay. Readback verified that the original source Published ID and graph were unchanged during this task. Knowledge Base content was not reindexed or edited.

## Recommended order

1. Add an explicit empty-usable-evidence guard before the answer LLM; return insufficient evidence without making a model call. Nonempty irrelevant evidence needs separate handling.
2. Repair filename/alias resolution using authorized document registry data, preserving the distinction between mentioned sources and explicit exclusive scope.
3. Inspect ER candidate selection and table boundaries; test one retrieval repair at a time, preserving originals.
4. Evaluate answer grounding on frozen sufficient evidence; compare prompt simplification and thinking level separately only after establishing the control.
5. Evaluate held-out questions, repeated runs, multi-turn context, citation precision and trusted tenant isolation before release.

## Local evidence and limitations

Atomic package: `output/research-evidence/experiments/2026-09-09-layer-diagnostic/` with `report.md`, `evidence.json`, `manifest.json`, snapshots and relevant traces. Private questions, answers and source excerpts remain local-only.

This is a small diagnostic sample, not an accuracy estimate. Draft debugger results require later Published API verification. Fixed rendered prompts do not establish provider-request byte identity. Golden fixtures do not validate ingestion, native citation rendering, or a deployed repair. Ratings are assistant-reviewed, not independently adjudicated. No history-dependent trials or tenant-isolation tests were run.

Related plan: [RAG improvement plan](rag-improvement-plan-2026-09-09.md). Historical formal result: [2026-09-07 evaluation](self-hosted-real-use-case-evaluation-2026-09-07.md).
