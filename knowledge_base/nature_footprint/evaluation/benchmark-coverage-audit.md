# Benchmark Sampling Coverage Audit

Status: pre-authoring allocation audit. Held-out rows are planning records only and contain no question text or answers.

## Totals

### development

- Items: 36
- Language: {'th': 24, 'en': 6, 'th_en': 6}
- Answerability: {'all': 27, 'partial': 5, 'none': 4}
- Difficulty: {'simple': 6, 'moderate': 15, 'complex': 15}

#### primary_category × answerability

| primary_category | all | none | partial | Total |
|---|---:|---:|---:|---:|
| complete_list | 4 | 0 | 0 | 4 |
| conflicting_sources | 1 | 0 | 0 | 1 |
| cross_document_comparison | 3 | 0 | 0 | 3 |
| duplicate_information | 2 | 0 | 0 | 2 |
| evidence_boundary_no_answer | 0 | 2 | 1 | 3 |
| explicit_source_restriction | 2 | 1 | 1 | 4 |
| multi_document_trace | 4 | 0 | 1 | 5 |
| multi_facet | 2 | 0 | 2 | 4 |
| schema_er | 4 | 1 | 0 | 5 |
| simple_single_fact | 5 | 0 | 0 | 5 |

#### primary_category × language

| primary_category | en | th | th_en | Total |
|---|---:|---:|---:|---:|
| complete_list | 1 | 3 | 0 | 4 |
| conflicting_sources | 0 | 1 | 0 | 1 |
| cross_document_comparison | 1 | 2 | 0 | 3 |
| duplicate_information | 0 | 2 | 0 | 2 |
| evidence_boundary_no_answer | 1 | 1 | 1 | 3 |
| explicit_source_restriction | 0 | 3 | 1 | 4 |
| multi_document_trace | 0 | 4 | 1 | 5 |
| multi_facet | 0 | 3 | 1 | 4 |
| schema_er | 2 | 2 | 1 | 5 |
| simple_single_fact | 1 | 3 | 1 | 5 |

#### difficulty × language

| difficulty | en | th | th_en | Total |
|---|---:|---:|---:|---:|
| complex | 2 | 12 | 1 | 15 |
| moderate | 2 | 9 | 4 | 15 |
| simple | 2 | 3 | 1 | 6 |

#### difficulty × answerability

| difficulty | all | none | partial | Total |
|---|---:|---:|---:|---:|
| complex | 11 | 1 | 3 | 15 |
| moderate | 11 | 2 | 2 | 15 |
| simple | 5 | 1 | 0 | 6 |

### held_out

- Items: 72
- Language: {'th': 50, 'en': 12, 'th_en': 10}
- Answerability: {'all': 54, 'partial': 12, 'none': 6}
- Difficulty: {'moderate': 27, 'simple': 17, 'complex': 28}

#### primary_category × answerability

| primary_category | all | none | partial | Total |
|---|---:|---:|---:|---:|
| complete_list | 7 | 0 | 1 | 8 |
| conflicting_sources | 2 | 0 | 1 | 3 |
| cross_document_comparison | 5 | 0 | 1 | 6 |
| duplicate_information | 3 | 0 | 0 | 3 |
| evidence_boundary_no_answer | 0 | 3 | 3 | 6 |
| explicit_source_restriction | 5 | 2 | 1 | 8 |
| multi_document_trace | 8 | 0 | 2 | 10 |
| multi_facet | 6 | 0 | 2 | 8 |
| schema_er | 8 | 1 | 1 | 10 |
| simple_single_fact | 10 | 0 | 0 | 10 |

#### primary_category × language

| primary_category | en | th | th_en | Total |
|---|---:|---:|---:|---:|
| complete_list | 1 | 6 | 1 | 8 |
| conflicting_sources | 0 | 2 | 1 | 3 |
| cross_document_comparison | 1 | 4 | 1 | 6 |
| duplicate_information | 1 | 2 | 0 | 3 |
| evidence_boundary_no_answer | 1 | 5 | 0 | 6 |
| explicit_source_restriction | 1 | 6 | 1 | 8 |
| multi_document_trace | 1 | 7 | 2 | 10 |
| multi_facet | 2 | 5 | 1 | 8 |
| schema_er | 2 | 7 | 1 | 10 |
| simple_single_fact | 2 | 6 | 2 | 10 |

#### difficulty × language

| difficulty | en | th | th_en | Total |
|---|---:|---:|---:|---:|
| complex | 7 | 18 | 3 | 28 |
| moderate | 4 | 19 | 4 | 27 |
| simple | 1 | 13 | 3 | 17 |

