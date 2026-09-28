# AW5 DS2 Requirements Specification — Working Draft

## Document control

| Field | Value |
| --- | --- |
| Project | Multi-Tenant RAG-based Conversational AI for Software Development Lifecycle |
| Topic ID | AW5 |
| Deliverable | DS2 Requirements Specification |
| Status | Working draft for owner review |
| Prepared | 2026-09-19 |
| Target submission | `AW5-RequirementSpec.pdf` |

Related system-level design:
[AW5 MVP System Architecture for DS2](../../../architecture/aw5-mvp-system-architecture-ds2-2026-09-19.md).

This document records the agreed DS2 planning baseline. It specifies the intended
MVP and does not claim that the Microsoft Teams integration, trusted backend,
Project B onboarding, or tenant-isolation controls have been implemented or verified.
The Mockup / Example / Demonstration section is intentionally deferred to a later
DS2 work session.

## 1. System purpose

AW5 is a multi-tenant conversational assistant that retrieves and traces evidence
from selected Software Development Life Cycle project artifacts. Authorized
project members ask natural-language questions and receive evidence-grounded
answers with source citations, or an explicit insufficient-evidence response.

AW5 does not automate the entire SDLC. One AW5 tenant represents one software
project. The canonical project-scope identifier is `tenant_id`; no separate
project ID is introduced. Dify's internal Workspace `tenant_id` is a different
identifier and must not be treated as the AW5 project tenant ID.

## 2. MVP scope

The MVP shall include:

1. A Microsoft Teams personal bot conversation as the user-facing channel.
2. Microsoft Entra ID single sign-on for organization user identity.
3. A trusted AW5 backend that validates platform requests and derives the
   effective AW5 `tenant_id` from authenticated project membership.
4. One Microsoft Team mapped to one AW5 project tenant for the MVP.
5. Project roles `project_member` and `project_admin`, with a separate
   `system_operator` role.
6. Default role synchronization in which Teams Owner maps to `project_admin`,
   Teams Member maps to `project_member`, and Teams Guest is denied unless an
   explicit future policy allows access.
7. One tenant-specific Dify application per AW5 project tenant for the MVP.
8. A real first tenant, `tenant_id = 1`, named `Nature Footprint`.
9. Three Nature Footprint Knowledge Bases, one for each primary artifact: TOR,
   System Design Specification, and ER/dbdiagram.
10. A single Knowledge Retrieval node over the authorized project corpus, with
    generic source enrichment and no per-file routing branches.
11. Evidence-grounded answers with source citations and an explicit
    insufficient-evidence response when the retrieved evidence is inadequate.
12. Conversation state scoped at least by `platform_user_id + tenant_id`.
13. Administrator-controlled document onboarding. Ordinary project members can
    query project evidence but cannot upload documents in the initial MVP.
14. Project B as a second, separate AW5 tenant for another real organizational
    software project, with its own membership, Dify application, and project
    Knowledge Bases.
15. Operational observation of authorization outcomes, latency, tokens,
    provider errors, retries, and estimated API cost.
16. No AW5-enforced per-user question quota, daily/monthly quota, or token quota.
17. Per-request timeout, bounded retry, duplicate-request protection, and access
    revocation as technical and security safeguards rather than usage limits.
18. Self-hosted Dify and persistent project knowledge/files on the owner's
    computer, with cloud APIs for embeddings and answer generation.

## 3. Out of scope for the MVP

The following are outside the MVP:

1. Automating the complete software development lifecycle.
2. Generating or modifying production source code, deployments, or project
   artifacts as an autonomous agent.
3. Arbitrary public document upload or immediate self-service ingestion by all
   members.
4. Guaranteed support for every file format, OCR case, image, or unstructured
   enterprise repository.
5. Simultaneous production support for Microsoft Teams and Discord.
6. A public consumer chatbot or anonymous access.
7. Public high-scale deployment, enterprise high availability, disaster
   recovery, or contractual SLA.
8. Local LLM or local embedding-model serving as a requirement.
9. A guarantee of 100% answer accuracy or provider availability.
10. Hard-coded routing by known questions, corpus-specific filenames, expected
    answers, or test-specific prompt exceptions.
