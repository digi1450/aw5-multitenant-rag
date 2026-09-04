# Tenant and Project Identity — Owner-confirmed 2026-09-03

## Superseding decision

The owner revised and locked the AW5 terminology on **2026-09-03**:

- One AW5 business **tenant is one software project**.
- `tenant_id` is the project's identifier and the only AW5 project-scope ID.
- The first/current tenant is `tenant_id = 1`, with the display name
  `Nature Footprint`.
- A tenant does not represent a team, department, or organization in AW5.
- The earlier same-day Team -> Projects hierarchy is superseded and must not be
  used for implementation.

The intended hierarchy is:

```text
One organization
├── Nature Footprint  (tenant_id = 1)
├── Future Project B (tenant_id = 2)
└── Future Project C (tenant_id = 3)
```

The submitted DS1 concept may still contain the earlier or ambiguous terminology.
The owner will revise DS1 separately. Until that revision is made, this decision
record is authoritative for current architecture and implementation planning.

## Authorization and retrieval boundary

Every project-scoped knowledge object must remain attributable to its project
tenant. This includes source documents, extracted content, chunks, image
attachments, embeddings/index entries where metadata is supported, and retrieval
results.

The trusted application backend must derive the effective project tenant ID from
the authenticated user's authorized project membership. User text, model output,
browser-supplied dataset IDs, Discord/Teams messages, and an untrusted frontend
selector are not authorization sources. Retrieval must fail closed if the ID is
absent, invalid, mismatched, or unauthorized.

Isolation testing must use at least two project tenants with conflicting synthetic
facts and verify that neither tenant retrieves the other's data. Existing `ISO-01`
material remains a historical placeholder and does not prove this isolation or
the trusted backend filter.

## Identifier naming

New AW5 code, metadata, and APIs must use `tenant_id` as the canonical and only
project-scope identifier. Do not introduce a separate project ID field. The exact
storage and filtering mechanism remains an implementation decision. `tenant_name`
is a display label and must not be used as the authorization key.

Dify also uses an internal `tenant_id` to identify a **Dify Workspace**. That Dify
database field is not automatically the AW5 project tenant ID. Code and
documentation must qualify the two meanings where confusion is possible:

| Term | Meaning |
| --- | --- |
| Dify internal `tenant_id` | Dify Workspace identifier |
| AW5 `tenant_id` | Project identifier |

## Status and non-claims

This document locks the business identity and isolation requirement. It does not
claim that the current Dify Chatflow, Knowledge Base, synthetic PDF pilot, or
historical cloud workflow implements or verifies project-tenant isolation. It
does not authorize uploading private corpus material, publishing an app, or
changing external access.
