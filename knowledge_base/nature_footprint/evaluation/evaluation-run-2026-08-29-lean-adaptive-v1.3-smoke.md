# Lean Adaptive v1.3 ER-01 Smoke — 2026-08-29

> **Historical run under the legacy source-routing rubric.** Results and original
> recommendations below are preserved, not rescored or newly executed. Follow the
> [current export pointer](../../../dify/exports/CURRENT.md) for the owner-confirmed
> workflow and target direction; the recommendations below are not current tasks.

## Status

- App: imported and Published Lean Adaptive v1.3 test app
- Case: `ER-01`
- Workflow status: succeeded
- Purpose: test citation propagation after removing the standalone Guard node

## Result

| Metric | Observed |
| --- | ---: |
| End-to-end latency | 13.40 s |
| Total tokens | 4,614 |
| Executed steps | 13 |
| Executed LLM calls | 2 |
| Repair LLM executed | No |
| All six ER-01 identifiers present | Yes |
| Merged evidence boundary | ER-only |
| Citations returned | 0 |
| Strict result | **Fail** |

`Merge Context` contained six rows from `ER_dbdiagram.txt`, with standard Dify
citation metadata intact. The answer contained `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`,
`UM_FUNCTION`, `UM_ROLE_FUNCTION`, and `UM_USER_ORG`. The final `message_end` event
still contained no `retriever_resources`.

## Finding

Removing the standalone Guard node did not restore citation propagation. The v1.3
graph edges are identical to citation-positive v1. Exact node comparison showed
only one material difference: v1.3 added `sys.query` to Merge Context and performed
the deterministic source filter inside that node.

## Decision

Do not run the full suite on v1.3. Build v1.4 directly from v1, keep Merge Context
and all graph edges exactly unchanged, and perform deterministic source
normalization inside the existing `Route Queries` node. Test only `ER-01` first.
