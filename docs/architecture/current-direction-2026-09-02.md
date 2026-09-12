# Current Direction — Self-hosted Dify, Local Knowledge, Cloud Models

## Authority and status

Confirmed direction recorded on **2026-09-02**, from the project owner's latest
clarification after speaking with the instructor. This is a record of that
decision, not a new technical proposal or evidence of implementation.

Later on 2026-09-02, the owner approved a concrete local Docker Compose
installation. Dify 1.17.0 is installed and its administrator setup page verified;
see the [installation record](dify-local-installation-2026-09-02.md). At that date,
this resolved the base installation/version/storage-product choices below but did
not yet implement the target workflow or choose models/providers.

The first owner-confirmed self-hosted main workflow was captured on 2026-09-04.
The owner promoted the Published five-node successor on 2026-09-06; see the
current-workflow section below.

This document supersedes the architecture and phase sequence in
[`local-first-hybrid-rag-roadmap.md`](local-first-hybrid-rag-roadmap.md), including
mandatory local embedding inference, continued source-router development, and the
requirement to preserve a two-LLM fast path. Historical workflows and evaluation
results remain intact as controls; they are not instructions for the new design.

If repository notes, old conversations, or agent memory disagree with this
direction, use this document and the owner's newer explicit instructions. Ask the
owner before resolving an ambiguity or selecting an undecided implementation.

On 2026-09-03, the owner revised and locked the business identity and isolation
boundary: one AW5 tenant is one software project, and `tenant_id` is the sole
project-scope identifier. The first/current tenant is `tenant_id = 1`, named
`Nature Footprint`. See the authoritative
[tenant/project identity](tenant-project-boundary-2026-09-03.md). This supersedes
the earlier same-day Team -> Projects interpretation while leaving the concrete
filtering implementation open.

## Current workflow is recorded separately

On 2026-09-06, the owner supplied the Published **AW5-RAG Test** export and
promoted it to the project's current main development workflow. See the
[current export pointer](../../dify/exports/CURRENT.md) and
[snapshot record](../../dify/exports/aw5-rag-self-hosted-main-2026-09-06.md).
Its graph is `User Input -> Knowledge Retrieval -> Code -> LLM -> Answer`, with
the three current Knowledge Bases connected to one retrieval node. The Code node
adds generic source metadata to retrieved content; it does not route or filter
documents. The export is preserved without modification, and the Published path
has targeted runtime evidence. It has not received a formal quality,
repeatability, citation, or tenant-isolation evaluation.

The 2026-09-04 four-node main and 2026-09-02 AW5-RAG 1.2 export remain preserved
as previous snapshots and historical controls.

Later registry-backed development candidates and their unresolved deployment
boundaries are recorded separately. See
[`Runtime File Registry and Database Policy`](runtime-registry-and-database-policy-2026-09-13.md)
and [`Chatbot Delivery Options`](chatbot-delivery-options-2026-09-13.md). These
records do not supersede the current-main pointer or turn an undecided delivery
option into an implementation decision.

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
- For the current Nature Footprint tenant, connect that one retrieval node to
  **three Knowledge Bases separated by primary file**:
  `Attach_TOR_1.pdf`, `System Design Specification.pdf`, and `er-dbdiagram.txt`.
  Each future primary file receives its own Knowledge Base and is added to the
  same retrieval node; it does not receive another routing/retrieval branch.
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

The agreed design uses one retrieval step, deterministic source enrichment and
grounded answer generation. The 2026-09-06 main export implements this graph,
while general runtime behavior remains to be formally validated:

```text
User question -> Knowledge Retrieval -> Source enrichment -> Answer LLM -> Answer
```

The three Knowledge Bases may use parser and chunking settings appropriate to
their file formats while remaining searchable through the same retrieval node.
The current export uses conversation memory and no reranker. Future changes to
query rewriting, history behavior, or reranking require comparative evidence.

## Retrieval scope and citations

Search across relevant documents **within trusted project-tenant authorization**.
Removing document-type routing must not remove access control. Identity and scope
must be authorized by the backend, not granted by user text or an untrusted
frontend selector; their implementation and isolation are not yet verified.

For AW5, one business tenant is one software project. `tenant_id` is the canonical
and only project-scope identifier; no separate project ID field is used. The
trusted backend must derive and enforce that project-tenant identity from
authenticated project membership. Dify's internal `tenant_id` means its Workspace
and must not be confused with the AW5 project tenant ID.

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

- Whether the current exported model/provider and retrieval settings should be
  retained after evaluation. They record the current workflow, not a proven optimum.
- Whether to add reranking or change search/fusion mode, Top K, thresholds, and
  other tuning.
- Upload/ingestion design, parsers, chunking, and the concrete mechanism that
  enforces the now-defined `tenant_id` boundary. The current corpus layout of one
  Knowledge Base per primary file is decided.
- Additional infrastructure beyond the subsequently approved Dify 1.17.0
  Docker Compose installation using PostgreSQL and Weaviate. Custom retrieval
  services and External Knowledge API use remain undecided.
- Whether to retain the exported conversation-memory window of 10; query rewriting,
  retries, and detailed answer/citation presentation behavior.
- The revised evaluation protocol and implementation sequence. Do not reinterpret
  old scores under a new rubric or start new tests without authorization.

## Original documentation scope (before the later installation approval)

The owner authorized aligning Markdown, preserving the supplied current workflow
export, and committing/pushing that update to `main`. The supplied DSL is retained
byte-for-byte; no live workflow, model, corpus, index, or service is changed.
This is bounded authorization for the current documentation/snapshot update, not
standing permission for later commits or deployment. Do not install, migrate, tune,
evaluate, or Publish as a consequence of reading this document. Ask the owner
before the next implementation decision.
