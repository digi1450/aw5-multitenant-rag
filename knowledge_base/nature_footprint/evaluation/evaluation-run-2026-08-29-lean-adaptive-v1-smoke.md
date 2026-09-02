# Lean Adaptive v1 ER-01 Smoke — 2026-08-29

> **Historical run under the legacy source-routing rubric.** Results and original
> recommendations below are preserved, not rescored or newly executed. Follow the
> [current export pointer](../../../dify/exports/CURRENT.md) for the owner-confirmed
> workflow and target direction; the recommendations below are not current tasks.

## Status

- App: imported and Published Lean Adaptive v1 test app
- Case: `ER-01`
- Service API workflow: succeeded
- Purpose: verify answer-contract fast path and detect regressions before the full suite
- Raw sanitized trace: retained only under ignored `output/evaluation/`

## Result

| Metric | Observed |
| --- | ---: |
| End-to-end latency | 6.82 s |
| Total tokens | 5,765 |
| Executed steps | 13 |
| Executed LLM calls | 2 |
| Repair LLM executed | No |
| Answer completeness | Pass; all six required tables present |
| Required citation boundary | Fail; SDS was included with ER |
| Strict case result | **Fail** |

The answer contained `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`,
`UM_ROLE_FUNCTION`, and `UM_USER_ORG`. `ANSWER CONTRACT`, `ANSWER COVERAGE CHECK`,
and `COVERAGE GATE` executed successfully, and the answer stayed on the two-LLM
fast path.

## Demonstrated failure

LLM 1 produced the complete ER query but over-routed the database-schema question:

```text
use_tor=false
use_sds=true
use_er=true
```

Expected routing was ER-only. Merge Context therefore included SDS and ER evidence,
and the final response cited both `System Design Specification.pdf` and
`ER_dbdiagram.txt`. This is a citation-precision failure even though the answer text
was complete.

The run demonstrates two separate findings:

1. the deterministic answer contract addresses the observed schema-identifier
   omission without invoking an always-on verifier or repair model; and
2. post-answer coverage cannot correct an upstream source-boundary error.

## Decision

Do not run the full suite on v1. Add a deterministic source-boundary guard and rerun
`ER-01` first. Preserve the normal two-LLM path and keep conditional retrieval as a
separate experiment so the citation-boundary change can be measured independently.
