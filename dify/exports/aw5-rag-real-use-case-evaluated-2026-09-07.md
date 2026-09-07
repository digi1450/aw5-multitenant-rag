# AW5-RAG real-use-case evaluated snapshot — 2026-09-07

## Status

**Owner-supplied export of the live Published workflow used for the 20-case
real-use-case evaluation; preserved byte-for-byte and correlated with the saved
runtime graph.** It is an evaluated snapshot, not an owner-confirmed promotion
over the 2026-09-06 current main.

## Files and identity

- Owner-supplied source: `/Users/digital/Downloads/AW5-RAG Test2.yml`.
- Repository snapshot:
  `aw5-rag-real-use-case-evaluated-2026-09-07.yml`.
- Source and repository SHA-256:
  `3d3e588a93d56bc35c4176365939009995936fcd133aeda0c104747aa4992f93`.
- Application label: `AW5-RAG Test2`.
- Mode: `advanced-chat`.

`cmp` confirmed that the repository file is byte-identical to the supplied
source.

## Graph and configuration

- 6 nodes / 5 edges / 1 LLM node:
  `User Input -> Code 1 -> Knowledge Retrieval -> Code 2 -> LLM -> Answer`.
- One Knowledge Retrieval node with three portable Knowledge Base references.
- Multiple retrieval, Top K 10, semantic/keyword weights `0.7/0.3`, reranker
  disabled, and manual metadata filtering.
- Embedding model: `gemini-embedding-2` through the AW5 plugin.
- Answer model: `gemini-3.5-flash`.

## Runtime correlation

A read-only comparison used a graph snapshot retained by
`workflow_runs` during the evaluation window. Node IDs, node types, titles,
edges, prompts and execution settings matched after normalizing fields that Dify
changes during export:

- the three live UUID Knowledge Base IDs become 64-character portable export
  references;
- canvas viewport and node positions; and
- UI-only selection flags.

After those fields were normalized, the exported and runtime graphs were equal.
Both had normalized SHA-256:
`72c100b664c15aaad40bd188d5676340f250bde2e93361876ade782a98389393`.

No live Knowledge Base UUID is stored in this record.

## Evaluation evidence

The owner-authorized 20-case run produced:

- 13 pass, 4 partial and 3 fail;
- strict pass 65% and pass-or-partial 85%;
- required-source coverage 17/20;
- 20/20 cases with a completed answer after retries;
- 39 attempts, including 11 timeouts; and
- selected-answer latency p50 4.186 seconds and p95 14.287 seconds.

See the sanitized
[evaluation summary](../../docs/research/self-hosted-real-use-case-evaluation-2026-09-07.md)
for the protocol deviation, node latency, usage, findings, local evidence hashes
and non-claims.

## Validation

- Ruby/Psych parsed the supplied and repository YAML successfully.
- Static inspection confirmed 6 nodes, 5 edges, one Knowledge Retrieval node,
  one LLM node and three Knowledge Base references.
- The bounded secret scan found no API key, authorization header, bearer token,
  password or credential value.
- The bounded private-content scan found none of the tested corpus phrases.

## Evidence boundary

This snapshot is direct evidence for the exact workflow structure and settings
used in the dated run. The evaluation does not establish repeatability,
production readiness, tenant isolation or the root cause of Retrieval stalls.
The 2026-09-06 workflow remains current main until the owner explicitly promotes
this evaluated snapshot.
