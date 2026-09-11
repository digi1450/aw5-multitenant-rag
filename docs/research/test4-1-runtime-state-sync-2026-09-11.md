# Test4.1 runtime-state synchronization — 2026-09-11

## Scope

This is a static review and repository synchronization of the owner-supplied
`AW5-RAG Test4.1 - ER Table Chunk Candidate.yml`. The supplied YAML is the source
of truth for implementation. No Dify app, workflow setting, prompt, model,
Knowledge Base, corpus, benchmark or evaluation item was changed or run.

The byte-identical repository snapshot is
[`dify/exports/aw5-rag-test4-1-er-table-chunk-candidate-2026-09-11.yml`](../../dify/exports/aw5-rag-test4-1-er-table-chunk-candidate-2026-09-11.yml),
SHA-256
`842fd57728d4c2b173ebdc594ea3728a83f8d69d7436cd32a2871de79fe2bcef`.
The adjacent [snapshot record](../../dify/exports/aw5-rag-test4-1-er-table-chunk-candidate-2026-09-11.md)
contains the complete static configuration and discrepancies.

## Observed problem to current status

| Stage | Record |
| --- | --- |
| Observed problem | Code1 copied the query without transformation. Document balancing could force low-ranked sources into a ten-item context. Exact filename restrictions worked, while canonical source labels were not deterministically filtered. |
| Hypothesis | Remove the identity node, preserve original retrieval rank on ordinary queries, and read the canonical source identity from the actual custom-metadata location. |
| Investigation | Owner-inspected execution traces compared raw and selected ranks and inspected raw retrieval metadata. Custom fields were found under `metadata.doc_metadata`. |
| Root cause | Context selection assigned capacity by document rather than relevance. Custom `document_type` had been sought at the wrong metadata level. |
| Current implementation | Direct `sys.query` propagation; retrieval-order first ten valid items on the normal path; exact filename/stem plus nested canonical `document_type` restriction; source provenance prefix; nonempty-context IF guard. |
| Diagnostic evidence | Owner reports raw ranks 1-10 were preserved and six targeted semantic cases passed. This task did not rerun or independently validate those diagnostics. |
| Current status | Historical at synchronization: Test4.1 was the production-oriented candidate. Owner status update on 2026-09-12: Test4.1 is now the previous candidate, Test4.2 is the primary candidate, and V9.1 is the frozen research comparator. This status change did not alter the preserved Test4.1 export. |
| Remaining risk | Deterministic restriction vocabulary and missing-canonical-source behavior have gaps; `has_evidence` is not semantic validation; formal correctness, latency, cost, reliability and tenant isolation remain unverified. |

## Engineering decisions retained

- **Code1 removal:** cleanup / behavior-preserving refactor.
- **Document balancing removal:** experimental context-selection change.
  Relevance-preserving Top10 is a provisional keep supported by targeted
  engineering diagnostics, not benchmark proof.
- **Nested metadata lookup:** source-resolution bug fix. Built-in physical
  filename remains at `metadata.document_name`; custom canonical identity is at
  `metadata.doc_metadata.document_type`.
- **Canonical source restriction:** exact physical filename/stem and exact
  canonical type token are distinct mechanisms.
- **Alias boundary:** broad natural-language aliases are not implemented.
- **Guard semantics:** `has_evidence` means Code 2 emitted at least one context
  item; it does not establish relevance or entailment.

## Evidence boundary

The six-case Top10 regression, canonical TOR/SDS/ER restrictions and prior
five-versus-five Test4/V9.1 diagnostic are owner-reported engineering evidence
from earlier runtime work. This synchronization preserves their stated status
without promoting them to formal evaluation or publication evidence. No result
is transferred to Development-36, V9.1 or a future experimental variant.

## Protected state

- Frozen V9.1 SHA-256 remained
  `0d72301d424f4c2166b7587b399c722c441e73ff33bc60a7b2d1440a8ec41e35`.
- Corrected Development-36 datasets, sampling artifacts and human-review pack
  were not edited.
- Frozen methodology files were not edited.
- Held-out question text was not authored.
- No benchmark item was marked `gold_verified`.
- No V9.1, Test4.1, Development-36, Held-out or A/B/C/D inference was run.
