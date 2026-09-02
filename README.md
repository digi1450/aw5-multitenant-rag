# AW5 — Multi-Tenant RAG-based Conversational AI for SDLC

Senior project repository for a multi-tenant conversational assistant that retrieves evidence from selected Software Development Life Cycle (SDLC) project artifacts.

## Current status

**Target direction updated 2026-09-02; the live implementation has not been changed
by this update.** The owner's latest clarification after consulting the
instructor is recorded in
[`Current architecture direction`](docs/architecture/current-direction-2026-09-02.md).

- **Dify self-hosted and knowledge/files stored on the owner's computer**, acting as
  the project server.
- **Cloud models** for embeddings and answer generation, and reranking if selected.
- **One Knowledge Retrieval node**, searching across the authorized corpus rather
  than hard-gating TOR/SDS/ER through source-router flags.
- **Generic prompts**, without file-specific descriptions, routing rules, examples,
  known questions, expected answers, or exceptions designed to pass particular tests.
- **Preserve the old workflow as a historical control**; build the new design
  separately when implementation is authorized.

The previous four-phase Lean Adaptive/local-embedding roadmap is superseded, not
the current task list. Models/providers, reranking, knowledge-base organization,
installation details, and the implementation/evaluation sequence remain undecided.
Ask the owner before selecting them.

## Current workflow — owner-confirmed 2026-09-02

The owner supplied **AW5-RAG 1.2** as the current workflow. Its
[DSL snapshot](dify/exports/aw5-rag-1.2-current-2026-09-02.yml) is preserved
byte-for-byte, with [configuration and status notes](dify/exports/aw5-rag-1.2-current-2026-09-02.md).
It has **9 nodes / 10 edges**, LLM 1 routing, separate TOR/SDS/ER retrieval, and
Merge Context before LLM 2. Retrieval uses weighted `0.5/0.5`, TOR/SDS Top K **3**,
ER Top K **10**, with reranking disabled.

This is the current-state record, **not the new single-retrieval implementation**
and not Lean Adaptive v1.2. The supplied export was inspected locally; no new run,
evaluation, or Published/draft verification was performed. The baseline's old
scores must not be attributed to this file.

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

- The owner has identified the current workflow export and its file hash is recorded. Exact agreement with a live app, Published/draft state, and any self-hosted deployment have not been independently checked; Dify does not synchronize automatically with Git.
- The historical baseline result was `19/19`, but the 2026-08-28 regression was `16/19` strict after bounded retry. Treat repeatability as unresolved and do not quote the historical score as a current stability guarantee.
- The 2026-08-27 candidate is not promoted as the verified correctness baseline; the earlier conditional-gating revision scored `12/19`, while the final Route Guard revision has only a seven-question smoke test so far.
- `ISO-01` remains N/A until a Project B fixture and a trusted backend tenant/project filter exist.
- Multi-tenant authorization, production deployment, frontend/backend implementation, and conversation-memory behavior are not complete or proven.

## Immediate scope

Synchronize Markdown with the confirmed direction and preserve the supplied current
workflow. The owner has authorized committing and pushing this documentation and
snapshot update to `main`. This is not authorization to install services, modify a
live workflow/prompt, choose models, run evaluations, migrate documents, or Publish
a Dify app. Unresolved implementation decisions still require the owner's input.

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
dify/                        Dify workflow export instructions/artifacts
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

Running Dify applications are maintained separately from this repository. After authorized meaningful changes, export DSL/YAML under `dify/exports/`; never commit API keys or provider credentials. [`dify/exports/CURRENT.md`](dify/exports/CURRENT.md) identifies the owner-confirmed current AW5-RAG 1.2 snapshot, historical artifacts, and the frozen control separately. The new single-retrieval self-hosted direction has no approved implementation snapshot recorded by this update.

Custom Dify plugins are maintained in separate Git repositories and are not versioned in this repository.
