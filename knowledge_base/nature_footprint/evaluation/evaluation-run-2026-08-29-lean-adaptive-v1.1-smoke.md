# Lean Adaptive v1.1 ER-01 Smoke — 2026-08-29

> **Historical run under the legacy source-routing rubric.** Results and original
> recommendations below are preserved, not rescored or newly executed. Follow the
> [current export pointer](../../../dify/exports/CURRENT.md) for the owner-confirmed
> workflow and target direction; the recommendations below are not current tasks.

## Status

- App: imported and Published Lean Adaptive v1.1 test app
- Case: `ER-01`, two independent Service API runs
- Workflow status: succeeded in both runs
- Purpose: verify guarded ER-only source boundary before broader testing

## Results

| Metric | Run 1 | Run 2 |
| --- | ---: | ---: |
| End-to-end latency | 12.54 s | 7.40 s |
| Total tokens | 4,681 | 4,753 |
| Executed steps | 14 | 14 |
| Executed LLM calls | 2 | 2 |
| Repair LLM executed | No | No |
| All six ER-01 identifiers present | Yes | Yes |
| Guarded route | ER-only | ER-only |
| Citations returned | 0 | 0 |
| Strict result | **Fail** | **Fail** |

LLM 1 over-routed the question to SDS + ER in both runs. `LEAN ROUTE GUARD`
correctly normalized the route to:

```text
use_tor=false
use_sds=false
use_er=true
```

The final answers contained `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`,
`UM_ROLE_FUNCTION`, and `UM_USER_ORG`. Both remained on the two-LLM fast path.

## Demonstrated regression

Dify returned no citations in either run. This is repeatable and therefore not
treated as a transient citation event.

The v1.1 graph changed the retrieval execution edge from the baseline provenance:

```text
Route Queries -> Retrieve source
```

to:

```text
Route Queries -> Lean Route Guard -> Retrieve source
```

while each retrieval node's query selector still referenced Route Queries. The
retrievals and grounded answer succeeded, but the altered execution/provenance path
is the leading explanation for Dify dropping citation resources.

## Decision

Do not continue to `XDOC-02` or `EDGE-03` on v1.1. Create v1.2 that restores the
baseline Route Queries-to-Retrieval edges and keeps Route Guard as an independent
Merge Context dependency. This retains guarded source inclusion without changing
the retrieval provenance path.
