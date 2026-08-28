# AW5 Repository Guidance for Agents

## Project purpose

AW5 is a senior-project repository for a multi-tenant conversational assistant that retrieves evidence from selected SDLC project artifacts. It does not claim to perform the entire SDLC. The current case study uses Nature Footprint TOR, System Design Specification, and ER/dbdiagram artifacts.

## Read first

Before planning or changing the project, read these files in order:

1. `README.md` — current phase, verified state, missing evidence, and next priorities.
2. `dify/exports/CURRENT.md` — authoritative pointer to the current verified Dify DSL snapshot and frozen retrieval settings.
3. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md` — current baseline accuracy/latency/cost evidence and demonstrated failures.
4. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md` — historical scored `19/19` RAG evidence and its limits.
5. `knowledge_base/nature_footprint/evaluation/evaluation-suite-v1.md` — evaluation definitions, including the unexecuted `ISO-01` fixture.
6. `docs/course-requirements/ds1-ds3-requirements.md` — instructor-supplied deliverable requirements.
7. `knowledge_base/nature_footprint/README.md` and `manifest.json` — corpus provenance and ingestion boundaries.

Do not infer the latest workflow from export filenames alone. Follow `dify/exports/CURRENT.md`.

## Evidence and status rules

- Separate **verified**, **not verified**, and **planned** work. A plan, prompt, README statement, or configuration is not test evidence by itself.
- The historical RAG baseline run has `19/19` strict passes, while the fresh 2026-08-28 regression scored `16/19` strict after bounded retry. This does not prove stability, production readiness, multi-tenant isolation, or conversation memory.
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

## Primary RAG optimization challenge

The main workflow challenge is to satisfy all three goals together:

1. **Accurate and evidence-grounded answers** — answer every requested facet, avoid unsupported inference, and cite only the necessary trusted sources.
2. **Low response latency** — measure end-to-end p50 and p95 latency, node latency, and provider stalls; do not judge speed from a single run or the mean alone.
3. **Controlled API cost** — measure model calls, input/output tokens, and estimated price per question; avoid always-on LLM judges or verifiers when deterministic checks or conditional execution are sufficient.

Correctness is the release gate, not a tradeable average. Among candidates that meet the same strict correctness and citation requirements, prefer the workflow with lower latency, lower cost, and less complexity. Provider availability and repeatability are a fourth operational constraint: record 429/503 errors, timeouts, retries, and repeated-run variance separately from semantic RAG failures.

For workflow design and evaluation:

- Keep the verified two-LLM baseline as the control until a candidate proves a better measured balance.
- Default to the shortest safe path. Extra retrieval, judging, verification, or repair must run conditionally for a demonstrated risk or failure case.
- Do not add a node, prompt rule, or model call without identifying the failure it addresses and recording before/after correctness, citation, latency, and token evidence.
- A candidate is not better merely because it scores higher once; require repeatable results and report quality, speed, cost, and provider reliability together.
- Do not call a workflow production-ready if it achieves accuracy by creating unacceptable latency or cost, or achieves speed by weakening evidence grounding, privacy, or tenant isolation.

## Current priority

The verified source-routing baseline (`dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`) is the **primary development base and performance control**. Build the next lean adaptive candidate from it and add only conditional mechanisms that address demonstrated failures while preserving the two-LLM fast path.

Immediate workflow sequence:

1. Use the 2026-08-28 baseline recheck as the current before-evidence.
2. Address the demonstrated `ER-01`, `XDOC-02`, and `EDGE-03` semantic failures without always-on LLM judges/verifiers.
3. Re-run the same 19 cases and compare strict quality, citation precision, p50/p95 latency, tokens, recorded price, and provider failures.
4. Keep both the frozen baseline and heavier experimental artifacts available as controls; promote no candidate without repeatable evidence.

After the workflow quality/speed/cost balance is verified, continue the trusted tenant/project isolation priority:

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
