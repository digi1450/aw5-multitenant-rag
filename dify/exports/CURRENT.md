# AW5-RAG Dify Export Pointer

## Current main workflow — owner-confirmed 2026-09-04

- Application: **AW5-RAG**.
- File:
  [aw5-rag-self-hosted-main-2026-09-04.yml](aw5-rag-self-hosted-main-2026-09-04.yml).
- Source: the owner supplied `AW5-RAG-2.yml` from the local self-hosted system and
  identified it as the new main workflow.
- SHA-256: `b843323262447b25eca4d17304c2b94d521cb53cdc75a18d6f30153e93c25b6d`.
- Status: **owner-confirmed current main export, statically inspected and
  preserved byte-for-byte; not formally runtime-tested**.
- Graph: 4 nodes / 3 edges / 1 LLM node:
  `User Input -> Knowledge Retrieval -> LLM -> Answer`.
- Retrieval: one node over three dataset references; weighted semantic/keyword
  `0.7/0.3`; Top K **10**; reranking and score threshold disabled.

See the [snapshot record](aw5-rag-self-hosted-main-2026-09-04.md) for models,
dependencies, prompt characteristics, wiring and verification limits. The export
matches the confirmed self-hosted architecture direction. Published/draft state,
live-app equality, answer quality and trusted project-tenant isolation were not
verified by preserving this file.

## Implemented direction — confirmed 2026-09-04, formal validation incomplete

The owner confirmed [self-hosted Dify, local knowledge storage, cloud models, and
one Knowledge Retrieval node](../../docs/architecture/current-direction-2026-09-02.md).
The current main export implements the simple single-retrieval graph without
per-file prompts or TOR/SDS/ER hard-gating flags. It references three Knowledge
Bases from the one retrieval node. The export and its static configuration are
reviewed repository evidence; formal quality, latency, cost, citation and isolation
evaluation remains incomplete.

The baseline below remains the frozen control and rollback artifact, **not the
required development template**. All earlier candidate notes, proposed next steps,
and source-router evaluation expectations in this directory are historical unless
explicitly re-approved. The current-workflow pointer is the owner-confirmed
self-hosted AW5-RAG export above.

## Previous owner-confirmed snapshot — 2026-09-02

- Application: **AW5-RAG 1.2**.
- File: [aw5-rag-1.2-current-2026-09-02.yml](aw5-rag-1.2-current-2026-09-02.yml).
- SHA-256: `7e1d7d7e49f711bf0653db38ed6b3923f590cf83d5b4d46538db6ae4fe2f320d`.
- Graph: 9 nodes / 10 edges / 2 LLM nodes; separate TOR/SDS/ER retrieval.
- Status: **superseded current-state snapshot; retained as historical evidence**.

See its [snapshot record](aw5-rag-1.2-current-2026-09-02.md). It is distinct from
the similarly named Lean Adaptive v1.2 candidate and does not inherit the frozen
baseline's evaluation scores.

## Frozen historical baseline and performance control

- File: `aw5-rag-source-routing-final-2026-08-25.yml`
- SHA-256: `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`
- Validated graph: 9 nodes / 10 edges / 2 LLM calls
- Repository baseline commit: `64418f8`
- Status: **authoritative historical baseline and rollback reference; not the new architecture**

The 2026-08-28 Published Service API trace matched the 9-step baseline architecture. That regression produced route match `19/19`, eventual citation boundaries `19/19`, strict semantic quality `16/19`, median latency `13.87 s`, and median usage `4,856` tokens per primary case under the legacy rubric. See `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md`.

Preserve this artifact without importing its hard-coded routing or answer contracts into the new design. A fresh owner export is required before claiming that any live app is byte-identical to this YAML.

## Historical Lean Adaptive experiments — 2026-08-29

The retained notes below describe past experiments. Their candidate YAML/build
artifacts remain separate local work and are not included in the current-workflow
snapshot update. References to those artifact filenames describe historical local
work, not an available or approved replacement for the current workflow.

- File: `aw5-rag-lean-adaptive-v1-candidate-2026-08-29.yml`
- SHA-256: `31009bd457534bee20a3b1865d425596afb204a6416ca75b86ff63fdddf8367f`
- Built from: the authoritative verified baseline above
- Validated graph: 16 nodes / 18 edges / 3 LLM nodes, with only 2 LLM calls on the normal path
- Change: deterministic schema/provider answer contract, deterministic coverage checks, and a third LLM call only on the repair path
- Initial build status: locally built and structurally validated. Later live smoke evidence is recorded below; this candidate is not promoted.

This was a Phase 1 experiment under the superseded roadmap. See
`aw5-rag-lean-adaptive-v1-candidate-2026-08-29.md` for its historical scope, fixtures,
and proposed validation sequence, not current implementation instructions.

The first live v1 `ER-01` smoke produced a complete six-table answer on the two-LLM
fast path, but failed strict citation precision because LLM 1 selected SDS + ER for
an ER-only question. See
`../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1-smoke.md`.

The v1.1 follow-up artifact was:

- File: `aw5-rag-lean-adaptive-v1.1-candidate-2026-08-29.yml`
- SHA-256: `96bfa846e27845e1091231dc016425f41fb1e05d2ede42578fd349bd582d3a94`
- Validated graph: 17 nodes / 19 edges; normal path remains 2 LLM calls
- Change from v1: one deterministic `LEAN ROUTE GUARD` controls Merge Context and
  Answer Contract source boundaries
