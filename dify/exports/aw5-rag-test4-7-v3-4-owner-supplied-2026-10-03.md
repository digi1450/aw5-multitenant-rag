# AW5-RAG Test4.7 v3-4 — owner-supplied 2026-10-03

## Status and provenance

The owner supplied `AW5-RAG Test4.7 v3-4.yml` and authorized preserving it
after the Draft scope/context changes and targeted diagnostics. The internal
app label is **AW5-RAG Test4.7 v3**; the filename suffix is not proof of a
different app or Published version.

- [Preserved export](aw5-rag-test4-7-v3-4-owner-supplied-2026-10-03.yml), byte-identical to the supplied file.
- SHA-256: `637d6169d571637e9c3505c4ee034f042f3d6288e6d92bef8cc17d14f54c72c2`.
- Size: 56,578 bytes; advanced-chat; DSL version `0.7.0`.
- Compared runtime: Dify 1.17.0, app `0d110469-3014-48ae-ae25-6f962e6a7a80`,
  Draft workflow `31fe009a-d24e-46e8-aef7-228e3060f7c5`.
- YAML safely parses; 10 unique nodes / 9 edges; edge endpoints exist;
  both Python Code nodes parse. Environment and conversation variable lists
  are empty; bounded common credential-pattern checks found no matches.
- All node settings and edges match the final inspected Draft except the
  normal export transformations: encrypted dataset references and omitted
  tool `credential_id`. Reproducing Dify's export encoding verified all three
  Knowledge Base references in order. No credential or encryption key was
  retained in the preservation evidence.

Status: **latest preserved development Draft; targeted diagnostics verified**.
No import roundtrip, Published promotion, formal evaluation, repeatability,
general stability or cross-project authorization is established here. The
earlier v2 export and historical main remain preserved separately.

## Recorded path and settings

```text
User Input -> Get File Registry -> Scope Resolver -> Code 1
  -> Knowledge Retrieval -> Code 2 -> IF/ELSE
      true  -> LLM -> Answer
      false -> Answer 2
```

- Registry returns a query-based shortlist, not the whole corpus. SQL still
  requires document metadata AW5 `tenant_id = '1'`, enabled/unarchived/completed
  documents, positive filename/type/token scores, and a limit of 20.
- Resolver uses `gemini-3.5-flash-lite`, thinking Medium, output limit 2048.
  Its effective Jinja2 prompt receives `source_registry` dynamically. Required
  schema fields are `scope_mode`, `document_names_csv`, `strict`,
  `retrieval_query`, and Boolean `seek_other_sources`.
- `NON_STRICT` permits supplementary sources; `seek_other_sources=true` means
  an explicit request for sources outside the selected set. ALL, UNRESOLVED
  and STRICT return false. Multiple explicitly requested sources belong in the
  required set; the flag concerns additional sources outside that set.
- The older serialized Resolver `text` field is inactive under Jinja2.
  Installed Dify source and actual model prompts confirm it is not combined
  with `jinja2_text` and does not cause another model call.
- Code 1 returns null for ALL/NON_STRICT and SELECTED/NON_STRICT, exact
  selected filenames for SELECTED/STRICT, and an empty string otherwise.
  Retrieval uses manual built-in `document_name in Code 1.filter_names`.
- Retrieval references three Knowledge Bases, vector/keyword weights 0.7/0.3,
  Top K 30, reranking disabled, score threshold null.
- Code 2 takes six inputs: `results`, `scope_mode`, `document_names_csv`,
  `source_registry`, `strict`, `seek_other_sources`. It keeps a maximum of 15
  valid candidates, retains each identifiable required-source anchor first,
  optionally retains at most one outside-set anchor, then fills by retrieval
  order and preserves that order and provenance metadata. STRICT filters all
  selected candidates by resolved required document IDs.
- Code 2 accepts actual Booleans and only literal `true`/`false` text, with
  surrounding whitespace allowed. Actual Resolver runs returned strings
  despite the Boolean schema. Preserve this compatibility check; using
  `bool(text)` would incorrectly treat `"false"` as true.
- Its five outputs are `result`, `has_evidence`, `evidence_count`,
  `selection_report`, `fallback_message`. Required-source coverage reports
  candidate presence, not semantic answer sufficiency. Other-source status is
  `not_requested`, `present`, `not_retrieved` or `omitted_by_limit`.
