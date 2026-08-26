# AW5 Repository Guidance for Agents

## Project purpose

AW5 is a senior-project repository for a multi-tenant conversational assistant that retrieves evidence from selected SDLC project artifacts. It does not claim to perform the entire SDLC. The current case study uses Nature Footprint TOR, System Design Specification, and ER/dbdiagram artifacts.

## Read first

Before planning or changing the project, read these files in order:

1. `README.md` — current phase, verified state, missing evidence, and next priorities.
2. `dify/exports/CURRENT.md` — authoritative pointer to the current verified Dify DSL snapshot and frozen retrieval settings.
3. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md` — scored `19/19` RAG evidence and its limits.
4. `knowledge_base/nature_footprint/evaluation/evaluation-suite-v1.md` — evaluation definitions, including the unexecuted `ISO-01` fixture.
5. `docs/course-requirements/ds1-ds3-requirements.md` — instructor-supplied deliverable requirements.
6. `knowledge_base/nature_footprint/README.md` and `manifest.json` — corpus provenance and ingestion boundaries.

Do not infer the latest workflow from export filenames alone. Follow `dify/exports/CURRENT.md`.

## Evidence and status rules

- Separate **verified**, **not verified**, and **planned** work. A plan, prompt, README statement, or configuration is not test evidence by itself.
- The current RAG baseline has `19/19` strict passes for executable scored cases. This does not prove production readiness, multi-tenant isolation, or conversation memory.
- `ISO-01` is N/A until a synthetic Project B fixture and trusted backend `tenant_id`/`project_id` filtering exist.
- The verified DSL/evaluation baseline is committed on `origin/main` at `64418f8`. The working tree may contain newer documentation, so inspect `git status` before making a current repository-state claim. The Dify Cloud app is maintained separately and does not synchronize automatically with Git.
- The improved Dify workflow was last verified as a saved draft on 2026-08-25. Check the live application before claiming that it is currently Published or unchanged.
- Do not describe the assistant as doing the whole SDLC. Describe it as retrieving and tracing evidence across selected SDLC artifacts.

## Current architecture boundary

The verified Dify flow is:

```text
START -> LLM 1 -> Route Queries
                    |-> Retrieve TOR --|
                    |-> Retrieve SDS --|-> Merge Context -> LLM 2 -> Answer
                    |-> Retrieve ER  --|
```

- LLM 1 classifies source facets and writes source-specific queries; it does not answer.
- TOR, SDS, and ER retrieval nodes execute in parallel.
- Merge Context includes only sources enabled by the router, deduplicates results, and preserves citation metadata.
- LLM 2 writes the grounded answer from merged context.
- Answer returns `LLM 2.text`; it is not another model call.
- Retrieval uses weighted semantic/keyword search `0.5/0.5`, TOR/SDS Top K `3`, ER Top K `6`, with reranking disabled.

Do not tune prompts, chunking, Top K, fallback, or reranking without a failing evaluation case and before/after evidence.

## Current priority

Preserve the working RAG baseline. The next system priority is trusted tenant/project isolation:

1. Resolve authorized tenant/project scope in the backend, not from user text or an untrusted frontend selection.
2. Attach filterable tenant/project metadata to documents or datasets.
3. Create a synthetic Project B fixture.
4. Execute `ISO-01` and prove that Project A cannot retrieve, answer from, or cite Project B.
5. Add deterministic insufficient-evidence handling.
6. Build application authentication, project/document management, API integration, and frontend around the verified isolation boundary.

## Privacy and secrets

- Nature Footprint sources, derived text, cleaned/OCR outputs, and Dify-upload files are private by default and excluded from Git.
- Keep the GitHub repository private while course deliverables or student information are present.
- Never commit `.env`, API keys, tokens, credentials, `.difypkg` packages, private corpus files, vector indexes, or generated `output/` artifacts.
- Preserve original files and checksums in `knowledge_base/nature_footprint/manifest.json`; do not overwrite provenance sources with cleaned outputs.
- Do not publish, distribute, upload elsewhere, or expose Nature Footprint material without explicit owner permission.

## Repository boundaries

- This repository stores AW5 project documentation, evaluation evidence, and Dify DSL snapshots.
- The live Dify Cloud application is external state. Export a new dated DSL after meaningful changes and update `dify/exports/CURRENT.md` only after validation.
- `dify/plugins/gemini-embedding-2-aw5/` is a separate local Git repository and is ignored by this repository. Treat its commits, branches, releases, secrets, tests, and package artifacts independently.
- Generated `.difypkg` files under `dify/plugins/` are local deployment artifacts and must remain untracked.

## Safe change procedure

Before changing files:

1. Inspect `git status` and preserve unrelated user changes.
2. Confirm whether the request is read-only, diagnostic, or authorizes implementation.
3. For Dify changes, preserve/export a rollback snapshot and work on a duplicate app when the change is risky.
4. Do not Publish a Dify app, modify external services, commit, push, create a release, or expose private material unless the user explicitly authorizes that action.
5. Record evaluation questions, routing, retrieved sources, answer correctness, citation precision, and limitations after a meaningful RAG change.
6. Update status documents when repository evidence changes; retain historical evaluation results instead of rewriting them as if they were newly rerun.

## Future code directories

When frontend and backend implementation begins, add scoped `AGENTS.md` files inside those directories for framework-specific commands, tests, style, and security rules. The root rules in this file continue to apply unless a more specific nested rule adds stricter guidance.