- Initial build status: locally validated. Later live runs are recorded below; this candidate is not promoted.

v1.1 is retained for historical comparison, not scheduled as the next candidate.

Two live v1.1 `ER-01` runs confirmed correct ER-only guarded routing, complete
six-table answers, and the two-LLM fast path, but both returned zero citations. v1.1
therefore remains failed. Evidence:
`../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.1-smoke.md`.

The v1.2 follow-up artifact was:

- File: `aw5-rag-lean-adaptive-v1.2-candidate-2026-08-29.yml`
- SHA-256: `0c74a9265ab0186370add902400a98dbdd5fc75621c15aa1a2456a52f5358edf`
- Validated graph: 17 nodes / 20 edges; normal path remains 2 LLM calls
- Change from v1.1: restore baseline `Route Queries -> Retrieval` provenance and
  make Guard an independent Merge Context dependency
- Initial build status: locally validated; subsequent evidence is recorded in the dated v1.2 smoke report below. No promotion is made here.

Later records, retained without rescoring or promoting them:

- [v1.2 smoke](../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.2-smoke.md)
- [v1.3 candidate](aw5-rag-lean-adaptive-v1.3-candidate-2026-08-29.md) and [smoke](../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.3-smoke.md)
- [v1.4 candidate](aw5-rag-lean-adaptive-v1.4-candidate-2026-08-29.md), [smoke](../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.4-smoke.md), and [full report](../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.4-full.md). The full report records provisional semantic `19/19` after bounded provider retry but does not claim a strict `19/19` citation audit. It does not validate the new single-retrieval architecture.

## Historical Route Guard candidate — 2026-08-27

- File: `aw5-rag-route-guard-candidate-2026-08-27.yml`
- SHA-256: `52a4598dad3f2d56d5deee5f058bf5fdfce82a43523d050b858b66d9b2864754`
- Exported from: Dify Cloud test app on 2026-08-27 Asia/Bangkok
- Validated graph: 19 nodes / 23 edges
- Changes from the frozen baseline: conditional retrieval branches, deterministic `ROUTE GUARD`, fail-closed blank/generic queries, and ER Top K 7
- Validation: YAML/graph/source wiring passed; manual seven-question Preview smoke test passed after correcting the `TOR` token-boundary rule
- Status: **experimental candidate; full 19-case regression has not been rerun after the final Route Guard and ER Top K 7 changes**

Keep this candidate as a historical reference, not the new development base. Evidence: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-route-guard-smoke.md`.

## Verified draft snapshot at capture — 2026-08-25

- File: `aw5-rag-source-routing-final-2026-08-25.yml`
- SHA-256: `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`
- Exported from: Dify Cloud live saved draft on 2026-08-25 at 18:13 Asia/Bangkok
- Validated graph: 9 nodes / 10 edges
- Status at capture: **verified final draft snapshot; not Published at that time**. Current live state is not established here.

Use this file as the verified correctness and rollback reference. It contains the LLM prompt revisions and retrieval settings used for the final `19/19` scored evaluation.

## Frozen baseline configuration evidence — not new defaults

- LLM 1 prompt: 7,879 characters; SHA-256 `88b23028168330b7694d3b7db0ae755192ab136041e4f0841e5ace1bfa7a6067`
- LLM 2 prompt: 6,607 characters; SHA-256 `899f94ad5abcf29ae30226a34565282bdb4cacc39b14e162c97688f59cddc3ee`
- Models: LLM 1 `gemini-3.5-flash-lite`; LLM 2 `gemini-3.5-flash`
- Retrieval: Weighted Score 0.5 semantic / 0.5 keyword; TOR/SDS Top K 3; ER Top K 6; rerank disabled
- Export validation: YAML parsed successfully; expected 9-node/10-edge graph and all source-routing nodes present
- Structural comparison: node IDs/types, dataset IDs, retrieval configs, and Route/Merge code match the previous snapshot; source-to-target connectivity is unchanged. The exporter only normalized empty `sourceHandle` values and added `isInIteration: false` metadata on several edges.
- Secret-key scan: no API key, bearer token, password, credential, authorization, or remote-install-key field found; `max_output_tokens` was the only token-named configuration key

## Previous snapshots

- `aw5-rag-baseline-2026-08-25.yml` — original baseline before prompt/workflow tuning
- `aw5-rag-pre-source-routing-2026-08-25.yml` — rollback point immediately before source-specific routing changes
- `aw5-rag-source-routing-postfix-2026-08-25.yml` — earlier source-routing draft before the final prompt revisions
- `aw5-rag-conditional-gating-test-2026-08-27.yml` — first generated gating candidate before the final live Route Guard export

Do not treat these historical snapshots as the latest candidate or the verified baseline.

## Evidence and boundaries

- Before/after representative evaluation: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-representative-baseline.md`
- Final live-draft evaluation: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`; strict pass `19/19` scored cases
- At the 2026-08-25 capture, the Dify UI showed the improved workflow as an Auto-Saved draft while the Published version remained older
- `ISO-01` remains N/A until a Project B tenant fixture and trusted project-tenant filter exist; do not call tenant isolation complete
- Repository handoff for this snapshot and its full-suite evidence was completed on `origin/main` in commit `64418f8` (`feat: finalize AW5 RAG source-routing workflow`). This confirms the Git snapshot, not the current Dify Cloud Published state.
