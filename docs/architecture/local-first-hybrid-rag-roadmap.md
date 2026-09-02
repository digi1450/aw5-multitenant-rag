# Local-First Hybrid RAG Roadmap

> **Superseded on 2026-09-02 — historical plan only.** The owner confirmed
> [self-hosted Dify, local knowledge storage, cloud models, and one retrieval node](current-direction-2026-09-02.md).
> The local-embedding requirement, source-router continuation, and four "locked"
> phases below are no longer active instructions. The original plan is retained
> for provenance, not as an implementation checklist. Do not resume it unless the
> owner explicitly approves a new decision.

## Locked architecture direction

AW5 will target a **local-first hybrid RAG** architecture. Original project files,
parsed/OCR text, chunks, embeddings, vector indexes, authorization checks, and
retrieval remain inside infrastructure controlled by the organization. An approved
cloud LLM may receive only the user's question and the minimum authorized evidence
snippets required to answer it.

The current Dify Cloud work is a research and workflow-validation environment. It
is not the final privacy-compliant deployment architecture because its knowledge
base, chunks, vector index, and workflow traces are hosted outside the organization.

## Four locked phases

These phases are ordered and must not be silently replaced, skipped, or collapsed.
Changing their order or architecture boundary requires an explicit project-owner
decision and an update to this document.

### Phase 1 — Portable Lean Adaptive workflow

Continue from the verified two-LLM source-routing baseline. Build only workflow
mechanisms that remain portable to a self-hosted environment:

- source-specific routing and queries;
- evidence-grounded answer contract;
- deterministic answer-coverage checks;
- conditional repair only when the normal answer path fails;
- deterministic insufficient-evidence handling; and
- precise source citations.

Normal requests should remain on the lean path. Every added model call or node must
justify its effect on answer accuracy, p50/p95 latency, and API cost with comparable
evaluation evidence.

### Phase 2 — Early local-hybrid feasibility spike

Before treating the cloud workflow as complete, prove the deployment boundary with
a small safe or synthetic corpus:

- self-host Dify or the selected RAG runtime inside the organization;
- use a local parser/OCR pipeline;
- use a local embedding model;
- use a local vector database or index;
- run retrieval locally; and
- call the approved cloud model only with the question and selected Top-K evidence.

Inspect the actual outbound request or equivalent sanitized trace to verify that
the original file, complete parsed document, full vector index, and unauthorized
chunks are not sent to the cloud model. Phase 2 is an early feasibility check and
may run while Phase 1 is being refined; it is not postponed until Phase 1 is
perfect.

### Phase 3 — Move and re-evaluate on the local retrieval stack

After Phase 2 succeeds, move the Lean Adaptive candidate and the controlled corpus
to the local stack. Recreate ingestion and run retrieval-only checks before testing
answers. Then rerun the same 19 executable evaluation cases and compare against the
cloud baseline on:

- strict answer correctness and completeness;
- citation precision and evidence sufficiency;
- p50 and p95 latency;
- number of model calls and tokens;
- estimated API cost; and
- provider errors versus semantic RAG failures.

Passing on Dify Cloud does not automatically count as passing on the local stack,
because parsing, embeddings, indexing, and retrieval behavior may change.

### Phase 4 — Trusted tenant/project isolation

Enforce scope before retrieval, using backend-authorized identity rather than user
text or an untrusted frontend selector:

- resolve trusted `tenant_id` and `project_id`;
- attach filterable tenant/project metadata to documents or indexes;
- apply authorization filters before semantic or keyword retrieval;
- create the synthetic Project B fixture;
- execute `ISO-01`; and
- prove that Project A cannot retrieve, answer from, or cite Project B.

Add audit logging, rate limits, and sensitive-section/DLP policy around the outbound
cloud-model boundary. Per-request Top-K minimization alone does not prevent a cloud
provider from seeing many parts of a document cumulatively across repeated queries.

## Non-negotiable trust boundary

The organization-controlled environment keeps:

- original files and derived/OCR content;
- embeddings and vector indexes;
- document permissions and tenant/project authorization;
- retrieval and evidence selection; and
- full internal audit records.

The approved cloud model may receive only:

- the current user question;
- the minimum authorized evidence excerpts selected locally; and
- the minimum metadata needed to produce traceable citations.

Cloud embeddings are outside this target boundary because they require sending
document chunks to the embedding provider during ingestion. Any exception requires
an explicit security/privacy decision rather than being introduced as an
implementation convenience.

## Global acceptance objectives

All phases preserve the project's three-way challenge:

1. accurate, complete, evidence-grounded answers;
2. practical interactive latency; and
3. bounded, observable API cost.

Accuracy and evidence isolation are release gates. Among candidates that meet those
gates, prefer the design with lower p50/p95 latency, fewer model calls, fewer tokens,
and simpler failure handling.
