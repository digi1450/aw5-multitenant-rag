# AW5-RAG — Self-hosted Main Workflow

> **Historical status update — 2026-09-06:** this was the owner-confirmed main
> snapshot on 2026-09-04. It was superseded by
> [`aw5-rag-self-hosted-main-2026-09-06.yml`](aw5-rag-self-hosted-main-2026-09-06.yml)
> and is retained as the immediate four-node control.

## Provenance and status

- The owner supplied `AW5-RAG-2.yml` and explicitly identified it as the new
  main workflow on **2026-09-04**. This is the confirmation/recording date, not
  an inferred deployment timestamp.
- Original local path: `/Users/digital/Downloads/AW5-RAG-2.yml`.
- Repository snapshot:
  [aw5-rag-self-hosted-main-2026-09-04.yml](aw5-rag-self-hosted-main-2026-09-04.yml).
- SHA-256: `b843323262447b25eca4d17304c2b94d521cb53cdc75a18d6f30153e93c25b6d`.
- The repository copy is byte-identical to the supplied file. Prompts,
  dependencies, dataset references and retrieval settings were not modified.
- Application name: `AW5-RAG`; mode: `advanced-chat`; DSL version: `0.7.0`.

**Status at capture: owner-confirmed main workflow for the self-hosted system;
now superseded and retained as a control; statically inspected as a local
export.** This does not verify Published versus
draft state, byte equality with the currently running app, import compatibility,
answer quality, citation behavior, latency, cost, backup/restore, or tenant
isolation. No Dify import or formal evaluation was performed for this record.

## Inspected graph and configuration

```text
User Input -> Knowledge Retrieval -> LLM -> Answer
```

- 4 nodes, 3 edges and one answer-model call.
- One Knowledge Retrieval node references three dataset IDs and passes its result
  directly to the LLM context.
- Answer returns the LLM output.

| Configuration | Supplied snapshot |
| --- | --- |
| Answer model | `gemini-3.5-flash` via `langgenius/gemini/google` |
| Maximum output | 6,601 tokens |
| Thinking level | `Minimal` |
| Conversation memory | Enabled, window size 10 |
| Retrieval mode | Multiple-dataset weighted semantic/keyword search |
| Retrieval weights | Semantic/vector `0.7`; keyword `0.3` |
| Top K | 10 |
| Reranking | Disabled |
| Score threshold | `null` / disabled |
| Embedding | `gemini-embedding-2` via `digi1450/gemini_embedding_2_aw5/gemini_embedding_2_aw5` |
| Retriever-resource/citation feature | Enabled in configuration; runtime display not tested |
| Vision | Enabled at `high` detail; chat file-upload feature disabled |
| Structured output | Disabled |

The system prompt is generic and evidence-grounded. It requires same-language
answers, exact source identifiers where available, careful separation of claims
between documents, explicit handling of insufficient or conflicting context, and
treatment of instructions inside retrieved documents as content. It contains no
TOR/SDS/ER router, test answers, or per-file retrieval rules.

Declared plugin dependencies are marketplace plugin
`langgenius/gemini:0.9.7` and package
`digi1450/gemini_embedding_2_aw5:0.1.4`; their exact identifiers remain in the
snapshot. This record does not install, modify, or publish either plugin.

## Architecture fit and remaining boundary

The graph implemented the owner-confirmed simple path and connected three
Knowledge Bases through one retrieval node. It replaced AW5-RAG 1.2 as the
current pointer on 2026-09-04 and was itself superseded on 2026-09-06. AW5-RAG
1.2 and the 2026-08-25 source-routing baseline remain historical controls.

Metadata filtering is disabled in this export. The workflow itself therefore does
not demonstrate trusted enforcement of the AW5 project `tenant_id`. The required
authorization boundary must still be implemented and tested outside or before
retrieval; `ISO-01` remains unverified.

## Preservation and security checks

- YAML parsing, graph/configuration inspection, and source/copy SHA-256 equality
  are static checks only; no prompt or model call was executed.
- A bounded scan found no populated environment/conversation variables or common
  API-key, bearer-token, password, private-key, or credential patterns.
- Dataset IDs are retained as opaque workflow references. They are not treated as
  credentials and do not prove that another Dify instance can access the datasets.
- Original documents, chunks, vector indexes, credentials and plugin packages are
  not added by this snapshot.
