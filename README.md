# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

Last verified: **2026-08-26** from repository evidence. The Dify Cloud live state was last inspected on **2026-08-25**.

Current phase: **RAG baseline frozen; tenant/project isolation pending**.

Verified:

- DS1 Project Concept was submitted.
- The private Nature Footprint corpus is prepared locally for controlled RAG experiments.
- The Dify source-routed Chatflow has separate TOR, SDS, and ER retrieval paths.
- The current verified export is `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`; `dify/exports/CURRENT.md` records its hash and frozen settings.
- The full currently executable evaluation achieved strict pass `19/19`; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`.
- The final export and its evaluation evidence are committed and available on `origin/main`.

Not yet verified or complete:

- The improved workflow was last observed as a saved Dify draft, not Published. Recheck Dify Cloud before making a current live-state claim.
- `ISO-01` remains N/A until a Project B fixture and a trusted backend tenant/project filter exist.
- Multi-tenant authorization, production deployment, frontend/backend implementation, and conversation-memory behavior are not complete or proven.

Next priorities:

1. Enforce trusted `tenant_id` and `project_id` authorization before retrieval.
2. Add document metadata filtering and a synthetic Project B fixture.
3. Run and record the `ISO-01` cross-project leakage test.
4. Add deterministic insufficient-evidence handling before introducing retrieval fallback or reranking.
5. Continue with the application API, authentication/authorization, and frontend after the isolation boundary is defined.

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
