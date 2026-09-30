# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

**Target direction updated 2026-09-02; local Dify 1.17.0 is installed, and the
owner promoted the Published five-node self-hosted workflow as the current main
workflow on 2026-09-06. Its reviewed DSL snapshot and targeted diagnostic are
recorded, but it has not received a formal evaluation.**

A separate, newer six-node live Published state received an owner-authorized
20-case real-use-case evaluation on 2026-09-07. It produced 13 pass, 4 partial
and 3 fail after repeated operational retries, with 11 timeouts across 39
attempts. The owner then supplied its exact export, now preserved as an
[evaluated snapshot](dify/exports/aw5-rag-real-use-case-evaluated-2026-09-07.yml).
It differs from the current-main export, so the result does not validate or
promote the current main. See the sanitized
[evaluation summary](docs/research/self-hosted-real-use-case-evaluation-2026-09-07.md).

Installation location, checks and operating instructions are recorded in the
[local installation record](docs/architecture/dify-local-installation-2026-09-02.md).
The owner's latest clarification after consulting the
instructor is recorded in
[`Current architecture direction`](docs/architecture/current-direction-2026-09-02.md).
The owner-confirmed business identity is recorded separately in
[`Tenant and project identity`](docs/architecture/tenant-project-boundary-2026-09-03.md).

- **Dify self-hosted and knowledge/files stored on the owner's computer**, acting as
  the project server.
- **Cloud models** for embeddings and answer generation, and reranking if selected.
- **One Knowledge Retrieval node**, searching across the authorized corpus rather
  than hard-gating TOR/SDS/ER through source-router flags.
- **Three Knowledge Bases for the current tenant**, one for each primary file:
  TOR, SDS, and ER/dbdiagram. All three connect to the same retrieval node.
- **One tenant is one software project**; `tenant_id` is the sole project-scope
  identifier and is derived from trusted project membership.
- **Current tenant:** `tenant_id = 1`, `tenant_name = Nature Footprint`.
- **Generic prompts**, without file-specific descriptions, routing rules, examples,
  known questions, expected answers, or exceptions designed to pass particular tests.
- **Preserve old workflows as historical controls**; the self-hosted main workflow
  is maintained as a separate dated export.

The previous four-phase Lean Adaptive/local-embedding roadmap is superseded, not
the current task list. The current export records the models and retrieval
settings in use. Future model, reranking, ingestion/chunking, and evaluation
changes require evidence rather than assumptions inherited from historical flows.

The dated research history, raw-evidence locations, current gaps and Git/local
classification are maintained in the
[`Research Evidence Inventory`](docs/research/research-evidence-inventory.md).
Historical scores in that inventory remain attached to their original workflows
and must not be reported as validation of the self-hosted target.

## Discord and AW5 backend — implementation update 2026-09-30

The Discord adapter now calls a separate AW5 backend for current role checks,
project selection, ticket state, questions and file inventory. The backend owns
its PostgreSQL registry and Dify credentials, and reads the Published Retrieval
selection through a restricted Dify database view. The administrator still
Publishes using Dify's UI; no project JSON or manual user-ID enrollment is needed.

The existing AW5 Compose deployment runs separate PostgreSQL, API and bot
containers. A live ticket and post-fix answer were confirmed after the Docker
migration, and the focused offline suite passes 27 tests. This is demo/incident
evidence, not formal RAG evaluation or cross-project isolation proof. Project B
and the remaining operational/security work are recorded in the
[current backend/Discord handoff](docs/architecture/aw5-backend-discord-handoff-2026-09-30.md).
See [backend setup](aw5_backend/README.md) and [bot operation](discord_bot/README.md).
The owner-confirmed main Dify workflow below remains a separate evidence track.

## Current main workflow — owner-confirmed 2026-09-06

The owner supplied the Published **AW5-RAG Test** export and promoted it to the
project's current main development workflow. Its
[DSL snapshot](dify/exports/aw5-rag-self-hosted-main-2026-09-06.yml) is preserved
byte-for-byte, with [configuration and status notes](dify/exports/aw5-rag-self-hosted-main-2026-09-06.md).
It has **5 nodes / 4 edges**:
`User Input -> Knowledge Retrieval -> Code -> LLM -> Answer`. The single
retrieval node searches the three current Knowledge Bases. The deterministic
Code node adds retrieved `document_name` and `dataset_name` values to the content
seen by the LLM; it does not route or filter by document.

The Published five-node path and source prefixes in the rendered LLM prompts were
verified. A [targeted five-case diagnostic](docs/research/self-hosted-source-prefix-diagnostic-2026-09-06.md)
produced 4 pass, 1 partial and 0 fail without timeout or retry. This is
exploratory evidence, not a formal evaluation, repeatability result, production
readiness claim or tenant-isolation test. The 2026-09-04 four-node workflow and
AW5-RAG 1.2 remain previous snapshots.

## Historical implementation and evaluation evidence

These are dated records, not proof of the new design or current live application:

