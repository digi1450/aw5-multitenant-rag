# Chatbot Delivery Options

## Decision status

AW5 is expected to expose its RAG capability through a chatbot, potentially
Microsoft Teams or Discord. The platform is not selected and may change. This is
a provisional product/deployment direction, not an implementation record.

Since this proposal, a local Discord demo adapter has been implemented. See the
[dated demo handoff](discord-bot-demo-handoff-2026-09-28.md) for its verified
scope and limits. The demo does not settle the product platform decision.

The current Dify candidate remains the RAG engine. A platform-neutral trusted AW5
backend is the proposed integration and authorization boundary:

```text
Personal Teams/Discord conversation
  -> AW5 backend and platform adapter
  -> authenticate user and resolve project membership
  -> select authorized Dify app/tenant scope
  -> Dify RAG workflow
  -> return answer and citations to that user's conversation
```

## Frontend conversation privacy

The intended frontend behavior is:

- each user sees only their own conversation with the AW5 bot;
- other ordinary users cannot view that conversation;
- an administrator does not participate in or see it as an ordinary frontend
  chat participant;
- authorized administrators may still inspect operational logs through backend,
  Dify, or administration tools.

This is frontend conversation separation, not a requirement to cryptographically
hide logs from system administrators. A Teams personal bot chat or Discord bot
direct message is closer to this behavior than a shared channel. Shared-channel
and ephemeral-response behavior has not been selected.

## Provisional tenant routing

One candidate is to maintain a Dify app per AW5 project tenant:

```text
authenticated member of tenant_id 1 -> Dify App A -> Project A Knowledge Bases
authenticated member of tenant_id 2 -> Dify App B -> Project B Knowledge Bases
```

The backend, not the user or LLM, performs this mapping. Users who belong to more
than one project require a trusted active-project selection. Conversation state
must be scoped at least by platform user identity and AW5 tenant so memory from
one project cannot continue in another project.

The alternative is one generic tenant-filtered Dify app. The repository does not
yet select between a per-project app and a shared generic app.

## Backend responsibilities

A later implementation must define:

- platform request verification and authenticated user identity;
- user-to-project membership and active-project selection;
- fail-closed app/tenant routing;
- server-side storage of Dify app keys and database credentials;
- per-user/per-tenant conversation mapping;
- message length, asynchronous response, retry, and rate-limit handling;
- citation rendering and attachment policy;
- operational logging, retention, and administrator access controls.

Teams/Discord clients must not call PostgreSQL directly or receive Dify/database
credentials. The concrete platform, hosting endpoint, identity provider, data
retention policy, and adapter implementation remain undecided.
