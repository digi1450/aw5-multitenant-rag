# AW5 Repository Guidance for Agents

## Project purpose

AW5 is a senior-project repository for a multi-tenant conversational assistant that retrieves evidence from selected SDLC project artifacts. It does not claim to perform the entire SDLC. The current case study uses Nature Footprint TOR, System Design Specification, and ER/dbdiagram artifacts.

## Read first

Before planning or changing the project, read these files in order:

1. `README.md` — current direction, historical evidence, and unresolved decisions.
2. `docs/architecture/current-direction-2026-09-02.md` — authoritative owner-confirmed architecture; supersedes the old locked roadmap.
3. `dify/exports/CURRENT.md` — owner-confirmed current AW5-RAG 1.2 export, frozen baseline, and historical candidates; none is a deployed implementation of the new direction.
4. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md` — historical baseline accuracy/latency/cost evidence and demonstrated failures.
5. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md` — historical scored `19/19` RAG evidence and its limits.
6. `knowledge_base/nature_footprint/evaluation/evaluation-suite-v1.md` — legacy evaluation definitions, including the unexecuted `ISO-01` fixture; source-router expectations are not the new architecture contract.
7. `docs/course-requirements/ds1-ds3-requirements.md` — instructor-supplied deliverable requirements.
8. `knowledge_base/nature_footprint/README.md` and `manifest.json` — corpus provenance and ingestion boundaries.

Do not infer the latest workflow from export filenames alone. Follow `dify/exports/CURRENT.md` for artifacts and the current-direction document for design intent. Newer explicit owner instructions supersede older repository plans or agent memory; ask before resolving ambiguity.

## Evidence and status rules

- Separate **verified**, **not verified**, and **planned** work. A plan, prompt, README statement, or configuration is not test evidence by itself.
- The owner identified `dify/exports/aw5-rag-1.2-current-2026-09-02.yml` as the current workflow. Its byte-identical preservation and static configuration are verified, not its runtime behavior or Published/draft state. It is distinct from Lean Adaptive v1.2 and must not inherit old evaluation scores.
- The historical RAG baseline run has `19/19` strict passes, while the 2026-08-28 regression scored `16/19` strict after bounded retry under the legacy rubric. This does not prove the new architecture, stability, production readiness, multi-tenant isolation, or conversation memory.
- `ISO-01` is N/A until a synthetic Project B fixture and trusted backend `tenant_id`/`project_id` filtering exist.
- The verified DSL/evaluation baseline is committed on `origin/main` at `64418f8`. The working tree may contain newer documentation, so inspect `git status` before making a current repository-state claim. The Dify Cloud app is maintained separately and does not synchronize automatically with Git.
- The baseline export records a saved draft on 2026-08-25; later dated traces and candidate reports are separate evidence. Check the live application before claiming that it is currently Published or unchanged.
- Do not describe the assistant as doing the whole SDLC. Describe it as retrieving and tracing evidence across selected SDLC artifacts.

## Current architecture direction — confirmed 2026-09-02

- Dify and persistent knowledge/files run on the owner's computer, acting as the project server. Models use cloud APIs: embeddings, answer LLM, and reranker if one is selected.
- Use one Knowledge Retrieval node over the authorized corpus; do not split retrieval by TOR/SDS/ER or gate it with `use_tor` / `use_sds` / `use_er`.
- Do not hard-filter to a document merely because the question names it. Preserve actual source attribution; broader retrieval does not permit claiming that one document says something found only in another.
- Prompts must be generic: no per-file descriptions, test questions, expected answers, worked examples, or case-specific exceptions to force known tests to pass.
- Adding a file must not require another routing node or a system-prompt update. Knowledge-base layout, model/provider choice, reranking, installation details, and optional rewriting/history behavior remain undecided.
- Local storage is not zero disclosure: cloud embedding receives chunk/query text; cloud reranking receives candidates; answer generation receives the selected context. Do not claim that only final Top-K evidence leaves the computer.
- Preserve old workflows as controls, not as a required design template. The new direction has not been implemented or validated by this documentation update.

Full decisions and open questions: `docs/architecture/current-direction-2026-09-02.md`.

## Current workflow snapshot — distinct from target and baseline

`dify/exports/aw5-rag-1.2-current-2026-09-02.yml` is the owner-confirmed current
AW5-RAG 1.2 export. It still uses LLM 1, Route Queries, three retrieval nodes,
Merge Context, LLM 2, and Answer: 9 nodes / 10 edges. Its weighted retrieval is
`0.5/0.5`, TOR/SDS Top K `3`, ER Top K `10`, with reranking disabled.

