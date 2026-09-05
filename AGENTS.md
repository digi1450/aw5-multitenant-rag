# AW5 Repository Guidance for Agents

## Project purpose

AW5 is a senior-project repository for a multi-tenant conversational assistant that retrieves evidence from selected SDLC project artifacts. It does not claim to perform the entire SDLC. The current case study uses Nature Footprint TOR, System Design Specification, and ER/dbdiagram artifacts.

## Read first

Before planning or changing the project, read these files in order:

1. `README.md` — current direction, historical evidence, and unresolved decisions.
2. `docs/architecture/current-direction-2026-09-02.md` — authoritative owner-confirmed architecture; supersedes the old locked roadmap.
3. `docs/architecture/tenant-project-boundary-2026-09-03.md` — authoritative definition that one AW5 tenant is one project and the required isolation boundary.
4. `docs/research/research-evidence-inventory.md` — chronological evidence map, raw-artifact locations, verified/partial/missing boundaries, and Git/local classification.
5. `dify/exports/CURRENT.md` — owner-confirmed self-hosted main workflow, previous snapshots, frozen baseline, and historical candidates.
6. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md` — historical baseline accuracy/latency/cost evidence and demonstrated failures.
7. `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md` — historical scored `19/19` RAG evidence and its limits.
8. `knowledge_base/nature_footprint/evaluation/evaluation-suite-v1.md` — legacy evaluation definitions, including the unexecuted `ISO-01` fixture; source-router expectations are not the new architecture contract.
9. `docs/course-requirements/ds1-ds3-requirements.md` — instructor-supplied deliverable requirements.
10. `knowledge_base/nature_footprint/README.md` and `manifest.json` — corpus provenance and ingestion boundaries.

Do not infer the latest workflow from export filenames alone. Follow `dify/exports/CURRENT.md` for artifacts and the current-direction document for design intent. Newer explicit owner instructions supersede older repository plans or agent memory; ask before resolving ambiguity.

## Evidence and status rules

- Separate **verified**, **not verified**, and **planned** work. A plan, prompt, README statement, or configuration is not test evidence by itself.
- The owner identified `dify/exports/aw5-rag-self-hosted-main-2026-09-04.yml`
  as the current main workflow. Its byte-identical preservation and static
  configuration are verified, not its runtime behavior, Published/draft state,
  quality, latency, cost, citations, or tenant isolation. It must not inherit old
  evaluation scores.
- The historical RAG baseline run has `19/19` strict passes, while the 2026-08-28 regression scored `16/19` strict after bounded retry under the legacy rubric. This does not prove the new architecture, stability, production readiness, multi-tenant isolation, or conversation memory.
- `ISO-01` is N/A until a synthetic Project B tenant fixture and trusted backend project-tenant filtering exist.
- The verified DSL/evaluation baseline is committed on `origin/main` at `64418f8`. The working tree may contain newer documentation, so inspect `git status` before making a current repository-state claim. The Dify Cloud app is maintained separately and does not synchronize automatically with Git.
- The baseline export records a saved draft on 2026-08-25; later dated traces and candidate reports are separate evidence. Check the live application before claiming that it is currently Published or unchanged.
- Do not describe the assistant as doing the whole SDLC. Describe it as retrieving and tracing evidence across selected SDLC artifacts.

## Current architecture direction — confirmed 2026-09-02

- Dify and persistent knowledge/files run on the owner's computer, acting as the project server. Models use cloud APIs: embeddings, answer LLM, and reranker if one is selected.
- Business identity revised and locked 2026-09-03: one AW5 tenant is one software project, and `tenant_id` is the sole project-scope identifier. Do not introduce a separate project ID field. The earlier Team -> Projects interpretation is superseded.
- The first/current tenant is `tenant_id = 1`, with `tenant_name = Nature Footprint`; the name is a display label and is not an authorization key.
- Dify's internal `tenant_id` means Workspace and is distinct from the AW5 project tenant ID; qualify the identifier in code and documentation.
- The trusted backend must derive and enforce the project tenant ID from authenticated project membership before retrieval. User text, model output, and untrusted client IDs cannot grant scope.
- Use one Knowledge Retrieval node over the authorized corpus; do not split retrieval into TOR/SDS/ER branches or gate it with `use_tor` / `use_sds` / `use_er`.
- Current Knowledge Base layout confirmed 2026-09-03: use one Knowledge Base per primary file. Nature Footprint therefore has three Knowledge Bases for `Attach_TOR_1.pdf`, `System Design Specification.pdf`, and `ER_dbdiagram.txt`, all connected to the same retrieval node.
- Do not hard-filter to a document merely because the question names it. Preserve actual source attribution; broader retrieval does not permit claiming that one document says something found only in another.
- Prompts must be generic: no per-file descriptions, test questions, expected answers, worked examples, or case-specific exceptions to force known tests to pass.
- Adding a primary file means adding its own Knowledge Base to the same retrieval node; it must not require another routing node or a system-prompt update. The current export records the current model, retrieval and history settings; future changes require evidence. Ingestion/chunking details and trusted isolation enforcement remain under development.
- Local storage is not zero disclosure: cloud embedding receives chunk/query text; cloud reranking receives candidates; answer generation receives the selected context. Do not claim that only final Top-K evidence leaves the computer.
- Preserve old workflows as controls, not as a required design template. The simple workflow graph is now captured in the 2026-09-04 main export, but it has not been formally validated.

Full decisions and open questions: `docs/architecture/current-direction-2026-09-02.md`.

## Current self-hosted main workflow — owner-confirmed 2026-09-04

`dify/exports/aw5-rag-self-hosted-main-2026-09-04.yml` is the owner-confirmed
current main export. It uses `User Input -> Knowledge Retrieval -> LLM -> Answer`:
4 nodes / 3 edges / 1 LLM node. One retrieval node references the three current
Knowledge Bases. Its weighted retrieval is `0.7` semantic/vector and `0.3`
keyword, Top K `10`, with reranking and score threshold disabled. The answer model
is `gemini-3.5-flash`; conversation memory is enabled with a window of 10.

Use `dify/exports/CURRENT.md` and the linked snapshot record for exact current-file
configuration. Preserve the export without editing its prompt or settings. Static
inspection does not establish runtime quality, Published/draft state, live-app
equality, or trusted AW5 `tenant_id` enforcement. Metadata filtering is disabled,
so this graph alone does not prove project-tenant isolation.

## Previous owner-confirmed snapshot — 2026-09-02

`dify/exports/aw5-rag-1.2-current-2026-09-02.yml` is the previous current-state
snapshot. It uses LLM 1, Route Queries, three retrieval nodes, Merge Context,
LLM 2, and Answer: 9 nodes / 10 edges. Retain it as historical evidence, separate
from the frozen baseline and Lean Adaptive v1.2 candidate.

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

Treat the settings in the owner-confirmed current main export as recorded current
state, not as proven optimal defaults. Ask before changing models/providers,
reranking, ingestion/chunking details, installation/infrastructure, the evaluation
protocol, or the work sequence. Preserving and documenting a supplied export does
not authorize modifying a live workflow/prompt, uploading knowledge to a provider,
running evaluations, or publishing Dify.

Trusted project-tenant authorization remains required before retrieval. Removing
document-type routing does not authorize cross-tenant (cross-project) search. Project B and
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
- Running Dify applications, whether Cloud or self-hosted, are state separate from Git. After authorized meaningful changes, export a dated DSL. `dify/exports/CURRENT.md` may record an owner-confirmed current workflow while separately stating its static and runtime validation status; do not infer validation from promotion alone.
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

## Research-evidence handoff checkpoints

Runtime-testing tasks produce the experiment evidence; the scheduled
`AW5 Daily Research Evidence` heartbeat inventories and summarizes evidence that
already exists. The schedule is a collector, not an evaluation runner, and must
not be relied on to reconstruct transient runtime evidence after a test has
finished. Capture the smallest consistent evidence set that is sufficient to
reproduce the run, verify its conclusions, and explain material anomalies; do not
collect runtime data merely because it is available.

- Before an authorized meaningful Dify change, preserve a read-only pre-change
  state or identify the exact existing evidence package that the owner accepts
  as the comparison state. Record the app, Draft/Published status, workflow or
  export identifier, prompt hash, model, retrieval configuration, Knowledge Base
  identifiers, corpus/version references, Dify version, timestamp, and intended
  change to the extent they are available.
- After the change, capture a post-change state before changing another variable.
  State exactly what changed and retain the previous state for comparison.
- After every authorized bounded runtime diagnostic, create or update an atomic
  local evidence package under
  `output/research-evidence/experiments/<dated-experiment>/` with `report.md`,
  `evidence.json`, and `manifest.json`.
- The minimum evidence set for a candidate or formal run is: evidence
  classification; exact configuration/version identity; corpus version or safe
  checksum references; exact questions and rubric when applicable; answers;
  retrieved-source identifiers, ranks, and scores when available; correctness
  and citation results; end-to-end and material node-latency summaries; reported
  token/cost scope; provider failures; and limitations. Use a consistent schema
  across comparable runs.
- Preserve detailed runtime evidence such as full SSE events, node
  inputs/outputs, generated context, Docker/plugin logs, and retry traces only
  when needed for an authorized diagnostic, a failed case, an anomalous latency
  or cost result, or a formal methodology that explicitly requires it. Keep only
  the relevant time window and fields.
- For owner-directed diagnostics against the local Dify runtime, use a 20-second
  per-attempt cutoff unless an explicitly approved protocol sets another limit.
  If an attempt exceeds the cutoff, stop the Dify task when its task identifier
  is available, record it as a stalled operational attempt, and retry once with
  a fresh conversation. If the retry also exceeds the cutoff, stop and report
  the repeated stall instead of continuing. Do not use a stalled or aborted
  attempt as representative latency or as the semantic result when a completed
  retry exists; retain it separately as reliability/incident evidence.
- Do not collect unrelated logs, full database dumps, vector indexes, secrets, or
  duplicate private corpus content as publication evidence.
- Classify each package as `exploratory diagnostic`, `formal evaluation`,
  `incident evidence`, or `release evidence`. Do not promote manual observations
  or exploratory results to formal evaluation evidence.
- Run a formal evaluation only with explicit owner authorization and against a
  frozen workflow, prompt, corpus version, question suite, rubric, and recorded
  environment.
- Keep experiment packages local-only by default. Do not copy private corpus
  text, raw retrieved chunks, credentials, API keys, `.env` contents, Dify
  databases, or vector-index contents into Git. Publication-facing artifacts
  must be separately sanitized and reviewed while retaining local provenance and
  checksums.
- The scheduled collector may hash, classify, compare, and summarize completed
  evidence packages. It must not run tests, modify Dify or Docker, change an
  evidence classification, or commit local-only evidence unless the owner has
  separately authorized that action and the schedule has been updated for it.

## Future code directories

When frontend and backend implementation begins, add scoped `AGENTS.md` files inside those directories for framework-specific commands, tests, style, and security rules. The root rules in this file continue to apply unless a more specific nested rule adds stricter guidance.
