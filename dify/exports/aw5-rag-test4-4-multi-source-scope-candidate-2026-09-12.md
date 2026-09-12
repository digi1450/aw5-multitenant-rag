# AW5-RAG Test4.4 Multi-source Scope Candidate

## Identity and status

- Preserved export: `aw5-rag-test4-4-multi-source-scope-candidate-2026-09-12.yml`
- Application name in export: `AW5-RAG Test4.4`
- SHA-256: `89e94535eb4050c1d1b13ba4fe51a2d4b22164a6edee9c95c0beb3dc47505ebc`
- Static graph: 9 nodes / 8 edges / 2 LLM nodes
- Status: preserved development candidate; not current main, not formally
  evaluated, and not evidence of trusted tenant isolation.

The export is retained byte-for-byte. This record describes it without changing
the workflow.

## Static graph

```text
User Input
  -> Get File Registry
  -> Scope Resolver
  -> Knowledge Retrieval
  -> Code 2
  -> IF/ELSE
       true  -> LLM -> Answer
       false -> Answer 2
```

`Answer 2` returns a deterministic insufficient-evidence message. The IF/ELSE
condition is `Code 2.has_evidence is true`.

## Registry and resolver

`Get File Registry` uses the Database Client PostgreSQL tool and queries Dify's
`documents` table. It returns `document_id`, `document_name`, and the custom
`document_type` value from `doc_metadata`. The query is currently fixed to AW5
`tenant_id = 1` and to enabled, non-archived, completely indexed documents.

The Scope Resolver uses `gemini-3.5-flash-lite`, thinking level `Medium`, and a
2,048-token maximum output. Its structured output is:

- `scope_mode`: `ALL`, `SELECTED`, or `UNRESOLVED`
- `document_names_csv`: comma-separated exact built-in `document_name` values
- `strict`: `STRICT` or `NON_STRICT`
- `retrieval_query`: semantic retrieval query

The resolver receives the runtime registry rather than a corpus-specific source
list embedded in application code. `strict` is classified but is not consumed by
any downstream selector, filter, branch, Code node, or writer in this export.

## Retrieval and answer path

Knowledge Retrieval uses `retrieval_query`, searches three configured Knowledge
Bases in multiple weighted retrieval mode, and applies one Dynamic Manual
Metadata Filter:

```text
document_name in Scope Resolver.document_names_csv
```

Static retrieval settings are Top K 30, vector weight 0.7, keyword weight 0.3,
Gemini Embedding 2, no reranker, and no score threshold.

Code 2 still contains the earlier query-based source-restriction logic. It
parses Thai and English exclusivity markers, resolves exact filenames and
canonical `document_type` tokens from retrieved results, keeps at most ten valid
items, prefixes each item with `SOURCE_METADATA`, and emits `result`,
`has_evidence`, and `evidence_count`.

The answer LLM is `gemini-3.5-flash`, thinking level `Minimal`, with a 6,601-token
maximum output. It reads `Code 2.result`; conversation memory is enabled with a
window of 10. `has_evidence` means that Code 2 produced at least one nonblank
context item. It is an empty-context guard, not proof that the evidence is
semantically sufficient.

## Relationship to Test4.5

Test4.5 keeps this graph, registry, resolver, retrieval, writer, IF/ELSE, and
fallback configuration. Its controlled change removes the duplicated
query/source-intent parsing from Code 2 so source intent remains the resolver and
retrieval filter's responsibility.