11. Direct Teams-client access to Dify credentials, provider keys, PostgreSQL,
    vector storage, or local project files.
12. Enterprise certification, formal compliance attestation, or a claim of
    production readiness.
13. Fixed numeric response-time or availability targets before a representative
    evaluation protocol and environment are agreed.
14. Detailed DS3-level implementation design, infrastructure hardening, and
    production operations.

## 4. Actors and roles

| Actor / role | Description | MVP permissions |
| --- | --- | --- |
| Project Member | Authenticated member of an authorized project | Ask questions, view own conversation, receive answers and citations for authorized project evidence |
| Project Admin | Project-level administrator | All Project Member permissions; manage project membership mapping and request/control document onboarding |
| System Operator | AW5 operational administrator | Operate backend/Dify, configure tenant-app mappings, inspect authorized operational logs, and recover services; not granted automatically from Teams Owner |
| Microsoft Teams | User-facing conversation platform | Deliver signed bot activities and display responses |
| Microsoft Entra ID | Organization identity provider | Authenticate users and issue identity tokens |
| Microsoft Graph | Membership synchronization source | Notify or expose Team membership and role changes for backend validation |
| Dify | RAG orchestration platform | Retrieve authorized evidence and generate grounded answers through configured model APIs |

## 5. Permission matrix

| Capability | Project Member | Project Admin | System Operator |
| --- | :---: | :---: | :---: |
| Ask questions in authorized tenant | Yes | Yes | Only when explicitly granted project membership |
| View own bot conversation | Yes | Yes | Not as an ordinary chat participant |
| Select among own authorized tenants | Yes | Yes | Only when explicitly granted project membership |
| Upload/onboard project documents | No | Request/control | Execute or administer |
| Manage project membership mapping | No | Yes, within own tenant | Yes, operationally |
| Configure Dify/provider credentials | No | No | Yes |
| Inspect operational logs | No | Limited project-level view if later enabled | Yes, under retention/access policy |
| Grant System Operator privilege | No | No | Separate administrative process only |

## 6. Functional requirements

### 6.1 Identity and authorization

| ID | Requirement |
| --- | --- |
| FR-AUTH-01 | The system shall authenticate users through Microsoft Entra ID before processing a project question. |
| FR-AUTH-02 | The Teams Bot Adapter shall validate the origin and integrity of incoming Teams activities and validate the associated identity token. |
| FR-AUTH-03 | The trusted backend shall resolve the authenticated platform user to current AW5 project membership. |
| FR-AUTH-04 | The backend shall derive the effective AW5 `tenant_id` from verified membership; user text, model output, message content, and caller-supplied IDs shall not grant project scope. |
| FR-AUTH-05 | The backend shall reject the request before Dify or retrieval when membership is missing, invalid, revoked, ambiguous, or mismatched. |
| FR-AUTH-06 | The system shall synchronize or revalidate Teams membership and role changes through trusted Microsoft Graph data. |
| FR-AUTH-07 | When a user belongs to multiple project tenants, the system shall permit selection only from the user's verified memberships. |
| FR-AUTH-08 | The system shall map Teams Owner to `project_admin`, Teams Member to `project_member`, and deny Teams Guest by default for the MVP. |
| FR-AUTH-09 | The system shall manage `system_operator` separately and shall not derive it from a Teams project role. |

### 6.2 Conversation and project context

| ID | Requirement |
| --- | --- |
| FR-CONV-01 | The system shall provide each user with a personal Teams bot conversation. |
| FR-CONV-02 | Ordinary project users shall not view another user's bot conversation through the normal chat interface. |
| FR-CONV-03 | The system shall scope conversation state by at least `platform_user_id + tenant_id`. |
| FR-CONV-04 | Changing the active project tenant shall not reuse conversation memory from the previous tenant. |
| FR-CONV-05 | The system shall accept natural-language questions concerning authorized selected SDLC artifacts. |
| FR-CONV-06 | The system shall return the response to the same authenticated personal conversation that initiated the request. |

### 6.3 Tenant routing and RAG

