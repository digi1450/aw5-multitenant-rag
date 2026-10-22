# Architecture

## Components

| Component | Responsibility |
|---|---|
| Discord bot | Start panel, project selection, private threads, questions, file listing and closing |
| AW5 API | Current membership checks, project authorization, Published selection validation, Dify requests and local administration |
| AW5 PostgreSQL | Project/role bindings, encrypted app keys, tickets/conversation IDs and provisioning journals |
| Dify | Chatflow execution, Knowledge Bases and retrieval |
| Restricted Dify database reader | Published app/workflow/dataset projection and digest-only app-key binding |
| Cloud provider | Configured embedding and answer models; reranker only if explicitly enabled |

One **AW5 tenant is one software project**. Dify uses the word tenant for a Workspace; these are different identifiers. Project names are display labels, not authorization keys.

## Question flow

1. A Discord member selects an eligible project and opens a private thread.
2. The bot sends the thread, guild, user and question to the AW5 API using its service token.
3. The backend verifies ticket ownership and the member's current Discord roles.
4. It reads the app's Published selection and checks every selected document's AW5 `tenant_id` metadata. Missing/mismatched metadata or an unavailable upstream suspends access.
5. It constructs a query-based source shortlist from the authorized inventory and sends it as `aw5_registry_json`, alongside the question and thread-bound Dify conversation ID.
6. Dify resolves source scope, retrieves evidence, selects context and writes an answer or bounded fallback.
7. The backend stores the conversation ID and returns the answer. The bot posts it in the original thread.

The bot receives neither Dify credentials nor access to Dify's database/Docker socket. Only the backend holds Knowledge and Chatflow credentials. App keys are encrypted in AW5 PostgreSQL using the separately configured Fernet key.

## Chatflow

```text
User Input → Registry parser → Scope Resolver → Metadata-filter builder
 → Knowledge Retrieval → Context selector → Evidence present?
     yes → Writer → Answer
     no  → Fallback
```

The template has 10 nodes, 9 edges, one retrieval node and two LLM nodes. Source selection is dynamic; it does not branch on fixed document types or names. Adding a document requires configuring its Knowledge Base/metadata and connecting it to the same retrieval node.

The reference settings are vector/semantic 0.7, keyword 0.3, Top K 30, no reranker, and at most 15 selected chunks. These are recorded settings, not proven optimal defaults. `has_evidence` means context is nonempty, and `candidate_coverage` tracks selected-source candidates; neither proves semantic completeness or whole-document coverage.

## Administration

`/aw5-admin` is restricted by configured channel and current admin role. It returns an ephemeral one-use link to the loopback portal. Enrollment validates the app-key binding and Published corpus before registering a stable tenant ID and safe project role. The portal can change that role binding or explicitly remove the AW5 registration.

Registration deletion removes AW5 records; it does not delete Dify apps/documents, Discord roles or messages. Provisioning and role changes retain journals for uncertain operations. Inspect `needs_attention` operations before retrying; do not remove journals to hide partial external changes.

## Boundaries

- The administrator Publishes in Dify; AW5 does not Publish workflows.
- Dify's database and filesystem are separate state from this Git repository. Exported DSL is not a database backup.
- Backend source checks and offline fixtures do not prove deployed cross-project isolation.
- A Publish can race an in-flight request; the Chatflow request is not atomically pinned to the Published workflow the backend just inspected.
- The portal is designed for access on the host computer. Remote public hosting, multiple API replicas and a shared distributed lock are outside the current setup.

See [installation](installation.md) and [limitations](limitations.md).
