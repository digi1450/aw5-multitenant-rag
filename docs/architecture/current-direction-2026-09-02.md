# Current Direction — Self-hosted Dify, Local Knowledge, Cloud Models

## Authority and status

Confirmed direction recorded on **2026-09-02**, from the project owner's latest
clarification after speaking with the instructor. This is a record of that
decision, not a new technical proposal or evidence of implementation.

This document supersedes the architecture and phase sequence in
[`local-first-hybrid-rag-roadmap.md`](local-first-hybrid-rag-roadmap.md), including
mandatory local embedding inference, continued source-router development, and the
requirement to preserve a two-LLM fast path. Historical workflows and evaluation
results remain intact as controls; they are not instructions for the new design.

If repository notes, old conversations, or agent memory disagree with this
direction, use this document and the owner's newer explicit instructions. Ask the
owner before resolving an ambiguity or selecting an undecided implementation.

## Current workflow is recorded separately

On the same date, the owner supplied **AW5-RAG 1.2** as the current workflow. See
the [current export pointer](../../dify/exports/CURRENT.md) and
[snapshot record](../../dify/exports/aw5-rag-1.2-current-2026-09-02.md).
It still has LLM 1 routing and separate TOR/SDS/ER retrieval. It has been preserved
without modification, not converted into the target described below. Recording its
existing models/settings does not select them for the new architecture.

## Confirmed direction

- Run **Dify self-hosted on the owner's computer**, which serves as the project
  server. This is the senior-project deployment target, not a claim of production
  readiness or a requirement to buy a separate server.
- Keep the **knowledge/files and their persistent storage locally** on that
  computer/server, including source documents, derived text/chunks, and the stored
  index. Existing Dify Cloud knowledge bases have not been migrated by this decision.
- Use **cloud APIs for models**, including embeddings and answer generation, and
  reranking if a reranker is selected. Local model serving or a GPU is not required
  by the current direction.
- Use **one Knowledge Retrieval node** to search the authorized project corpus,
  rather than document-specific TOR/SDS/ER retrieval branches.
- Do not use `use_tor`, `use_sds`, or `use_er` as a model-selected hard gate in the
  new workflow. Mentioning a document in the question does not by itself exclude
  evidence in other authorized documents.
- Keep prompts **generic and evidence-grounded**: no per-file descriptions,
  document-role routing rules, known evaluation questions, expected answers,
  answer identifiers, worked examples, or question-specific exceptions embedded
  in prompts to force a test to pass. New files must not require another routing
  node or a rewrite of the system prompt.
- Keep the old workflow and its evidence separate from the new design. Do not
  overwrite the baseline to implement the new direction.

The agreed simplification is one retrieval step followed by grounded answer
generation. This is a conceptual outline, **not a validated or final DSL**:

```text
User question -> Knowledge Retrieval -> Answer LLM -> Answer
```

One retrieval node does not decide whether there will be one or several knowledge
bases, nor require every file format to use the same parser or chunking method.
Any query-rewriting/history step and any reranking configuration remain undecided.

## Retrieval scope and citations

Search across relevant documents **within trusted tenant/project authorization**.
Removing document-type routing must not remove access control. Identity and scope
must be authorized by the backend, not granted by user text or an untrusted
frontend selector; their implementation and isolation are not yet verified.

Retrieved evidence, evidence used in the answer, and displayed citations are
different things. Do not lock the new workflow to a predetermined citation count
or source list derived from router flags. Cite evidence that actually supports the
answer, preserve its real provenance, and distinguish documents where they differ.
Searching another document does not make it evidence of what the named document
itself says. Insufficient retrieved evidence is not proof that the entire knowledge
base contains no answer.

## Local storage is not zero disclosure

Cloud model calls still transmit data outside the computer/server:

| Model call | Data sent when that call is used |
| --- | --- |
| Cloud embedding | Document chunk text during indexing; query text for query embeddings |
| Cloud reranker, if selected | Query and candidate chunk text submitted for scoring |
| Cloud answer LLM | Question, selected evidence, and any history/metadata explicitly included in the request |

Consequently, do not claim that only final Top-K chunks ever leave the machine, or
that local file storage prevents cloud providers from receiving document content.
Model/provider selection and the associated handling of private material still
need approval. This documentation/snapshot update authorizes no inference calls or
knowledge uploads; the separately authorized GitHub push is limited to reviewed
project documentation and the supplied workflow configuration.

## Not yet decided

- Model names, providers, pricing choices, or any requirement to match a future
  local model. BGE-M3, a particular reranker, and earlier proposed vendors are ideas,
  not approved selections.
- Whether to use reranking; search/fusion mode, Top K, thresholds, and other tuning.
- Knowledge-base organization, upload/ingestion design, parsers, chunking, and the
  concrete tenant/project authorization mechanism.
- Dify version and installation details. Docker/Compose is an option, not a
  completed installation or a newly mandated implementation in this record.
- Storage/vector database product, custom retrieval service, External Knowledge
  API, or additional infrastructure. None is selected by the one-node decision.
- Conversation history, query rewriting, retries, and detailed answer/citation
  presentation behavior.
- The revised evaluation protocol and implementation sequence. Do not reinterpret
  old scores under a new rubric or start new tests without authorization.

## Immediate scope

The owner authorized aligning Markdown, preserving the supplied current workflow
export, and committing/pushing that update to `main`. The supplied DSL is retained
byte-for-byte; no live workflow, model, corpus, index, or service is changed.
This is bounded authorization for the current documentation/snapshot update, not
standing permission for later commits or deployment. Do not install, migrate, tune,
evaluate, or Publish as a consequence of reading this document. Ask the owner
before the next implementation decision.