- Answer 2 reads `fallback_message` directly, distinguishing unresolved source
  identity from an empty evidence context. UNRESOLVED still visits Retrieval,
  but its empty filter causes Dify to skip internal retrievers when no document
  IDs are eligible; it does not execute Writer.
- Writer uses `gemini-3.5-flash`, thinking Minimal, output limit 6601, memory
  window 10 and vision enabled. Context reads Code 2.result; its actual prompt
  receives `selection_report` and the selected enriched chunks. File upload
  remains disabled. Dependencies are embedding plugin 0.1.4, Database Client
  0.1.47 and Gemini provider 0.9.9; credentials remain runtime configuration.

## Evidence and limits

These are targeted exploratory diagnostics, not formal evaluation scores.
Owner-displayed timestamps are preserved; their UI timezone was not inferred.

| Owner-displayed start, 2026-10-03 | Verified result | Seconds | Reported tokens |
|---|---|---|---|
| 05:23:24 AM | Permission only: flag false, `not_requested`; fresh dialogue; 18 retrieved -> 15 selected | 17.552202 | 14,642 |
| 05:23:59 AM | Explicit other-source request: flag true, `present`; fresh dialogue; 19 retrieved -> 15 selected | 12.040285 | 14,065 |

The runs are `0ad74d85-5207-48c3-8e48-5882059bae2e` and
`6fd350c2-bbd1-4ef9-adb6-19bdcf7c9d5a`. Both have 9 executed nodes, 2 LLM
calls and no recorded errors. Reported LLM prices total USD 0.0339433 and
0.0309174 respectively; embedding/infrastructure and unreported charges are
excluded. All selected chunks and selection reports reached actual Writer
prompts. TOR registry/retrieval IDs match exactly as strings; the current
database IDs for all three source documents also match retrieved metadata.

The explicit-request answer separates TOR and SDS; selected-content spot
checks support its details. SDS includes a TOR appendix, which is repeated
material rather than independent corroboration. Citation resource metadata
includes all selected chunks, including unused ER candidates; UI badges and
formal claim-level citation precision were not evaluated.

Owner Code 2 fixtures passed all four requested cases: true retains an
other-source candidate at rank 17; false preserves top 15; STRICT returns
only the selected source; no other candidate yields `not_retrieved`.
The identical standalone candidate passed 29 offline tests, including required
anchors, strict filtering, false-string handling, ALL and unresolved mapping.
The live pair already had other-source candidates within the first 15, so it
does not independently demonstrate rank-17 rescue.

Earlier STRICT and unknown-source runtime checks, Code 1/Code 2 node tests,
and registry ambiguity fixtures are separate evidence. Latest full ALL,
STRICT, unknown and ambiguous-source regressions are not claimed. No
p50/p95, repeatability, optimal-cap, Project B or isolation conclusion follows
from these diagnostics.

## Continuation and local evidence

Continue trusted AW5 `tenant_id` enforcement as separately scoped backend work.
Do not derive project authorization from user text, model scope, filename
filters or Dify's internal Workspace tenant ID. Preserve the generic workflow;
no new routing branch, ID normalizer or model call is indicated by this review.
After import, verify Workspace Knowledge Base references and bind the correct
runtime database/provider credentials before invoking the app.

Local-only evidence packages under `output/research-evidence/experiments/`:

- `2026-10-03-test4-7-v3-other-source-intent-pair/`: two latest full runs.
- `2026-10-03-test4-7-v3-other-source-owner-node-results/`: four owner fixtures.
- `2026-10-03-test4-7-v3-boolean-form-incident/`: compatibility fix and 29 tests.
- `2026-10-03-test4-7-v3-unresolved-fallback-owner-run/`: earlier unknown fallback.
- `2026-10-03-test4-7-v3-final-review/`: installed source, ID bridge and limits.
- `2026-10-03-test4-7-v3-4-owner-export-preservation/`: export integrity and identity.

These packages are ignored/private and will not accompany a fresh Git checkout;
this sanitized record carries the configuration and evidence summary. Detailed
answers, chunks, runtime prompts and source text must remain local-only.
Preserving this snapshot did not invoke/import/modify/Publish Dify or authorize
commit, push, runtime registration changes or another evaluation run.