Use `dify/exports/CURRENT.md` and its linked snapshot record for exact current-file
configuration. Preserve the export without editing its prompts/code. This current
workflow is not the new single-retrieval target; its existing models are not a
decision about models for that target. The frozen baseline below remains separate.

## Historical baseline architecture — not the new target

The frozen source-routing baseline flow is:

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

These settings describe the historical baseline only; they are not approved defaults for the new workflow. Preserve its DSL and past results. Do not tune or run evaluations without authorization, and record before/after evidence when an implementation change is authorized.

## Primary RAG optimization challenge

The main workflow challenge is to satisfy all three goals together:

1. **Accurate and evidence-grounded answers** — answer every requested facet, avoid unsupported inference, and cite only the necessary trusted sources.
2. **Low response latency** — measure end-to-end p50 and p95 latency, node latency, and provider stalls; do not judge speed from a single run or the mean alone.
3. **Controlled API cost** — measure model calls, input/output tokens, and estimated price per question; avoid always-on LLM judges or verifiers when deterministic checks or conditional execution are sufficient.

Correctness is the release gate, not a tradeable average. Among candidates that meet the same strict correctness and citation requirements, prefer the workflow with lower latency, lower cost, and less complexity. Provider availability and repeatability are a fourth operational constraint: record 429/503 errors, timeouts, retries, and repeated-run variance separately from semantic RAG failures.

For workflow design and evaluation:

- Keep the verified two-LLM baseline as a historical control; do not require the new workflow to retain its router, two model calls, or source-exclusive citation rules.
- Default to the shortest safe path. Extra retrieval, judging, verification, or repair must run conditionally for a demonstrated risk or failure case.
- Do not add a node, prompt rule, or model call without identifying the failure it addresses and recording before/after correctness, citation, latency, and token evidence.
- A candidate is not better merely because it scores higher once; require repeatable results and report quality, speed, cost, and provider reliability together.
- Do not call a workflow production-ready if it achieves accuracy by creating unacceptable latency or cost, or achieves speed by weakening evidence grounding, privacy, or tenant isolation.

## Current priority and decision boundary

Align project Markdown with the owner-confirmed direction first. Do not resume the
superseded four-phase Lean Adaptive/local-model roadmap, patch known questions, or
start another evaluation run just because a historical note says "next".

Keep implementation choices explicitly undecided until the owner resolves them.
Ask before choosing models/providers, reranking, knowledge-base organization,
installation/infrastructure, a new evaluation protocol, or a work sequence. The
owner authorized preserving the supplied current DSL and committing/pushing this
documentation/snapshot update to `main`. That bounded authorization does not
authorize installing Dify, modifying a live workflow/prompt, changing the supplied
DSL, uploading knowledge to a provider, running evaluations, or publishing Dify.

Trusted tenant/project authorization remains required before retrieval. Removing
document-type routing does not authorize cross-tenant search. Project B and
`ISO-01` remain unimplemented/unverified until supported by actual evidence; this
update does not choose the isolation mechanism or schedule its implementation.

## Privacy and secrets

- Nature Footprint sources, derived text, cleaned/OCR outputs, and Dify-upload files are private by default and excluded from Git.
- Keep the GitHub repository private while course deliverables or student information are present.
- Never commit `.env`, API keys, tokens, credentials, `.difypkg` packages, private corpus files, vector indexes, or generated `output/` artifacts.
- Preserve original files and checksums in `knowledge_base/nature_footprint/manifest.json`; do not overwrite provenance sources with cleaned outputs.
- Do not publish, distribute, upload elsewhere, or expose Nature Footprint material without explicit owner permission.
- Cloud inference is the confirmed direction, but no new inference provider or document transfer is authorized by this update. The owner-authorized GitHub push covers the reviewed documentation/current workflow snapshot only. Document the actual model-data boundary before implementation.

## Repository boundaries

- This repository stores AW5 project documentation, evaluation evidence, and Dify DSL snapshots.
- Running Dify applications, whether Cloud or self-hosted, are state separate from Git. After authorized meaningful changes, export a dated DSL; promote a verified artifact in `dify/exports/CURRENT.md` only after validation. Direction/status notes may be updated without claiming a new DSL is verified.
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
