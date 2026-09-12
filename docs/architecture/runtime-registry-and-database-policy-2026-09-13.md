# Runtime File Registry and Database Policy

## Status

This record captures the current Test4.4/Test4.5 implementation and the database
policy required before multi-tenant use. The current mechanism is a development
candidate. Trusted tenant authorization and cross-tenant isolation remain
unimplemented and unverified.

This document does not change Dify, its database, credentials, or either
preserved workflow export.

## Current Runtime File Registry

The current candidate obtains an available-source registry before source-scope
resolution:

```text
User Input -> Get File Registry -> Scope Resolver -> Knowledge Retrieval
```

The owner configured the Database Client plugin to connect inside the Dify Docker
network at `db_postgres:5432`, database `dify`, using a dedicated
`rag_registry_reader` login. The password is a secret and must not be stored in
Git, workflow documentation, screenshots intended for publication, or test
evidence.

The workflow export confirms this SQL behavior:

```sql
SELECT
    d.id AS document_id,
    d.name AS document_name,
    jsonb_extract_path_text(d.doc_metadata, 'document_type') AS document_type
FROM documents d
WHERE jsonb_extract_path_text(d.doc_metadata, 'tenant_id') = '1'
  AND d.enabled = true
  AND d.archived = false
  AND d.indexing_status = 'completed'
ORDER BY d.name;
```

The owner reports that the role was granted `CONNECT`, schema `USAGE`, and
`SELECT` on `public.datasets` and `public.documents`. This is least privilege
relative to a Dify administrator credential, but it still permits reading both
tables in full. The SQL `WHERE` clause is an application convention; it is not a
database-enforced row boundary.

The Dify UI label `Workspace Default` selects a shared/default plugin credential
inside the Dify workspace. It does not automatically restrict SQL rows to the
current Dify workspace or to an AW5 project tenant.

## Identity and authorization boundary

AW5 uses one business tenant per software project. AW5 `tenant_id` is distinct
from Dify's internal workspace `tenant_id`.

For a real multi-tenant service, a trusted AW5 backend must:

1. authenticate the platform user;
2. resolve authorized project membership;
3. derive the effective AW5 `tenant_id` server-side;
4. select the permitted Dify app or pass an authorized tenant scope to a generic
   workflow;
5. reject missing, invalid, mismatched, or unauthorized scope before retrieval.

User text, a Scope Resolver result, a Discord/Teams identifier, a frontend field,
or a caller-provided `tenant_id` cannot grant access. Dify app/API credentials
and database credentials remain server-side.

## Candidate deployment patterns

Two deployment patterns remain open:

### One Dify app per project tenant

Duplicate the generic workflow, connect each app only to that project's
Knowledge Bases, and restrict its Registry to the same AW5 tenant. A trusted
backend maps membership to the correct app/API credential. This gives useful
configuration separation and is manageable for a small number of projects.

Changing only the Knowledge Bases is insufficient in the current candidate: the
Registry SQL must also stop returning another project's filenames. App
duplication does not itself provide database-enforced authorization and remains
vulnerable to wrong-app routing or configuration mistakes.

### Shared generic Dify app

Use one generic workflow and supply an authenticated backend-derived tenant
scope to Registry and retrieval. This scales better but requires a proven
tenant-aware retrieval filter and must not expose a tenant selector as an
untrusted client input.

No final choice between these patterns has been made.

## Production database policy to decide and implement

Before production-style multi-tenant use:

- replace the literal tenant value with a value derived from trusted membership;
- parameterize database access rather than constructing SQL from user/model text;
- consider exposing a narrow registry view or controlled function containing
  only the fields needed by the resolver;
- if a view/function becomes the boundary, revoke the Registry role's direct
  table `SELECT` privileges so the restriction is meaningful;
- define credential creation, rotation, revocation, backup, and incident handling;
- verify behavior after every relevant Dify/database upgrade because the Registry
  currently depends on Dify's internal `documents` schema;
- test at least two project tenants containing conflicting synthetic facts and
  verify both retrieval directions fail closed.

Whether to use a dedicated AW5 registry table, a database view/function, or
role-specific row-level security remains an implementation decision. No option is
recorded as completed.

## Project and document onboarding requirement

Adding a project or source is an administered operation. Before making it
available, an administrator or engineer should:

1. create and inspect the project's Knowledge Bases and chunks;
2. assign the AW5 tenant metadata and useful document classification metadata;
3. connect only the intended Knowledge Bases to the intended Dify app/workflow;
4. confirm the Runtime File Registry returns the expected document identities;
5. test generic, one-source, multi-source, and unknown-source questions;
6. run cross-project leakage checks before publication.

The system is not required to make a newly uploaded file production-ready
without ingestion, metadata, retrieval, and safety review.
