# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

- DS1 Project Concept submitted.
- Nature Footprint corpus prepared locally for controlled RAG experiments.
- Dify source-routed Chatflow draft configured with separate TOR, SDS, and ER retrieval paths.
- Current verified draft export: `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`; see `dify/exports/CURRENT.md` for its hash and frozen settings.
- Full currently executable evaluation: strict pass `19/19`; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`.
- The verified workflow remains a Dify draft and is not Published. `ISO-01` remains N/A until a Project B fixture and trusted tenant/project filter exist.

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