| ID | Requirement |
| --- | --- |
| FR-RAG-01 | The Dify Gateway shall map an authorized AW5 `tenant_id` to the corresponding tenant-specific Dify application using server-side configuration. |
| FR-RAG-02 | Teams clients shall not receive Dify application keys, model-provider keys, database credentials, or arbitrary dataset identifiers. |
| FR-RAG-03 | Retrieval shall search only the Knowledge Bases assigned to the authorized AW5 tenant. |
| FR-RAG-04 | The Nature Footprint application shall use one Knowledge Retrieval node over its three authorized Knowledge Bases. |
| FR-RAG-05 | The workflow shall preserve actual document provenance and shall not claim that one document contains evidence retrieved only from another document. |
| FR-RAG-06 | The system shall provide citations that identify the evidence sources used to support the answer. |
| FR-RAG-07 | When retrieved evidence is insufficient, the system shall state that sufficient evidence is unavailable rather than inventing an answer. |
| FR-RAG-08 | Prompts and production workflow logic shall remain generic and shall not contain known test questions, expected answers, corpus-specific routing rules, or case-specific exceptions. |
| FR-RAG-09 | Adding a primary file to a tenant shall add its Knowledge Base to the tenant's existing retrieval node without requiring a new document-routing branch. |

### 6.4 Document onboarding

| ID | Requirement |
| --- | --- |
| FR-DOC-01 | Project document onboarding shall be controlled by authorized administrators. |
| FR-DOC-02 | Each onboarded primary file shall be attributable to exactly one AW5 `tenant_id`. |
| FR-DOC-03 | Source files, derived content, chunks, index records where supported, and retrieval results shall preserve tenant attribution and source provenance. |
| FR-DOC-04 | The initial MVP shall not allow ordinary Project Members to upload or immediately ingest arbitrary files. |
| FR-DOC-05 | The system shall expose an onboarding status or operational record sufficient for an administrator to determine whether a document is ready for retrieval. |
| FR-DOC-06 | The system shall preserve original source files and provenance rather than overwriting them with cleaned or derived outputs. |

### 6.5 Operations and observability

| ID | Requirement |
| --- | --- |
| FR-OPS-01 | The system shall record authorization outcome, end-to-end latency, material provider failures, retry outcome, input/output token scope where available, and estimated API cost. |
| FR-OPS-02 | The system shall not use the observed usage data to impose an AW5 per-user question or token quota. |
| FR-OPS-03 | The system shall apply a per-request timeout and bounded retry policy to provider or retrieval stalls. |
| FR-OPS-04 | The system shall avoid duplicate downstream processing when the same platform activity is delivered more than once. |
| FR-OPS-05 | The system shall revoke project access when trusted membership indicates that the user is no longer authorized. |
| FR-OPS-06 | Operational logs shall avoid storing complete private document content unless required for an authorized diagnostic or evaluation. |

### 6.6 Isolation validation

| ID | Requirement |
| --- | --- |
| FR-ISO-01 | The system shall onboard Project B as a separate real organizational project tenant with its own membership, Dify application, and Knowledge Bases. |
| FR-ISO-02 | An authorized Tenant 1 request shall not retrieve Project B evidence, and an authorized Project B request shall not retrieve Tenant 1 evidence. |
| FR-ISO-03 | An unauthorized or manipulated tenant selection shall fail before Dify retrieval. |
| FR-ISO-04 | Isolation validation may use owner-approved controlled marker records within real tenant boundaries so that private project content is not exposed merely to create a test. |
| FR-ISO-05 | Isolation results shall be recorded as evidence before the project claims multi-tenant isolation is verified. |

## 7. Non-functional requirements

### 7.1 Security

| ID | Requirement |
| --- | --- |
| NFR-SEC-01 | Authorization shall be enforced by the trusted backend before retrieval. |
| NFR-SEC-02 | All external bot callbacks and backend API traffic shall use authenticated HTTPS transport. |
| NFR-SEC-03 | Dify, database, model-provider, and platform credentials shall be stored server-side and excluded from client responses, source control, logs, and deliverables. |
| NFR-SEC-04 | The system shall fail closed when identity, membership, tenant mapping, or authorization data is unavailable or inconsistent. |
| NFR-SEC-05 | Project-tenant authorization shall use stable identifiers rather than tenant display names or mutable role names alone. |
| NFR-SEC-06 | Administrative privileges shall follow least privilege and separate project administration from system operation. |

