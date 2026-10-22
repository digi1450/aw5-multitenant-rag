# Status and limitations

## Implemented in source

Discord private threads, current-role authorization, Published dataset synchronization, document metadata validation, a backend-owned source registry, source-scoped RAG and a local administrator portal are implemented. Tests cover these contracts using offline fixtures and mocked integrations.

The owner has reported a working Discord answer in the original deployment. That observation does not establish that a fresh installation, every administrator action, or every query type succeeds.

## Not established by this repository

- Controlled end-to-end isolation across two real project tenants.
- Production readiness, backup/restore validation, formal quality scores, repeated-run p50/p95 latency or full provider cost.
- Automatic SDLC execution, proven requirement-to-design/schema traceability, exhaustive extraction or whole-document summaries.
- Availability of every configured model/plugin for a new provider account.
- An unattended installation with no manual Discord/Dify/provider configuration.

Historical case-study evaluation documents are not part of the public-facing source tree. No old score is assigned to the portable template.

## Operational constraints

- The backend's Dify request is blocking with a 35-second timeout; the bot waits up to 45 seconds for the backend.
- Writer memory is enabled, but source resolution and the backend shortlist depend on the latest question. Follow-up source references can therefore be lost upstream.
- Retrieval returns a bounded sample, followed by a 15-chunk selector. Increasing Top K does not establish whole-document coverage.
- The API runs as one process with per-ticket in-memory locks. Multiple replicas need shared coordination.
- Document metadata is revalidated on requests, which adds upstream calls and latency.
- Existing posted answers and requests already in flight cannot be recalled after role revocation.
- The Published-workflow check can race a Publish. Do not claim atomic project isolation solely from separate Dify apps.

## Data and public distribution

Use your own authorized documents or the synthetic examples. Local storage does not prevent cloud disclosure: embedding receives input text; answer generation receives selected evidence; a cloud reranker would receive candidates if enabled.

The current tree intentionally excludes private case-study material, credentials, internal academic deliverables and AI instructions. Removing files from a checkout does not remove them from older Git commits. Git history must be handled separately before making a previously private repository public.

## Verification scope

Run the offline suite from the README. Compose validation and static workflow checks do not replace importing the template and exercising a fresh installation with your own accounts. No live Discord/Dify calls are made by the offline test suite.
