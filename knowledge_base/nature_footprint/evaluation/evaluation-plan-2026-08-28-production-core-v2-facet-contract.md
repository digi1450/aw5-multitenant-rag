# AW5-RAG Production Core v2 Facet Contract — Evaluation Plan

## Candidate boundary

- Candidate: `dify/exports/aw5-rag-production-core-v2-facet-contract-candidate-2026-08-28.yml`
- Expected graph: 28 nodes / 33 edges
- Required new trace node: `REQUEST FACET CONTRACT`
- Baseline rollback: `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml` at commit `64418f8`
- `ISO-01`: excluded until trusted tenant/project filtering and a Project B fixture exist

Do not count an app-name match as revision evidence. After Publish, the Service API trace must contain `REQUEST FACET CONTRACT`, `EVIDENCE SUFFICIENCY`, `NORMALIZE EVIDENCE DECISION`, `ANSWER VERIFIER`, and `FINAL ANSWER COVERAGE CHECK`.

## Stage 0 — import and wiring control

1. Import the candidate into a Production Core test app.
2. Resolve Gemini models and existing TOR/SDS/ER datasets without changing prompts or retrieval settings.
3. Publish the test app.
4. Run one `SDS-03` request and verify all five required production nodes appear in the trace.
5. Inspect `REQUEST FACET CONTRACT` and confirm separate password-policy, encryption, and Audit Log facets.
6. Inspect `NORMALIZE EVIDENCE DECISION` and confirm every requested facet has one evidence mapping and no `contract_issues`.

## Stage 1 — repeated omission control

Run `SDS-03` ten times.

Pass conditions for every successful provider execution:

- route and citation are SDS-only;
- the contract contains password policy, encryption, and Audit Log as separate facets;
- Audit Log evidence includes login/logout, create/update/delete, indicator calculation, and process-error events;
- final answer contains every required term;
- `coverage_passed=true` and `missing_facets=[]`;
- a provider/model failure is recorded separately and is not counted as a semantic pass.

## Stage 2 — six-case risk suite

Run:

- `QRY-01` — explicit TOR boundary and unsupported Audit Log detail;
- `ER-01` — complete six-table RBAC set;
- `VIS-02` — exact figure 3-8 rows and statuses;
- `VIS-03` — exact figure 4-11 values and percentages;
- `XDOC-02` — TOR/SDS/ER cross-document coverage;
- `EDGE-04` — prompt-injection resistance and citation retention.

Require correct route, enabled retrievers only, complete requested facets, strict answer correctness, and citation precision for every case.

## Stage 3 — full executable suite

Run all 19 executable cases with sanitized traces. Record:

- planner, normalized, and authoritative Guard route;
- executed retrieval nodes and source boundaries;
- request facets and per-facet evidence statuses;
- normalized contract issues and required terms;
- final coverage outcome;
- answer correctness and completeness;
- citation precision;
- workflow/provider status, latency, and token use.

Promotion requires `19/19` strict semantic and citation quality on successful executions, no false-positive coverage pass, and a documented provider-failure rate. Repeated-run evidence is required before replacing the frozen baseline.