#### difficulty × answerability

| difficulty | all | none | partial | Total |
|---|---:|---:|---:|---:|
| complex | 22 | 2 | 4 | 28 |
| moderate | 20 | 2 | 5 | 27 |
| simple | 12 | 2 | 3 | 17 |

## Findings

- Development matches the frozen category totals (36), language target (24 Thai, 6 English, 6 mixed), and answerable/unanswerable boundary (27 all-supported; 5 partial and 4 none).
- Held-out planning matches the frozen category totals (72), language target (50 Thai, 12 English, 10 mixed), and answerable/unanswerable boundary (54 all-supported; 12 partial and 6 none).
- Unanswerable facets span list, multi-facet, schema, multi-document, source-restricted, comparison, conflict and evidence-boundary categories.
- English and mixed-language allocations include moderate and complex items; difficult cases are not confined to Thai.
- Schema, multi-document and source-restricted categories include multiple language/difficulty conditions.
- Partial-answer cases appear in both splits and across multiple primary categories.

## Sparse cells and limitations

- The dataset is intentionally not a balanced Cartesian matrix. Small categories such as duplicate information and conflicting sources cannot cover every language, difficulty and answerability cell.
- Held-out conflict items are only planning slots. They require two directly verified incompatible passages on the same comparison dimension before authoring; any slot without such evidence must remain draft or be reallocated before freeze.
- Hostile-document-content fixtures remain unallocated because no approved isolated synthetic corpus exists.
- The local ER-diagram PDF is not indexed in the frozen Knowledge Bases, so it is excluded from intended-source allocations.
- No serious category/language/difficulty confounding is present in the proposed allocation. Human reviewers must repeat this audit after held-out wording and evidence are authored.

## Development-36 authoring QA correction — 2026-09-11

- Structure audit result: PASS; no dangling facet/fact/evidence references, unknown source IDs, quote-hash mismatches, restriction leaks, comparison-source gaps or answerability/behavior mismatches.
- Development wording classes: `{'source_agnostic': 20, 'source_explicit_optional': 3, 'source_explicit_required': 13}`.
- Held-out planning wording classes: `{'source_agnostic': 39, 'source_explicit_optional': 6, 'source_explicit_required': 27}`; these are allocation tags only and contain no question text.
- Expected facts: `144`.
- Evidence links: `154`.
- Unsupported facets: `10` across `9` items.
- All five simple-single-fact items contain exactly one expected fact after correction.
- DEV-020 now names the two SDS components whose chapter names are requested.
- DEV-023 now uses the SDS data dictionary as semantic bridging evidence and keeps DBML declarations literal.
- DEV-029 is bounded to six predeclared candidate fields and records twelve atomic source-specific presence decisions.
- Human verification decisions and reviewer identities remain blank; all 36 items remain draft.

## Source-wording allocation by category

### Development 36

| primary_category | source_agnostic | source_explicit_optional | source_explicit_required | Total |
|---|---:|---:|---:|---:|
| complete_list | 4 | 0 | 0 | 4 |
| conflicting_sources | 0 | 0 | 1 | 1 |
| cross_document_comparison | 0 | 0 | 3 | 3 |
| duplicate_information | 2 | 0 | 0 | 2 |
| evidence_boundary_no_answer | 3 | 0 | 0 | 3 |
| explicit_source_restriction | 0 | 0 | 4 | 4 |
| multi_document_trace | 0 | 0 | 5 | 5 |
| multi_facet | 4 | 0 | 0 | 4 |
| schema_er | 2 | 3 | 0 | 5 |
| simple_single_fact | 5 | 0 | 0 | 5 |

### Held-out 72 planning

| primary_category | source_agnostic | source_explicit_optional | source_explicit_required | Total |
|---|---:|---:|---:|---:|
| complete_list | 8 | 0 | 0 | 8 |
| conflicting_sources | 0 | 0 | 3 | 3 |
| cross_document_comparison | 0 | 0 | 6 | 6 |
| duplicate_information | 2 | 1 | 0 | 3 |
| evidence_boundary_no_answer | 6 | 0 | 0 | 6 |
| explicit_source_restriction | 0 | 0 | 8 | 8 |
| multi_document_trace | 0 | 0 | 10 | 10 |
| multi_facet | 8 | 0 | 0 | 8 |
| schema_er | 5 | 5 | 0 | 10 |
| simple_single_fact | 10 | 0 | 0 | 10 |
