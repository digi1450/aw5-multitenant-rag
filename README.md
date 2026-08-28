# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

Last verified: **2026-08-28** from repository artifacts and sanitized Dify Service API traces. The current Published Service API exposed the 9-step, two-LLM source-routing baseline; the latest Production Core and facet-contract workflows remain experiments.

Current phase: **the verified source-routing baseline is the primary development base and performance control; the next workflow will be a lean adaptive derivative, while Production Core remains an isolated safety-heavy experiment**.

Verified:

- DS1 Project Concept was submitted.
- The private Nature Footprint corpus is prepared locally for controlled RAG experiments.
- The Dify source-routed Chatflow has separate TOR, SDS, and ER retrieval paths.
- The current verified export is `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`; `dify/exports/CURRENT.md` records its hash and frozen settings.
- The full currently executable evaluation achieved strict pass `19/19`; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`.
- The final export and its evaluation evidence are committed and available on `origin/main`.
- A fresh 2026-08-28 Service API regression confirmed the baseline-shaped 9-step graph, two LLM calls, route match `19/19`, and eventual citation boundaries `19/19`. Its current strict semantic score was `16/19`, median latency `13.87 s`, and median usage `4,856` tokens per primary case; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md`.
- The latest live-tested experimental export is `dify/exports/aw5-rag-production-core-v1-coverage-candidate-2026-08-28.yml`. It contains 27 nodes / 32 edges and adds conditional retrieval, a deterministic Route Guard, evidence sufficiency, answer verification, deterministic final-answer coverage, and safe insufficient-evidence handling.
- The next local candidate is `dify/exports/aw5-rag-production-core-v2-facet-contract-candidate-2026-08-28.yml`. It contains 28 nodes / 33 edges and adds an explicit request-facet contract plus per-facet evidence mapping. Its YAML, graph, selectors, embedded Code nodes, and local contract/coverage fixtures pass, but it has not been imported, Published, or evaluated through the Service API.
- The Production Core candidate completed a targeted repeated test of `SDS-03` and `XDOC-02` with 10/10 successful executions and correct citations after verified visual extraction was added to the SDS knowledge base.
- The latest full 19-case regression produced authoritative route matches and citation boundaries for 19/19 cases. Eight primary executions failed in Gemini provider/model calls and every case eventually obtained a successful execution through bounded provider retries.

Not yet verified or complete:

- The current Service API trace structurally matches the baseline architecture, but an exact current live YAML/hash still requires a fresh owner export; Dify Cloud does not synchronize automatically with Git.
- The historical baseline result was `19/19`, but the fresh regression was `16/19` strict after bounded retry. Treat repeatability as unresolved and do not quote the historical score as a current stability guarantee.
- The Production Core candidate is not promoted as the verified correctness baseline. Its latest full regression achieved strict answer quality `18/19`; `SDS-03` omitted requested Audit Log events while its LLM-generated `required_answer_terms` contract still allowed the final coverage check to pass.
- The 2026-08-25 source-routing export at commit `64418f8` remains the verified `19/19` correctness and rollback baseline. Later Route Guard and Production Core artifacts are experiments until explicitly promoted.
- `ISO-01` remains N/A until a Project B fixture and a trusted backend tenant/project filter exist.
- Multi-tenant authorization, production deployment, frontend/backend implementation, and conversation-memory behavior are not complete or proven.

Next priorities:

1. Use the verified two-LLM baseline as the performance control and build a lean adaptive candidate that addresses demonstrated semantic failures without running every judge/verifier on every question.
2. Compare candidates on strict answer quality, citation precision, p50/p95 latency, model calls, tokens, estimated API cost, and provider failures under the same suite and knowledge-base state.
3. Keep the facet-contract v2 workflow as a safety-heavy experiment; do not promote it unless it proves a better measured quality/speed/cost balance than the lean candidate.
4. Enforce trusted `tenant_id` and `project_id` authorization before retrieval.
5. Add document metadata filtering, a synthetic Project B fixture, and execute `ISO-01`.
6. Define provider retry/error handling separately from semantic RAG quality.

## Main RAG challenge

The project must optimize three objectives together:

1. answer accurately and only from sufficient evidence;
2. answer quickly enough for practical interactive use; and
3. keep model/API cost bounded and observable.

Accuracy and evidence safety are release gates. When two workflows meet the same strict quality bar, prefer the one with lower p50/p95 latency, fewer model calls, fewer tokens, and simpler failure handling. Provider errors and latency spikes must be measured separately from semantic failures so architecture decisions are based on comparable evidence rather than a single aggregate score.

## Repository structure

```text
docs/
  course-requirements/       Official DS1–DS3 submission requirements
  deliverables/              Submitted and working deliverables
dify/                        Dify workflow export instructions/artifacts
knowledge_base/
  nature_footprint/          Publishable metadata and evaluation material
```

## Privacy boundary

The Nature Footprint source documents and derived text are private project material. They are intentionally excluded from Git. Only metadata, corpus notes, and evaluation questions are version-controlled until publication permission is confirmed.

The GitHub repository must remain **Private** while student information and course deliverables are present.

## Dify workflow

The running Dify application is maintained separately from this repository. Export its DSL/YAML after meaningful workflow changes and store the export under `dify/exports/`; never commit API keys or provider credentials. `dify/exports/CURRENT.md` identifies the repository snapshot that should be used for continuation.

Custom Dify plugins are maintained in separate Git repositories and are not versioned in this repository.
