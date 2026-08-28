# AW5-RAG Published Conditional-Gating Baseline — 2026-08-27

## Evidence boundary

- App identity: `AW5-RAG Conditional Gating Test`, verified through Service API `/info`
- Suite: `evaluation-suite-v1-executable.json`; 19 executable cases
- Execution: Dify Service API streaming mode with sanitized node traces
- Raw sanitized trace: `output/evaluation/aw5-rag-route-guard-full-2026-08-27.json` (Git-ignored)
- Result describes the app's **Published Service API revision**, not the saved draft exported as `dify/exports/aw5-rag-route-guard-candidate-2026-08-27.yml`

The trace contains no `ROUTE GUARD` node in any case. The published graph executed 15 steps for a single-source route and still produced the pre-Guard over-routing behavior. The Service API revision therefore does not match the latest saved draft even though the app identity is the same.

## Summary

| Metric | Result |
|---|---:|
| Workflow success | 19/19 |
| Strict quality | 13/19 |
| Exact predefined routing | 16/19 |
| Disabled retriever execution | 0 |
| Total tokens | 109,166 |
| Median latency | 7.183 s |
| Average latency | 20.601 s |
| Maximum latency | 133.530 s (`VIS-02`) |

`VIS-02` spent 127.609 seconds in LLM 1; retrieval took 2.827 seconds and LLM 2 took 2.167 seconds. This is provider/model latency rather than a retrieval-graph delay.

## Strict failures

| Case | Failure evidence |
|---|---|
| `SDS-02` | Correct content, but routed TOR+SDS and cited TOR although the question was SDS-only. |
| `ER-01` | Routed SDS+ER, cited both, and omitted required base table `UM_USER`. Published ER retrieval returned only six results. |
| `ER-02` | Correct three columns, but routed/cited SDS+ER instead of ER only. |
| `VIS-02` | Correct SDS route but hallucinated a different four-item UI: included Water Footprint, omitted Biodiversity Footprint, and reported one pending result instead of all four SUCCESS. |
| `VIS-03` | Correct SDS route but returned insufficient evidence instead of the required Scope 1–3 values. |
| `XDOC-01` | Correct TOR+SDS route but claimed Biodiversity Footprint was missing from figure 3-8. |

`ER-03`, which failed source precision in the earlier 12/19 run, routed ER-only and answered correctly in this run. This improvement is run variance in the published pre-Guard revision, not evidence that the saved Route Guard draft was exercised.

## Architecture findings

1. App identity is insufficient to prove Service API revision identity. Node-title/step trace must be checked after each Publish.
2. Conditional gates prevent disabled retrievers from executing, but they cannot correct an inaccurate LLM route by themselves.
3. A correct document citation is not sufficient when the retrieved visual chunk does not contain the requested figure facts; the model may hallucinate a nearby UI.
4. One-shot generation has no independent evidence-sufficiency or claim-to-citation check.
5. Provider latency can dominate the whole request even when retrieval and answer generation are fast.
6. The latest exported draft has a separate wiring defect: Gate/Retrieve nodes read Guard outputs, while `Merge Context` still reads the original `Route Queries.use_*` flags. The production candidate must use one authoritative route object end to end.

## Promotion status

This published revision is not a production candidate. Preserve it only as before evidence. The next candidate must be imported/published separately, confirmed through node traces, and evaluated against this baseline plus holdout and repeated-run suites.
