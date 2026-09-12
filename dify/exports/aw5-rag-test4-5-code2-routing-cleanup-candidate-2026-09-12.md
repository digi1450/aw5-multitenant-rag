# AW5-RAG Test4.5 Code 2 Routing Cleanup Candidate

## Identity and status

- Preserved export: `aw5-rag-test4-5-code2-routing-cleanup-candidate-2026-09-12.yml`
- Application name in export: `AW5-RAG Test4.5 code 2 fix`
- SHA-256: `e8a90aa62aa9808e34724a3f560e33c716f736bee525891ce1acba936f7f37a9`
- Static graph: 9 nodes / 8 edges / 2 LLM nodes
- Status: latest development candidate; not current main, not frozen as a
  confirmatory comparator, not formally evaluated, and not evidence of trusted
  tenant isolation.

The export is retained byte-for-byte. This record describes it without changing
the workflow.

## Controlled change from Test4.4

Observed issue: after Scope Resolver and retrieval-level source filtering were
introduced, Code 2 still parsed the user query for `เฉพาะ`, English exclusivity
markers, filenames, and canonical document types. This duplicated source-intent
logic and kept corpus-sensitive routing behavior downstream of the resolver.

Controlled change: Test4.5 removes the `sys.query` input and all source-intent
parsing/filtering from Code 2. No graph, Registry SQL, resolver, retrieval,
IF/ELSE, writer, memory, or fallback setting changed between the two preserved
exports, apart from non-semantic canvas position and the application name.

## Static graph and configuration

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

The static configuration remains:

- Registry: PostgreSQL `documents`, currently restricted in SQL to AW5
  `tenant_id = 1`, enabled, non-archived, completely indexed documents.
- Resolver: `gemini-3.5-flash-lite`, `Medium`, maximum output 2,048 tokens;
  returns `scope_mode`, `document_names_csv`, `strict`, and `retrieval_query`.
- Retrieval: three Knowledge Bases, weighted multiple retrieval, Top K 30,
  vector/keyword 0.7/0.3, Gemini Embedding 2, no reranker, no threshold.
- Manual metadata filter: built-in `document_name in
  Scope Resolver.document_names_csv`.
- Writer: `gemini-3.5-flash`, `Minimal`, maximum output 6,601 tokens, memory
  window 10, context from `Code 2.result`.
- False branch: deterministic Thai insufficient-evidence response.

`scope_mode` and `strict` remain protocol/classification outputs but have no
direct downstream consumer in this graph. Retrieval execution is controlled by
`document_names_csv` and `retrieval_query`.

## Code 2 responsibility

Code 2 now performs only deterministic context preparation:

1. accepts Knowledge Retrieval results;
2. rejects non-object items and items with blank/non-string content;
3. preserves retrieval relevance order;
4. keeps the first ten valid items;
5. prefixes content with available `document_id`, `document_name`, `dataset_id`,
   and `dataset_name` as `SOURCE_METADATA`;
6. returns `result`, `has_evidence`, and `evidence_count`.

It no longer reads the user query or decides source intent. `has_evidence` still
means only that at least one prepared context item exists; it does not validate
semantic sufficiency.

## Evidence boundary

The owner reported that all requested Test4.5 smoke questions passed in the live
workflow. At the time of this synchronization, the repository does not contain
the exact question set, per-run traces, latency/token records, or an atomic local
evidence package tied to this export. The result is therefore classified as an
owner-run engineering smoke observation, not a Development-36 run, formal
benchmark, repeatability result, or promotion proof.