### 7.2 Privacy and data handling

| ID | Requirement |
| --- | --- |
| NFR-PRIV-01 | Persistent source files, derived knowledge, and vector/index storage shall remain on the owner's computer for the MVP. |
| NFR-PRIV-02 | The design shall disclose that cloud embedding receives document chunks and query text, while the answer LLM receives the question and selected evidence/history. |
| NFR-PRIV-03 | Nature Footprint source and derived content shall remain private and shall not be included in Git or public deliverables without permission. |
| NFR-PRIV-04 | Personal chat separation shall not be described as cryptographic secrecy from authorized system administrators. |
| NFR-PRIV-05 | Log retention duration and administrator log-access policy shall be documented before production deployment. |

### 7.3 Answer quality and evidence grounding

| ID | Requirement |
| --- | --- |
| NFR-QUAL-01 | Correctness and evidence grounding shall be release gates rather than tradeable averages against latency or cost. |
| NFR-QUAL-02 | Evaluation shall distinguish answer correctness, citation correctness, insufficient-evidence behavior, and cross-tenant leakage. |
| NFR-QUAL-03 | Historical workflow scores shall not be transferred to the MVP architecture without a new evaluation of the exact configuration. |
| NFR-QUAL-04 | A workflow shall not be called production-ready from a targeted diagnostic, manual observation, or single successful run. |

### 7.4 Performance and reliability

| ID | Requirement |
| --- | --- |
| NFR-PERF-01 | The system shall measure end-to-end p50 and p95 latency over a representative run rather than relying on a single response or mean alone. |
| NFR-PERF-02 | Provider timeout, throttling, unavailability, and retry events shall be reported separately from semantic RAG failures. |
| NFR-PERF-03 | Numeric response-time and availability acceptance thresholds remain TBD until the representative environment and evaluation protocol are agreed. |
| NFR-PERF-04 | The system shall prefer the shortest safe request path that satisfies the correctness, citation, privacy, and isolation requirements. |

### 7.5 Scalability and maintainability

| ID | Requirement |
| --- | --- |
| NFR-MAIN-01 | The logical architecture shall support multiple project tenants; the MVP diagrams show Nature Footprint and Project B as two real organizational projects without limiting the architecture to two tenants. |
| NFR-MAIN-02 | Platform adapter, authorization logic, conversation mapping, and Dify integration shall remain separate components so the chat channel or Dify topology can change later. |
| NFR-MAIN-03 | Adding a primary project file shall not require corpus-specific prompt changes or a new routing branch. |
| NFR-MAIN-04 | Dated Dify exports and evidence records shall preserve reproducibility without including credentials or private corpus content. |
| NFR-MAIN-05 | Current main, candidates, historical controls, and planned architecture shall retain separate status and evidence claims. |

### 7.6 Usability and accessibility

| ID | Requirement |
| --- | --- |
| NFR-USE-01 | Responses shall clearly separate the answer, citations, insufficient-evidence status, and operational error states. |
| NFR-USE-02 | Access-denied responses shall not reveal whether an unauthorized tenant or document exists. |
| NFR-USE-03 | Project selection for a multi-project user shall display only verified memberships and shall clearly identify the active tenant. |
| NFR-USE-04 | The Teams response format shall remain readable within the platform's message and card constraints. |

### 7.7 Cost observability

| ID | Requirement |
| --- | --- |
| NFR-COST-01 | The system shall observe model calls, available token counts, retries, and estimated cost per question or evaluation run. |
| NFR-COST-02 | The MVP shall not block authorized project work through an AW5-defined per-user usage quota. |
| NFR-COST-03 | External provider quotas, outages, or account limits shall be reported as provider constraints rather than represented as AW5 user policy. |

## 8. Primary use cases

