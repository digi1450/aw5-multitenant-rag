# AW5-RAG Test4.7 v2 — owner-supplied 2026-10-03

## Status and provenance

The owner supplied `AW5-RAG Test4.7 v2.yml` and proposed using this workflow
as the next primary development workflow. This records that direction, not
formal promotion, production readiness, or confirmation of live Published state.
The earlier 2026-09-06 main remains the historical owner-promoted reference.

- [Preserved export](aw5-rag-test4-7-v2-owner-supplied-2026-10-03.yml), byte-identical to the supplied file.
- SHA-256: `a2a68b8e74b066d368430c5ab82cf42caf560b8f6bbfb0b84b322dc5e041c2c3`.
- Export label: `AW5-RAG Test4.7 v2`; advanced-chat; DSL version `0.7.0`.
- Verified here: YAML parses; 10 unique nodes / 9 edges; all edge endpoints exist;
  both Python Code nodes parse; Code 1's three mode outputs checked locally.
- Pattern scan found no common provider keys, bearer tokens or private keys;
  environment and conversation variable lists are empty. This is a bounded
  credential check, not an exhaustive security audit.
- Not verified here: import compatibility, Published identity, live API behavior,
  retrieval results, answer quality, latency, cost, or cross-project isolation.
  No Dify app was imported, edited, Published, or invoked during this review.

## Recorded path and settings

```text
User Input -> Get File Registry -> Scope Resolver -> Code 1
  -> Knowledge Retrieval -> Code 2 -> IF/ELSE
      true  -> LLM -> Answer
      false -> Answer 2
```

- Registry uses Database Client `postgres_node_5` and `$arg0` from `sys.query`.
  It selects enabled, unarchived, completed documents whose AW5 document metadata
  has `tenant_id = '1'`. It scores filename/type/query terms, returns only
  positive matches, and limits the shortlist to 20. It does not constrain the SQL
  to the datasets selected in this app's Retrieval node.
- Scope Resolver: Gemini `gemini-3.5-flash-lite`, thinking `Medium`, maximum
  output tokens 2048. The active system prompt uses Jinja2 `source_registry`.
  Its schema requires `scope_mode`, `document_names_csv`, `strict`, and
  `retrieval_query`; modes are ALL, SELECTED and UNRESOLVED. The export also
  preserves an older `text` field on this Jinja2 prompt; this review does not
  treat that inactive text as the runtime prompt.
- Code 1 maps ALL to `filter_names = None`, SELECTED to the provided CSV, and
  other modes to an empty string. Retrieval's manual `document_name in` filter
  references this output; the retrieval query uses the resolver's query.
- Retrieval references three Knowledge Bases. Weighted vector/keyword is
  0.7/0.3, Top K 30, reranking disabled, score threshold null.
- Code 2 preserves retrieval order, skips malformed/blank items, takes the first
  ten valid items, and adds SOURCE_METADATA provenance. `has_evidence` checks
  nonempty prepared context, not semantic answer sufficiency.
- Answer model: `gemini-3.5-flash`, thinking `Minimal`, maximum output tokens
  6601, memory window 10, Context from Code 2.result. The generic prompt separates
  schema evidence and descriptions, forbids inferred fields/relationships and
  unsupported source attribution. File upload is disabled while answer vision
  remains enabled in the export.
- Dependencies: custom Gemini embedding plugin 0.1.4, Database Client 0.1.47,
  Gemini provider 0.9.9. Provider credentials are separate runtime configuration.

## Review points before accepting it as main

1. **ALL/null behavior:** Code 1 declares `filter_names` as string but returns
   Python None for ALL. Check the installed Dify version's Code output handling
   and manual `in` filter behavior. Static Python execution does not establish
   that null removes the filter or that Dify accepts the output.
2. **UNRESOLVED behavior:** it still enters Retrieval with an empty filter value;
   there is no pre-retrieval rejection branch. Verify that unknown/ambiguous
   sources cannot broaden retrieval, and observe the resulting fallback.
3. **Project boundary:** Registry's literal AW5 tenant 1 is project-specific.
   It is not a generic multi-project authorization mechanism. The three
   Retrieval dataset references and document-name filtering do not prove tenant
   isolation. Preserve backend authorization and document validation.
4. **Shortlist scope:** Registry can name a tenant-1 file outside this app's
   selected datasets, which Retrieval cannot search. Verify selection behavior
   when inventory and Published Retrieval diverge.
5. **STRICT:** the structured field has no downstream consumer; STRICT and
   NON_STRICT share the same selected-file retrieval filter. Do not claim that
   NON_STRICT enables broader retrieval in this graph.
6. **Evidence and integration:** confirm the registered app/API key corresponds
   to this app's actual Published version. A renamed export does not update
   AW5 registration. Assess representative ALL, single-file, two-file,
   unknown-file and follow-up paths under an owner-approved diagnostic before
   drawing runtime conclusions. Earlier Test4.7 scores do not transfer here.

These are static review findings and proposed verification work; this update
does not authorize changing the supplied workflow or running a live evaluation.
