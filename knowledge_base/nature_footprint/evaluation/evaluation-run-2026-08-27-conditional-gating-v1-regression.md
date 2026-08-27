# AW5-RAG Conditional Gating — v1 Regression Run — 2026-08-27

## Run status

- App: `AW5-RAG Conditional Gating Test`, verified by Service API `/info`
- Suite: `evaluation-suite-v1-executable.json`
- Scope: the same 19 executable case IDs and final question wording recorded in the 2026-08-25 `19/19` baseline
- `ISO-01`: excluded; Project B and trusted tenant/project filters still do not exist
- Execution: Dify Service API streaming mode with sanitized node traces and final citation metadata
- Result: **12/19 strict pass**
- Workflow execution: **19/19 succeeded**, zero API errors and zero workflow exceptions
- Exact predefined routing: **16/19**
- Conditional gating behavior: **19/19 matched the observed router flags**
- No retry was performed because no provider/transport failure occurred. Semantic, routing, retrieval, and answer failures remain failures.

This result does not replace the frozen v1 `19/19` baseline. The conditional-gating app is not ready for promotion as the verified current workflow.

## Usage and latency

| Metric | Result |
|---|---:|
| Calls | 19 |
| Tokens | 108,455 |
| Model price | USD 0.1545191 |
| Median latency | 19.735 s |
| Average latency | 20.365 s |
| Maximum latency | 33.350 s (`VIS-03`) |

## Case results

| Case | Strict | Routing/retrieval/citation evidence |
|---|---:|---|
| QRY-01 | Pass | TOR-only route, retrieval, and citation; did not import Audit Log from SDS/ER. |
| TOR-01 | Pass | TOR-only; returned `P2451236` and the complete project name. |
| TOR-02 | Pass | TOR-only; returned the two required access levels. |
| TOR-03 | Pass | TOR-only; returned all four indicator groups. |
| SDS-01 | Pass | SDS-only; returned all three user groups. |
| SDS-02 | **Fail** | Answer content was complete, but router enabled TOR+SDS and citations included both documents instead of SDS only. |
| SDS-03 | Pass | SDS-only; covered password, encryption/hash, and Audit Log facets. |
| ER-01 | **Fail** | ER-only routing/citations were correct, but the answer omitted required table `UM_USER_ROLE`; returned only five of the six required RBAC tables. |
| ER-02 | **Fail** | Content was correct, but router enabled SDS+ER and citations included SDS instead of ER only. |
| ER-03 | **Fail** | Relationship content was correct, but router enabled SDS+ER and citations included SDS instead of ER only. |
| VIS-01 | Pass | SDS-only; returned organization, form code, and eight activities. |
| VIS-02 | **Fail** | Query weakened to `รูปที่ 3-8 ผลการคำนวณ`; retrieved unrelated figure chunks and incorrectly reported that figure 3-8 was absent. |
| VIS-03 | **Fail** | Correct SDS-only route, but retrieved chunks did not expose the required figure values; answer incorrectly reported insufficient evidence. |
| XDOC-01 | **Fail** | Correct TOR+SDS route, but SDS query weakened to `รูปที่ 3-8`; answer could not compare the four figure entries and did not conclude that none were missing. |
| XDOC-02 | Pass | Correct all-source routing/citations and complete TOR/SDS/ER access-control traceability. |
| EDGE-01 | Pass | Correct English TOR-only answer. |
| EDGE-02 | Pass | Rejected the false Material Footprint premise with TOR-only evidence. |
| EDGE-03 | Pass | Correct TOR+SDS insufficient-provider answer; did not guess AWS/GCP/Azure. |
| EDGE-04 | Pass | Resisted injection, retrieved TOR+SDS, rejected AWS, and retained citations. |

## Failure classification

### Router/source precision — 3 cases

- `SDS-02`: enabled TOR in addition to SDS.
- `ER-02`: enabled SDS in addition to ER.
- `ER-03`: enabled SDS in addition to ER.

The Gate nodes behaved correctly by executing exactly what the router enabled. These are LLM 1 routing failures, not conditional-branch execution failures.

### Retrieval-query and visual grounding — 3 cases

- `VIS-02`: the previous passing run used a caption-aligned query containing `Indicator Calculation UI`; the current generated query omitted those anchors.
- `XDOC-01`: the SDS query was only `รูปที่ 3-8`, which retrieved the figure index instead of the calculation result content.
- `VIS-03`: the query preserved the required figure/scopes/units, but the retrieved segments still did not contain the expected numeric evidence.

These failures show that a previously observed passing query is not guaranteed by the current LLM 1 generation. LLM 1 currently has `max_output_tokens: 256` and no explicit temperature value in the DSL; Structured Output guarantees shape, not deterministic query wording.

### Answer completeness — 1 case

- `ER-01`: retrieval returned six ER chunks and the router query named all six tables, but LLM 2 omitted `UM_USER_ROLE` from the answer.

## What the run proves

- Conditional gating is structurally correct: disabled source retrievers did not execute in all 19 cases.
- The conditional-gating app does not currently preserve the old strict `19/19` result in a fresh run.
- All failures were observable without opening Dify Studio or Last Run manually.
- The original frozen workflow remains the strongest verified correctness baseline; the gating app remains an experimental candidate.

## Next safe action

This run remains historical evidence for the first gating revision. A successor candidate later added a deterministic Route Guard and ER Top K 7; its manual smoke evidence is recorded in `evaluation-run-2026-08-27-route-guard-smoke.md`. Do not rewrite this `12/19` result as if the successor had passed the same full suite.

Before promoting the successor:

1. Make source-routing rules deterministic for explicit document, table, column, relationship, and figure references.
2. Restore reusable caption-aligned SDS query anchors for figure 3-8 without adding case-ID-specific answer rules.
3. Investigate `VIS-03` retrieved segment positions and index behavior before changing Top K or chunking.
4. Require LLM 2 to enumerate every requested identifier/facet and verify `ER-01` completeness.
5. Rerun only the seven failures first; if they pass, rerun a limited pass-set regression before considering a full promotion run.
