# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

Last verified: **2026-08-28** from repository artifacts and sanitized Dify Service API traces. The latest live-tested Production Core candidate was exported on **2026-08-28**; a newer facet-contract candidate is locally validated but not yet imported or tested live.

Current phase: **verified RAG baseline frozen; Production Core experiment isolated on `codex/rag-production-core-v1`; tenant/project isolation pending**.

Verified:

- DS1 Project Concept was submitted.
- The private Nature Footprint corpus is prepared locally for controlled RAG experiments.
- The Dify source-routed Chatflow has separate TOR, SDS, and ER retrieval paths.
- The current verified export is `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`; `dify/exports/CURRENT.md` records its hash and frozen settings.
- The full currently executable evaluation achieved strict pass `19/19`; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`.
- The final export and its evaluation evidence are committed and available on `origin/main`.
- The latest live-tested experimental export is `dify/exports/aw5-rag-production-core-v1-coverage-candidate-2026-08-28.yml`. It contains 27 nodes / 32 edges and adds conditional retrieval, a deterministic Route Guard, evidence sufficiency, answer verification, deterministic final-answer coverage, and safe insufficient-evidence handling.
- The next local candidate is `dify/exports/aw5-rag-production-core-v2-facet-contract-candidate-2026-08-28.yml`. It contains 28 nodes / 33 edges and adds an explicit request-facet contract plus per-facet evidence mapping. Its YAML, graph, selectors, embedded Code nodes, and local contract/coverage fixtures pass, but it has not been imported, Published, or evaluated through the Service API.
- The Production Core candidate completed a targeted repeated test of `SDS-03` and `XDOC-02` with 10/10 successful executions and correct citations after verified visual extraction was added to the SDS knowledge base.
- The latest full 19-case regression produced authoritative route matches and citation boundaries for 19/19 cases. Eight primary executions failed in Gemini provider/model calls and every case eventually obtained a successful execution through bounded provider retries.

Not yet verified or complete:

- The verified `19/19` workflow was last observed as a saved Dify draft, not Published. Recheck Dify Cloud before making a current live-state claim about either app.
- The Production Core candidate is not promoted as the verified correctness baseline. Its latest full regression achieved strict answer quality `18/19`; `SDS-03` omitted requested Audit Log events while its LLM-generated `required_answer_terms` contract still allowed the final coverage check to pass.
- The 2026-08-25 source-routing export at commit `64418f8` remains the verified `19/19` correctness and rollback baseline. Later Route Guard and Production Core artifacts are experiments until explicitly promoted.
- `ISO-01` remains N/A until a Project B fixture and a trusted backend tenant/project filter exist.
- Multi-tenant authorization, production deployment, frontend/backend implementation, and conversation-memory behavior are not complete or proven.

Next priorities:

1. Import the locally validated facet-contract v2 candidate into a Dify test app and confirm the Published node trace contains `REQUEST FACET CONTRACT`.
2. Run `SDS-03` ten times, then the six-case risk suite, then all 19 executable cases; retain the frozen `19/19` workflow as rollback until the candidate passes consistently.
3. Enforce trusted `tenant_id` and `project_id` authorization before retrieval.
4. Add document metadata filtering, a synthetic Project B fixture, and execute `ISO-01`.
5. Define provider retry/error handling separately from semantic RAG quality.

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
