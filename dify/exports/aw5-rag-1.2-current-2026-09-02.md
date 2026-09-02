# AW5-RAG 1.2 — Owner-confirmed Current Workflow

## Provenance and status

- The owner supplied `AW5-RAG 1.2.yml` and explicitly identified it as the current
  workflow on **2026-09-02**. This is the confirmation/recording date, not an
  inferred export or deployment timestamp.
- Original local path: `/Users/digital/Downloads/AW5-RAG 1.2.yml`.
- Repository snapshot: [aw5-rag-1.2-current-2026-09-02.yml](aw5-rag-1.2-current-2026-09-02.yml).
- SHA-256: `7e1d7d7e49f711bf0653db38ed6b3923f590cf83d5b4d46538db6ae4fe2f320d`.
- The repository copy is byte-identical to the supplied file. Prompts, code,
  dependencies, dataset references, and retrieval settings were not modified.
- Application name: `AW5-RAG 1.2`; mode: `advanced-chat`; DSL version: `0.7.0`.

**Status: owner-confirmed current workflow; inspected as a local export.** This
does not verify Published versus draft state, the current live instance, import
compatibility, answer quality, citation behavior, latency, cost, or isolation.
No Dify import, execution, or evaluation was performed for this record.

This app is **not** `AW5-RAG Lean Adaptive v1.2 Candidate`. Similar version numbers
do not establish that they are the same workflow. It also differs from the frozen
2026-08-25 baseline, whose scores must not be assigned to this snapshot.

## Inspected graph and configuration

```text
Start -> LLM 1 -> Route Queries
                    |-> Retrieve TOR --|
                    |-> Retrieve SDS --|-> Merge Context -> LLM 2 -> Answer
                    |-> Retrieve ER  --|
```

- 9 nodes, 10 edges, and 2 LLM nodes on the graph's normal path.
- All three retrieval nodes are connected to Route Queries. The source flags
  control inclusion at Merge Context; the graph has no conditional branch that
  skips a retrieval node when its source flag is false.
- Merge Context filters enabled sources and deduplicates results while retaining
  their metadata. LLM 2 receives `Merge Context.result`; Answer returns `LLM 2.text`.

| Configuration | Supplied snapshot |
| --- | --- |
| LLM 1 | `gemini-3.5-flash-lite`, maximum output 256 tokens |
| LLM 2 | `gemini-3.5-flash`, maximum output 2048 tokens, thinking level `Minimal` |
| Retrieval mode | Weighted semantic/keyword score, `0.5 / 0.5` |
| TOR Top K | 3 |
| SDS Top K | 3 |
| ER Top K | **10**, not the frozen baseline's 6 |
| Reranking enabled | `false` on all three retrieval nodes |
| Score threshold | `null` on all three retrieval nodes |
| Embedding reference in retrieval settings | `gemini-embedding-2` via `digi1450/gemini_embedding_2_aw5/gemini_embedding_2_aw5` |
| Citation-resource feature | Enabled in configuration; runtime citations not tested |
| Chat file-upload feature | Disabled in configuration |

The export retains a `qwen3-rerank` model field, but `reranking_enable` is false.
Do not describe reranking as active merely because that model name is present.
The embedding reference above is an exported setting, not an independent audit of
the live knowledge bases or their indexes.

Declared plugin dependencies are custom package
`digi1450/gemini_embedding_2_aw5:0.1.4` and marketplace plugin
`langgenius/gemini:0.9.7`; their exact identifiers remain in the snapshot. This
record does not install, modify, or publish either plugin.

## Relationship to the target architecture

The [owner-confirmed target](../../docs/architecture/current-direction-2026-09-02.md)
remains self-hosted Dify, locally stored knowledge, cloud models, one retrieval
node, and generic prompts. **That target has not replaced this current workflow.**

This snapshot still has LLM 1 source descriptions, source flags, and three retrieval
nodes. Preserve them as the current-state record, not as mandatory rules for the
new design. Recording existing model names does not select the models/providers
for the future workflow.

## Preservation and security checks

- YAML parsing, graph/selector inspection, and source/copy SHA-256 equality are
  static checks only; no embedded code or prompt was executed.
- Credential-field and common key-pattern checks found no populated credential
  fields, nonempty secret environment variables, or matching common API/private-key
  patterns. This is a bounded scan, not a guarantee against every possible secret.
- Original documents, chunks, vector indexes, credentials, and plugin packages are
  not added by this snapshot. Dataset connection references are retained as export
  configuration, not as proof that another Dify instance can access those datasets.
- Keep the 2026-08-25 baseline and its historical evaluation results unchanged.
