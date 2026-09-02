# Lean Adaptive v1.2 ER-01 Smoke — 2026-08-29

> **Historical run under the legacy source-routing rubric.** Results and original
> recommendations below are preserved, not rescored or newly executed. Follow the
> [current export pointer](../../../dify/exports/CURRENT.md) for the owner-confirmed
> workflow and target direction; the recommendations below are not current tasks.

## Status

- App: imported and Published Lean Adaptive v1.2 test app
- Case: `ER-01`, two Service API runs
- Workflow status: succeeded in both runs
- Purpose: test whether restoring baseline retrieval edges repairs citation output

## Results

| Metric | Run 1 | Diagnostic rerun |
| --- | ---: | ---: |
| End-to-end latency | 7.72 s | 11.43 s |
| Total tokens | 4,864 | 4,910 |
| Executed steps | 14 | 14 |
| Executed LLM calls | 2 | 2 |
| Repair LLM executed | No | No |
| All six ER-01 identifiers present | Yes | Yes |
| Guarded route | ER-only | ER-only |
| Citations returned | 0 | 0 |
| Strict result | **Fail** | **Fail** |

The corrected diagnostic now treats `LEAN ROUTE GUARD` as the authoritative route.
It confirmed `use_tor=false`, `use_sds=false`, and `use_er=true`.

## Evidence boundary diagnosis

The diagnostic rerun showed that `Merge Context` contained six results from
`ER_dbdiagram.txt`. Each result retained the standard Dify evidence fields,
including `dataset_id`, `document_id`, `document_name`, `segment_id`,
`segment_position`, `score`, and `retriever_from`. The grounded answer was complete,
but the final `message_end` event still contained no `retriever_resources`.

Therefore the missing citations are not explained by empty retrieval, an incorrect
guarded route, missing ER content, or stripped Merge metadata. Restoring only the
baseline Route-to-Retrieval edges was insufficient.

## Decision

Do not run the full suite on v1.2. Test v1.3, which removes the standalone Guard
node and folds the deterministic source filter into the existing Merge Context.
This restores the v1 dependency shape more closely and reduces the graph by one
node. Promote nothing unless `ER-01` returns the required ER-only citations.
