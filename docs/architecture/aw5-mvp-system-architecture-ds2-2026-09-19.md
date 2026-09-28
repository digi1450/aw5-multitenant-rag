# AW5 MVP System Architecture for DS2

## Document status

- **Classification:** proposed DS2 architecture, not an implementation record.
- **Prepared:** 2026-09-19.
- **Purpose:** provide a reviewable system-level design for the DS2 Requirements
  Specification and mockup/demonstration section.
- **Authority boundary:** repository evidence remains authoritative for current
  implementation status. This design does not promote a Dify candidate, prove
  tenant isolation, or claim that the Teams integration exists.

The later [Discord demo handoff](discord-bot-demo-handoff-2026-09-28.md)
records a separate local adapter and its evidence limits. The Teams design
below remains a proposal.

## Architecture objective

AW5 is a multi-tenant conversational assistant that retrieves and traces evidence
from selected SDLC project artifacts. It is not an end-to-end SDLC automation
platform. For the MVP, authenticated project members ask questions in a private
Microsoft Teams bot conversation and receive an evidence-grounded answer with
source citations, or an explicit insufficient-evidence response.

One AW5 tenant is one software project. The trusted AW5 backend derives the
effective `tenant_id` from authenticated project membership before invoking
retrieval. User text, model output, Teams message content, and caller-supplied
identifiers cannot grant project scope.

## Proposed MVP decisions

| Area | Proposed DS2 decision |
| --- | --- |
| Chat channel | Microsoft Teams personal bot conversation |
| Identity | Microsoft Entra ID single sign-on |
| Project mapping | One Microsoft Team maps to one AW5 project tenant |
| Project roles | Teams Owner -> `project_admin`; Teams Member -> `project_member`; Guest denied by default |
| Privilege boundary | AW5 backend is authoritative; Teams roles are synchronization/provisioning signals |
| System operator | Separate AW5 operational role; never granted automatically from Teams Owner |
| Tenant routing | One Dify app per AW5 tenant for the MVP |
| Current real tenant | `tenant_id = 1`, display name `Nature Footprint` |
| Second project tenant | Project B, another real organizational software project; planned for separate AW5 onboarding |
| Document onboarding | Administrators control ingestion; ordinary members query only |
| Usage policy | No AW5 per-user question, daily, monthly, or token quota |
| Operational controls | Observe latency, tokens, provider failures, and estimated cost; use per-request timeout and bounded retry without blocking legitimate use through a usage quota |
| Local/cloud boundary | Dify, knowledge files, persistent database, and vector storage remain on the owner's computer; embedding and answer generation use cloud APIs |
| MVP ingress | Teams reaches the trusted backend through a managed public HTTPS ingress; the concrete tunnel/provider remains an implementation selection |

## Component responsibilities

### Microsoft 365 boundary

- **Microsoft Teams personal bot:** private user-facing conversation surface.
- **Microsoft Entra ID:** authenticates the organization user and provides a
  stable identity to the trusted backend.
- **Microsoft Graph:** supplies Team membership/role changes. Notifications do
  not directly authorize retrieval; the backend validates and synchronizes them.

### Trusted AW5 application boundary

- **Teams Bot Adapter:** validates incoming platform requests, normalizes
  messages, and formats answers/citations for Teams.
- **Authorization Service:** resolves authenticated user membership, derives the
  effective AW5 `tenant_id` and role, and fails closed on missing, invalid,
  mismatched, or revoked membership.
- **Membership Store:** records platform identity, AW5 tenant membership, role,
  and synchronization state. The tenant display name is never an authorization
  key.
- **Conversation Service:** scopes conversation state by at least
  `platform_user_id + tenant_id` so project context cannot continue into another
  tenant.
- **Dify Gateway:** retains Dify API credentials server-side and maps an
  authorized AW5 tenant to its Dify application. The client never selects an
  arbitrary Dify app or dataset.
- **Observability:** records authorization outcome, latency, provider errors,
  tokens, and cost estimates. It does not impose an AW5 user usage quota.

### Owner's computer / project server

- **Self-hosted Dify 1.17.0:** current RAG execution environment.
- **Nature Footprint Dify app:** proposed tenant-specific application for
  `tenant_id = 1`. The owner-confirmed current-main five-node workflow remains
  the evidence-backed current snapshot; the tenant-facing gateway is not yet
  implemented.
- **Nature Footprint Knowledge Bases:** one Knowledge Base for each primary file:
  TOR, System Design Specification, and ER/dbdiagram. A single retrieval node
  searches the authorized set.
