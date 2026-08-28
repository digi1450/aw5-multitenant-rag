# AW5-RAG Dify Export Pointer

## Primary development base and performance control

- File: `aw5-rag-source-routing-final-2026-08-25.yml`
- SHA-256: `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`
- Validated graph: 9 nodes / 10 edges / 2 LLM calls
- Repository baseline commit: `64418f8`
- Status: **authoritative verified baseline, rollback reference, and base for the next lean adaptive candidate**

The 2026-08-28 Published Service API trace matched the 9-step baseline architecture. The fresh full regression produced route match `19/19`, eventual citation boundaries `19/19`, strict semantic quality `16/19`, median latency `13.87 s`, and median usage `4,856` tokens per primary case. See `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md`.

Do not continue feature development from Production Core v1/v2 by default. Use them as safety-heavy comparison artifacts and port only mechanisms that prove a better quality/speed/cost balance onto a lean baseline-derived candidate. A fresh owner export is still required before claiming that the live app is byte-identical to this YAML.

## Safety-heavy facet-contract experiment

- File: `aw5-rag-production-core-v2-facet-contract-candidate-2026-08-28.yml`
- SHA-256: `7bfc598f377a34d06315d9694a1b008bd51a18dcfe66e5b03d5a2c2c97fa8a08`
- Source: generated from the owner-exported v1 coverage candidate by `../../scripts/build_dify_production_core_v2.rb`
- Validated graph: 28 nodes / 33 edges
- Branch: `codex/rag-production-core-v1`
- Changes: adds `REQUEST FACET CONTRACT`, maps evidence to every requested facet, validates facet sources and request terms against the authoritative route, fails closed on missing/duplicate/unknown facet evidence, and checks final coverage per supported facet
- Local validation: deterministic build hash; 67 selectors reference valid nodes; DAG validation passed; all embedded Code nodes compile; complete, missing-facet, and missing-answer-term fixtures passed; secret-pattern scan passed
- Status: **locally validated candidate; not imported, Published, or evaluated live**

Use the staged test order in `../../knowledge_base/nature_footprint/evaluation/evaluation-plan-2026-08-28-production-core-v2-facet-contract.md` only if this safety-heavy branch is resumed. Do not promote this file until it proves a better measured quality/speed/cost balance than the baseline-derived lean candidate.

## Latest Production Core experiment

- File: `aw5-rag-production-core-v1-coverage-candidate-2026-08-28.yml`
- SHA-256: `92f4a0ae72eafd826c509d27e9dd4b957f3bfcfba3b72008789579c9b7f7b7d9`
- Source: owner-exported Dify Cloud Production Core candidate on 2026-08-28 Asia/Bangkok
- Validated graph: 27 nodes / 32 edges
- Branch: `codex/rag-production-core-v1`
- Changes: conditional source gates, authoritative Route Guard, evidence sufficiency decision, normalized evidence contract, safe insufficient response, answer verifier, finalization, and deterministic final-answer coverage check
- Validation: YAML/graph/wiring and secret-pattern checks passed; targeted repeated controls succeeded 10/10; full 19-case run matched authoritative routes and citation boundaries 19/19, but strict answer quality was 18/19 after provider-controlled retries
- Status: **latest live-tested experimental candidate; not promoted over the verified 2026-08-25 baseline**

The remaining semantic failure is `SDS-03`: one successful full-suite execution omitted the requested Audit Log events while the LLM-generated `required_answer_terms` list was incomplete, so the deterministic coverage node had no missing term to reject. The next design step is a hybrid contract that combines evidence-generated terms with deterministic anchors for high-risk exact facets. Evidence: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-production-core-coverage.md`.

## Latest experimental candidate

- File: `aw5-rag-route-guard-candidate-2026-08-27.yml`
- SHA-256: `52a4598dad3f2d56d5deee5f058bf5fdfce82a43523d050b858b66d9b2864754`
- Exported from: Dify Cloud test app on 2026-08-27 Asia/Bangkok
- Validated graph: 19 nodes / 23 edges
- Changes from the frozen baseline: conditional retrieval branches, deterministic `ROUTE GUARD`, fail-closed blank/generic queries, and ER Top K 7
- Validation: YAML/graph/source wiring passed; manual seven-question Preview smoke test passed after correcting the `TOR` token-boundary rule
- Status: **experimental candidate; full 19-case regression has not been rerun after the final Route Guard and ER Top K 7 changes**

This is the previous Route Guard experiment. Do not treat it or Production Core as the primary development base. Evidence: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-route-guard-smoke.md`.

## Current verified draft snapshot

- File: `aw5-rag-source-routing-final-2026-08-25.yml`
- SHA-256: `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`
- Exported from: Dify Cloud live saved draft on 2026-08-25 at 18:13 Asia/Bangkok
- Validated graph: 9 nodes / 10 edges
- Status: **verified final draft snapshot; not Published**

Use this file as the verified correctness and rollback reference. It contains the LLM prompt revisions and retrieval settings used for the final `19/19` scored evaluation.

## Frozen configuration evidence

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
- The Dify UI showed the improved workflow as an Auto-Saved draft while the Published version remained older
- `ISO-01` remains N/A until a Project B fixture and trusted tenant/project filter exist; do not call tenant isolation complete
- Repository handoff for this snapshot and its full-suite evidence was completed on `origin/main` in commit `64418f8` (`feat: finalize AW5 RAG source-routing workflow`). This confirms the Git snapshot, not the current Dify Cloud Published state.
