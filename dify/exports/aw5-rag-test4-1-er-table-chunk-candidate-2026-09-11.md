# AW5-RAG Test4.1 runtime-state snapshot

## Identity and evidence status

- Application label: **AW5-RAG Test4.1 - ER Table Chunk Candidate**
- Preserved export:
  [aw5-rag-test4-1-er-table-chunk-candidate-2026-09-11.yml](aw5-rag-test4-1-er-table-chunk-candidate-2026-09-11.yml)
- Owner-supplied source export: `AW5-RAG Test4.1 - ER Table Chunk Candidate.yml`
- SHA-256: `842fd57728d4c2b173ebdc594ea3728a83f8d69d7436cd32a2871de79fe2bcef`
- Dify DSL version: `0.7.0`
- Status: **previous production-oriented candidate, preserved byte-for-byte and
  statically reviewed; not a formal benchmark result or current-main promotion**
- This record does not establish Published/Draft state because that state is not
  encoded authoritatively in the export and no live Dify inspection occurred.

V9.1 is retained as the frozen research comparator. Test4.1 is the previous
production-oriented candidate and is not Variant A/B/C/D. Test4.2 superseded it
as the owner-confirmed primary candidate on 2026-09-12 without changing this
preserved Test4.1 export.

## Static architecture

The export contains **7 nodes, 6 edges and 1 LLM node**:

```text
User Input -> Knowledge Retrieval -> Code 2 -> IF/ELSE
                                                  | true  -> LLM -> Answer
                                                  | false -> Answer 2
```

`Answer 2` is deterministic and returns:

> ยังไม่พบหลักฐานที่เพียงพอจากการค้นหาครั้งนี้ กรุณาระบุหัวข้อ เลขข้อ หรือรายละเอียดที่ต้องการเพิ่มเติม

Code1 is absent. No `original_query` reference remains. Knowledge Retrieval,
the `query` input of Code 2, the LLM user prompt and the memory query template
all read `sys.query` directly.

## Retrieval configuration

- Retrieval mode: `multiple`, over three configured Knowledge Base references
- Multiple-retrieval mode: weighted score
- Top K: `30`
- Vector weight: `0.7`
- Keyword weight: `0.3`
- Embedding model: `gemini-embedding-2`
- Embedding provider:
  `digi1450/gemini_embedding_2_aw5/gemini_embedding_2_aw5`
- Reranker: disabled; model `null`
- Score threshold: `null`
- Metadata filtering: disabled, with an empty condition list
- Saved metadata-filter model configuration: `gemini-3.5-flash-lite` from
  `langgenius/gemini/google`, temperature `0`, max output tokens `1024`

The retrieval configuration is statically identical to the preserved
2026-09-10 Test4 export for the compared fields.

## Code 2 behavior

Code 2:

1. rejects a non-array `results` value and discards non-object, blank-content
   retrieval items;
2. reads physical identity from outer `metadata.document_name`;
3. reads canonical logical identity from nested
   `metadata.doc_metadata.document_type`;
4. recognizes a source restriction when the normalized query contains Thai
   `เฉพาะ` (except `โดยเฉพาะ`) or one of the configured English restriction
   markers;
5. matches a physical filename or filename stem against the query, and matches
   canonical `document_type` by exact normalized token;
6. for a recognized restriction, retains entries whose physical name or
   canonical type matched; an unmatched explicit filename extension produces an
   empty result;
7. for a non-restricted path, preserves Knowledge Retrieval order with
   `selected_entries = valid_items[:10]`;
8. prefixes each retained chunk with `SOURCE_METADATA`, then returns `result`,
   `has_evidence` and `evidence_count`.

The emitted `SOURCE_METADATA` JSON contains available outer
`document_id`, `document_name`, `dataset_id` and `dataset_name`. It does not emit
the nested `doc_metadata` object or `document_type`.

`has_evidence` is exactly `bool(enriched_results)`. The IF/ELSE true branch runs
the LLM when this value is true. It is an empty-context/cost guard, not evidence
relevance or entailment validation.

## Answer LLM