- **Project B Dify app/Knowledge Bases:** planned tenant-specific environment for
  another real organizational software project; not yet implemented or verified
  in AW5.
- **Local persistence:** PostgreSQL, vector storage, source files, derived chunks,
  and operational state remain local according to the confirmed architecture
  direction.

### External model boundary

- **Cloud embedding API:** receives document chunks during indexing and query
  text during retrieval.
- **Cloud answer LLM:** receives the question, selected evidence, and any history
  explicitly included in the request.
- **Cloud reranker:** not part of the recorded current-main path. If selected
  later, it would receive the query and candidate chunks and would require
  comparative evidence before adoption.

## Authorization invariants

1. Authenticate the platform user before resolving a project.
2. Derive AW5 `tenant_id` from trusted project membership.
3. Deny the request before Dify when membership is absent, revoked, ambiguous,
   or mismatched.
4. Select the Dify application and project corpus only from the trusted mapping.
5. Scope conversation memory to the authenticated user and AW5 tenant.
6. Keep Dify, database, and provider credentials outside Teams and other clients.
7. Treat Microsoft Teams Owner/Member information as an input to synchronization,
   not as the final authorization decision at retrieval time.
8. Never derive System Operator privilege from a Teams project role.

## Primary request flow

1. A project member asks a question in a personal Teams conversation.
2. Teams sends a signed activity and SSO identity token to the Teams Bot Adapter.
3. The adapter validates the platform request and passes the authenticated
   identity to the Authorization Service.
4. The Authorization Service resolves the user's verified membership and active
   AW5 project tenant.
5. If authorization fails, the backend returns an access-denied response and
   does not invoke Dify.
6. If authorization succeeds, the backend derives `tenant_id`, resolves the
   tenant-specific Dify app, and creates or resumes a conversation scoped by
   `platform_user_id + tenant_id`.
7. Dify retrieves evidence from the authorized project Knowledge Bases through
   one retrieval node, enriches source metadata, and sends selected evidence to
   the answer LLM.
8. Dify returns a grounded answer with citations, or an insufficient-evidence
   response.
9. The backend records operational metrics and returns the result to the same
   private Teams conversation.

## Current evidence versus proposed work

### Verified or repository-backed current state

- Dify 1.17.0 is self-hosted on the owner's computer.
- The owner-confirmed current-main export is the five-node 2026-09-06 workflow:
  `User Input -> Knowledge Retrieval -> Code -> LLM -> Answer`.
- One retrieval node references three Nature Footprint Knowledge Bases.
- The current-main export uses weighted retrieval 0.7 semantic / 0.3 keyword,
  Top K 10, and no reranking, score threshold, or metadata filtering.
- The Published path and a five-case exploratory diagnostic are recorded. This
  is not formal validation or tenant-isolation evidence.

### Proposed for the MVP; not yet implemented or verified

- Teams personal bot and Entra ID SSO.
- Microsoft Graph membership/role synchronization.
- Trusted AW5 authorization backend, membership store, and Dify gateway.
- One Team to one AW5 tenant mapping and one Dify app per tenant.
- Per-user/per-tenant conversation mapping.
- Project B onboarding as a separate real project tenant.
- Cross-tenant isolation testing with owner-approved controlled evidence.
- Public HTTPS ingress for Teams callbacks.
- End-to-end authorization, revocation, privacy, and failure-path tests.

## Open implementation selections

The following are intentionally not fixed by the DS2 system-level design:

- the managed HTTPS ingress/tunnel provider;
- the backend programming language and web framework;
- the exact membership database schema and cache policy;
- Graph subscription renewal and reconciliation details;
- the final Dify app-per-tenant versus generic filtered-app topology after MVP;
- production hosting, high availability, disaster recovery, and enterprise SLA;
- retention period and administrator access policy for operational logs;
- future reranking, retrieval tuning, ingestion, and chunking changes.

## Diagrams

- [MVP system architecture overview](diagrams/aw5-mvp-system-architecture-overview-2026-09-19.svg)
- [Authorization and RAG request sequence](diagrams/aw5-mvp-authorization-rag-sequence-2026-09-19.svg)
- PNG previews:
  [overview](diagrams/aw5-mvp-system-architecture-overview-2026-09-19.png) and
  [sequence](diagrams/aw5-mvp-authorization-rag-sequence-2026-09-19.png).
- Editable diagrams.net sources:
  [overview](diagrams/aw5-mvp-system-architecture-overview-2026-09-19.drawio) and
  [sequence](diagrams/aw5-mvp-authorization-rag-sequence-2026-09-19.drawio).
