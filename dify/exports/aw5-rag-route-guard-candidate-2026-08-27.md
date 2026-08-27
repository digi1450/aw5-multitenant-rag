# AW5-RAG Route Guard Candidate — 2026-08-27

## Artifact

- DSL: `aw5-rag-route-guard-candidate-2026-08-27.yml`
- SHA-256: `52a4598dad3f2d56d5deee5f058bf5fdfce82a43523d050b858b66d9b2864754`
- Source: owner-exported Dify Cloud test app
- App name inside DSL: `AW5-RAG Conditional Gating Test`
- Graph: 19 nodes / 23 edges
- Status: experimental candidate; not the frozen `19/19` baseline

## Verified structure

- `Route Queries` feeds one deterministic `ROUTE GUARD` code node.
- `ROUTE GUARD` emits three normalized use flags and three source-specific queries.
- Gate TOR, SDS, and ER read the corresponding outputs from `ROUTE GUARD`.
- Each disabled branch uses an empty-result node; each enabled branch calls only its source retriever.
- TOR/SDS Top K remain 3; ER Top K is 7; weighted semantic/keyword retrieval remains 0.5/0.5; reranking remains disabled.
- LLM 1 and LLM 2 node configurations match the frozen source-routing baseline.
- Blank queries and the generic fallback `ข้อมูลโครงการ` are disabled before retrieval.
- YAML parsing, node/edge references, Gate inputs, retriever query inputs, and a secret-pattern scan passed locally.

## Route Guard intent

The Guard keeps LLM 1 as the general router but deterministically corrects high-confidence cases: explicit source names, database identifiers/relationships, SDS screen/design signals, and TOR requirement signals. The `TOR` source-name check uses token boundaries so text such as `INDICATOR` does not accidentally enable TOR.

## Evidence boundary

- Manual Dify Preview smoke evidence: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-route-guard-smoke.md`
- The first conditional-gating revision scored `12/19`; that result does not describe this final export.
- This final export has not yet been rerun through all 19 executable cases.
- `ISO-01`, tenant isolation, production readiness, and Published state remain unverified.

Promotion requires a fresh full regression with recorded routing, retrieved sources, answer correctness, citation precision, and limitations.