- Node title: `LLM`
- Model: `gemini-3.5-flash`
- Provider: `langgenius/gemini/google`
- Mode: chat
- Max output tokens: `6601`
- Thinking level: `Minimal`
- No temperature value is stored in this LLM node
- Context: enabled from `Code 2.result`
- Memory: enabled, window `10`
- Memory query template: `sys.query` followed by `sys.files`
- Vision: enabled, `high` detail, using `sys.files`
- Structured output: disabled

The unchanged system prompt limits claims to retrieved evidence, requires
partial-answer limitations, preserves exact schema declarations, forbids
deriving business meaning from schema labels, keeps differing source schemas
separate, surfaces unresolved conflicts, and attributes claims to their actual
supporting source. The user prompt reads `sys.query` directly.

## Runtime-change classification

| Change | Classification | Current evidence status |
| --- | --- | --- |
| Remove Code1 and wire `sys.query` directly | Cleanup / behavior-preserving refactor | Statically verified in this export; owner reports no regression in targeted diagnostics |
| Replace document diversity selection with retrieval-order Top10 | Experimental context-selection change | Provisionally keep based on owner-reported engineering diagnostics; not formal benchmark proof |
| Read `document_type` from `metadata.doc_metadata` and support canonical restriction | Bug fix / source-resolution architecture improvement | Nested location and targeted behavior were diagnosed from owner-inspected runtime metadata; current implementation is statically verified |
| Natural-language source aliases | Not implemented | Optional future product work |

The prior repository snapshot used Code1 and selected one initial item per
document before filling remaining slots. The owner also reports an intervening
runtime round-robin version that could select ranks approximately
`1, 2, 16, 5, 3, 18, 8, 4, 20, 6`; that intermediate state is not represented
by a preserved export in this repository. Test4.1 instead keeps raw ranks 1-10
on the normal path.

## Nested Custom Metadata finding

The observed defect was that an exact filename restriction could use the outer
`metadata.document_name`, while a canonical request such as TOR was not
deterministically filtered. A correct final response from the LLM could mask
that boundary failure.

Runtime inspection supplied by the owner located custom ingestion metadata at
`metadata.doc_metadata`, rather than the outer metadata object. Code 2 now reads
`document_type` from that nested object and keeps it separate from the physical
filename. The code is data-driven: the matching logic does not hard-code a list
of allowed types. The source comments mention TOR/SDS/ER only as examples.

This supports canonical identifiers present in document metadata. It does not
provide semantic resolution for Thai transliterations, descriptive document
names or arbitrary aliases.

## Round-robin diagnostic

The observed problem was context capacity being assigned to documents despite
low relevance. For an MD_FACTOR diagnostic, owner-inspected traces showed that
document balancing admitted low-ranked TOR chunks and displaced higher-ranked
ER/SDS evidence. The hypothesis was that preserving retrieval rank would retain
more query-relevant context. The candidate therefore uses the first ten valid
results in original order.

Owner-reported engineering diagnostics then preserved ranks 1-10 and passed six
targeted cases, including the 15-field CM_STAT list. These observations justify
the current provisional keep decision only. They are not a Development-36 run,
a formal evaluation, a publication result or proof of general superiority.

## Static discrepancies and remaining risks

1. The descriptive name “Answer LLM” corresponds to a YAML node titled `LLM`.
   This is a naming difference only.
2. The LLM prompt recognizes `เท่านั้น` as a source-restriction word, but Code 2
   does not. Such a query relies on the LLM rather than the deterministic filter.
3. Canonical type matching is derived only from types present in retrieved
   items. If a requested canonical type retrieves no item, Code 2 does not know
   that type matched and falls back to the normal Top10 path unless an explicit
   filename extension triggered the empty-context path.
4. A restricted match is not capped at ten and may pass up to all matching valid
   retrieval items; the Top10 limit applies only to the normal path.
5. Canonical `document_type` is used for filtering but is not included in the
   emitted `SOURCE_METADATA` prefix.
6. `has_evidence` proves only nonempty prepared context. Semantic sufficiency,
   refusal and partial-answer behavior remain dependent on the Answer LLM
   prompt.
7. The code comments contain corpus-specific examples (`TOR / SDS / ER`), though
   the executable matching logic is dynamic. Repository guidance prefers
   production candidate logic and prompts without corpus-specific aliases.
8. No static export can prove live Published/Draft state, provider availability,
   latency, cost, answer correctness or trusted project-tenant enforcement.

No workflow edit or runtime test was performed during this synchronization.