- DS1 Project Concept was submitted.
- The private Nature Footprint corpus is prepared locally for controlled RAG experiments.
- The historical Dify source-routed Chatflow has separate TOR, SDS, and ER retrieval paths.
- The frozen baseline export is `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`; `dify/exports/CURRENT.md` records its hash and frozen settings.
- The 2026-08-25 evaluation achieved strict pass `19/19` under the legacy suite; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`.
- The final export and its evaluation evidence are committed and available on `origin/main`.
- The 2026-08-28 Service API regression confirmed the baseline-shaped 9-step graph, two LLM calls, route match `19/19`, and eventual citation boundaries `19/19`. Its strict semantic score was `16/19`, median latency `13.87 s`, and median usage `4,856` tokens per primary case; see `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md`.
- The 2026-08-27 Route Guard candidate adds conditional retrieval, deterministic route checks, and ER Top K 7. Its final revision has recorded structural checks and a seven-question smoke test, not a full verified regression; it is not promoted.
- The 2026-08-29 Lean Adaptive v1–v1.4 artifacts and smoke reports are historical source-routing experiments. v1 returned a complete six-table answer in the first `ER-01` smoke but failed the old source-exclusive citation check. Two v1.1 runs had complete answers but zero citations. Their follow-up artifacts and dated results remain available; they are not the next implementation targets.
- The [v1.4 full report](knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-29-lean-adaptive-v1.4-full.md) records provisional semantic `19/19` after a provider retry, but explicitly does not claim strict `19/19` citation validation. This historical experiment is not evidence that the new architecture has been tested.

Not yet verified or complete:

- The current main workflow export and its file hash are recorded, and the
  Published five-node runtime path was independently checked. Only a targeted
  five-case diagnostic exists; general correctness and repeatability remain
  unverified, and Dify does not synchronize automatically with Git.
- The historical baseline result was `19/19`, but the 2026-08-28 regression was `16/19` strict after bounded retry. Treat repeatability as unresolved and do not quote the historical score as a current stability guarantee.
- The 2026-08-27 candidate is not promoted as the verified correctness baseline; the earlier conditional-gating revision scored `12/19`, while the final Route Guard revision has only a seven-question smoke test so far.
- Project B is another real organizational software project, not a synthetic
  scoring fixture. `ISO-01` remains N/A until at least two real project tenants
  are onboarded and the trusted backend project-tenant filter is tested with
  owner-approved controlled evidence.
- A local Discord demo adapter checks the member's current configured Discord
  project role before sending questions to a tenant-configured Dify Chatflow;
  manual user-ID registration is no longer required. Its
  two-project selector has offline unit tests; Project B onboarding, trusted
  cross-project retrieval isolation, production deployment, and formal adapter
  evaluation remain unverified.

## Immediate scope

The earlier documentation/current-snapshot update had bounded commit/push
authorization. The owner subsequently authorized and completed the local Dify
foundation, created the administrator account, configured model providers,
installed the signed Gemini Embedding 2 (AW5) plugin, and created the three
Knowledge Bases. The synthetic embedding pilot and a targeted real-corpus
diagnostic are recorded. The current self-hosted workflow has a reviewed DSL
export and verified Published path. It still needs formal validation before its
general answer quality, repeatability, citations, or tenant isolation can be
described as verified.

Old evaluation questions/results remain historical evidence. Do not copy their
answers into prompts or enforce their router/source-exclusive expectations on the
new architecture. Any revised evaluation protocol requires separate agreement;
past scores must not be silently rescored.

## Main RAG challenge

The project must optimize three objectives together:

1. answer accurately and only from sufficient evidence;
2. answer quickly enough for practical interactive use; and
3. keep model/API cost bounded and observable.

Accuracy and evidence safety are release gates. When two workflows meet the same strict quality bar, prefer the one with lower p50/p95 latency, fewer model calls, fewer tokens, and simpler failure handling. Provider errors and latency spikes must be measured separately from semantic failures so architecture decisions are based on comparable evidence rather than a single aggregate score.

## Repository structure

```text
docs/
  architecture/              Current direction and superseded architecture notes
  course-requirements/       Official DS1–DS3 submission requirements
  deliverables/              Submitted and working deliverables
  research/                  Evidence inventory and publication-oriented records
dify/                        Dify workflow export instructions/artifacts
discord_bot/                 Local Discord ticket and Dify demo adapter
knowledge_base/
  nature_footprint/          Publishable metadata and evaluation material
```

## Privacy boundary

The Nature Footprint source documents and derived text are private project material. They are intentionally excluded from Git. Only metadata, corpus notes, and evaluation questions are version-controlled until publication permission is confirmed.

The GitHub repository must remain **Private** while student information and course deliverables are present.

The target keeps persistent knowledge/files locally, but cloud embedding calls send
document chunks and query text to the provider. Cloud reranking, if selected, sends
candidate chunks; answer generation sends selected evidence. **Local storage is not
zero disclosure**, and only-final-Top-K disclosure is not a valid claim for this
design. Provider selection and new transfers of private material need approval.

## Dify workflow

Running Dify applications are maintained separately from this repository. After authorized meaningful changes, export DSL/YAML under `dify/exports/`; never commit API keys or provider credentials. [`dify/exports/CURRENT.md`](dify/exports/CURRENT.md) identifies the owner-confirmed self-hosted main workflow, the previous AW5-RAG 1.2 snapshot, historical artifacts, and the frozen control separately.

Custom Dify plugins are maintained in separate Git repositories and are not versioned in this repository.

## Discord demo adapter

The local Discord bot accepts questions in private tickets and forwards them to
the configured Dify Chatflow after checking the member's current project role. See
[its setup guide](discord_bot/README.md) and the
[dated implementation handoff](docs/architecture/discord-bot-demo-handoff-2026-09-28.md).
