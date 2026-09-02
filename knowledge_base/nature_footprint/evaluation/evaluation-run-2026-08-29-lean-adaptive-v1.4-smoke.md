# Lean Adaptive v1.4 ER-01 Smoke — 2026-08-29

> **Historical run under the legacy source-routing rubric.** Results and original
> recommendations below are preserved, not rescored or newly executed. Follow the
> [current export pointer](../../../dify/exports/CURRENT.md) for the owner-confirmed
> workflow and target direction; the recommendations below are not current tasks.

## Status

- App: imported and Published Lean Adaptive v1.4 test app
- Case: `ER-01`, two Service API runs plus a user-observed Dify UI check
- Workflow status: succeeded
- Purpose: validate upstream route normalization while preserving the v1 graph

## Service API observations

| Metric | Run 1 | History-check run |
| --- | ---: | ---: |
| End-to-end latency | 6.55 s | 12.69 s |
| Total tokens | 4,612 | 4,752 |
| Executed steps | 13 | 13 |
| Executed LLM calls | 2 | 2 |
| Repair LLM executed | No | No |
| Route | ER-only | ER-only |
| All six ER-01 identifiers present | Yes | Yes |
| Merge evidence | 6 ER chunks | 6 ER chunks |
| Streaming `retriever_resources` | 0 | 0 |

Both answers contained `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`,
`UM_ROLE_FUNCTION`, and `UM_USER_ORG`. Merge retained only `ER_dbdiagram.txt`, with
the standard citation metadata present.

The attempted read-only historical-message citation check returned HTTP 404 from
the current Service API endpoint, so it did not provide additional citation
evidence.

## Dify UI citation verification

The user reran the exact `ER-01` question in a new Dify UI conversation and
confirmed that the displayed citation was correct and precise: `ER_dbdiagram.txt`
only, with no TOR or SDS citation.

Therefore `ER-01` passes the semantic, route, and user-visible citation boundary on
v1.4. The empty streaming citation array is tracked as a Service API/diagnostic
observation and must not be scored as a workflow citation failure without a UI or
supported API confirmation.

## Decision

### XDOC-02 follow-up

The Service API run routed to TOR + SDS + ER and returned all requested facets:

- TOR clause 4.3: two access levels;
- SDS: Company Users, TIIS Officers, and Admin;
- ER: `UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`,
  `UM_ROLE_FUNCTION`, and `UM_USER_ORG`.

The run used two LLM calls without Repair, completed in 12.34 seconds, and consumed
7,545 tokens. The user reran the exact question in the Dify UI and confirmed that
all three required citations were present and precise: `Attach_TOR_1.pdf`,
`System Design Specification.pdf`, and `ER_dbdiagram.txt`.

`XDOC-02` therefore passes this smoke test. Proceed to `EDGE-03`. Continue
collecting route, answer completeness, latency, tokens, and provider errors through
the Service API, while using the Dify UI to verify user-visible citation precision
until a supported citation-history API path is confirmed.