| ID | Use case | Expected result |
| --- | --- | --- |
| UC-01 | Authorized member asks a project question | Backend derives the tenant, Dify retrieves only authorized evidence, and Teams displays a grounded answer with citations |
| UC-02 | Authorized member asks a question with insufficient evidence | System returns an explicit insufficient-evidence response without unsupported inference |
| UC-03 | User without current membership sends a question | Backend returns access denied and does not call Dify |
| UC-04 | User belongs to multiple project tenants | User selects only from verified memberships; conversation scope changes with the active tenant |
| UC-05 | Project Admin requests document onboarding | Administrator-controlled process associates the file and derived knowledge with the correct tenant and reports status |
| UC-06 | Teams membership or role changes | Trusted synchronization updates AW5 membership; revoked access no longer authorizes retrieval |
| UC-07 | Isolation test uses conflicting Tenant 1 and Project B facts | Each tenant retrieves only its own evidence; manipulated tenant selection fails before retrieval |
| UC-08 | Model provider times out or returns an error | System applies bounded failure handling, records the provider incident, and returns a clear operational response |

## 9. Acceptance criteria for the MVP

The MVP can be considered functionally ready for a bounded demonstration only
when all of the following have evidence:

1. A valid Teams/Entra user can authenticate and reach the trusted backend.
2. The backend derives the user's authorized `tenant_id` without trusting a
   caller-supplied tenant identifier.
3. A revoked or unauthorized user is denied before Dify retrieval.
4. Nature Footprint questions retrieve only its authorized Knowledge Bases.
5. Answers preserve citations and return an insufficient-evidence response for a
   case with inadequate evidence.
6. Conversation memory is separated by platform user and tenant.
7. Project B is onboarded as a separate real organizational project tenant, and
   a bounded isolation suite using owner-approved controlled evidence shows no
   cross-tenant retrieval in either direction.
8. Provider stalls and errors are recorded separately from answer-quality
   failures.
9. Latency, available token scope, retry events, and estimated API cost are
   captured without imposing an AW5 usage quota.
10. Evidence is attached to the exact workflow/configuration tested and does not
    inherit historical scores.

These criteria do not constitute an enterprise production-readiness, SLA, or
compliance claim.

## 10. Current evidence and implementation status

### Repository-backed current evidence

- Dify 1.17.0 is self-hosted on the owner's computer.
- The owner-confirmed current-main export is the five-node 2026-09-06 workflow:
  `User Input -> Knowledge Retrieval -> Code -> LLM -> Answer`.
- The workflow references three Nature Footprint Knowledge Bases through one
  retrieval node.
- The Published path and a targeted five-case exploratory diagnostic are
  recorded.

### Not yet implemented or verified

- Microsoft Teams personal bot and Entra ID SSO integration.
- Trusted AW5 backend, Membership Store, Conversation Service, and Dify Gateway.
- Microsoft Graph membership synchronization.
- One Team to one AW5 tenant mapping in a running application.
- Project B onboarding as a separate real tenant and bidirectional cross-tenant
  isolation testing.
- General correctness, repeatability, production readiness, and enterprise-scale
  operational characteristics.

## 11. Open decisions and missing information

The following do not block this first requirements draft but must be decided
before implementation or final operational claims:

1. Backend language and framework.
2. Managed HTTPS ingress/tunnel provider for Teams callbacks.
3. Exact membership-store schema, cache lifetime, and Graph reconciliation
   interval.
4. Active-project selection interaction for users in multiple projects.
5. Administrative onboarding interface and detailed document-status states.
6. Conversation-history retention and whether the current Dify memory window of
   10 should remain after evaluation.
7. Operational-log retention duration and project-admin visibility.
8. Numeric response-time, reliability, answer-quality, and citation thresholds.
9. Additional supported file types beyond the current selected artifacts.
10. Whether the post-MVP architecture retains one Dify app per tenant or adopts
    a shared generic app with a separately proven trusted tenant filter.

## 12. Deferred DS2 section

Mockups, UI examples, screenshots, and the demonstration script are deferred by
owner direction. When resumed, they should trace to the requirements above and
must clearly distinguish implemented Dify evidence from proposed Teams/backend
behavior.
