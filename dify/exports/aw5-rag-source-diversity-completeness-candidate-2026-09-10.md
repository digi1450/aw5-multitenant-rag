# AW5 RAG source-diversity and completeness candidate — 2026-09-10

## Identity

- Candidate DSL: `aw5-rag-source-diversity-completeness-candidate-2026-09-10.yml`
- Application label retained from the owner export: `AW5-RAG Test4 - ER Table Chunk Candidate`
- Repository candidate SHA-256: `e5f079b82328cd30c165321cae818e65334d3187650a52c81662598bee4942c2`
- Tested pre-normalization YAML SHA-256: `4c353b7fae10ab71d0585fe6b3fb22d01f062ea8d9f1e10f019c0e325c4446cb`
- Owner-supplied source export: `AW5-RAG Test4 - ER Table Chunk Candidate-2.yml`
- Owner-supplied source SHA-256: `fabccacb061c9eeb8dd16de347c13501c4d4c98299b2d50a119893916fa3c67a`
- Previous rollback export SHA-256: `7a2f2dfbc326a094c1810f8dc8b5596ae2d53b6ea2f3d6c4ba49b936e5f6cc75`

## Intended changes

The candidate changes two workflow values relative to the rollback export:

1. Code 2 reserves the first available result from each retrieved document for unrestricted questions, then fills the remaining positions in original retrieval order up to the existing limit of 10.
2. The answer prompt adds generic requested-facet completeness, authorization-scope precision, and source-specific schema validation rules plus corresponding final checks.

The changed code and prompt contain no corpus-specific filenames, dataset IDs,
expected answers, test questions, or source mappings. Existing Knowledge Base
references remain in the workflow's retrieval configuration.

## Source correction

The supplied export contained the intended Code 2 block at the same indentation level as its `else:` statement, which would raise `IndentationError`. The repository candidate corrects only that indentation while preserving the supplied prompt change. The supplied file is retained byte-for-byte in the local evidence package for provenance.

Before Git preservation, trailing spaces on empty YAML values were removed. This
changes the repository-file hash but not the parsed graph or values. The local
evidence package retains the exact YAML used for the targeted runtime gate under
the tested pre-normalization hash above.

## Static validation

- YAML parsed and round-tripped successfully.
- Graph remains 8 nodes / 7 edges.
- Every Code 2 Python block parses successfully.
- Generic source-diversity behavior passed with three synthetic document names.
- Explicit named-source restriction still selects only the matched source.
- An explicitly restricted but unavailable source still returns no evidence.
- Semantic comparison with the rollback export reports only the Code 2 source-selection code and LLM system prompt as changed.
- Secret-pattern scan found no credential or API-key material.

## Published seven-case gate

The owner corrected and Published the live Draft. Read-only PostgreSQL inspection
identified Published workflow
`1f9a9082-e39a-4ed8-b5ff-d745f03e0cb3`, version
`2026-09-10 07:02:36.217445 UTC`. Its normalized graph matched this stored
candidate after replacing portable Knowledge Base references and excluding
UI-only fields.

The frozen seven-case regression produced:

- 2 pass: `UC-11`, `UC-19`
- 3 partial: `UC-06`, `UC-09`, `UC-18`
- 2 fail: `UC-13`, `UC-20`
- 8 attempts for 7 selected answers; one `UC-06` attempt stopped at the
  20-second cutoff while the LLM was running
- selected latency p50 5.990 seconds, p95 7.196 seconds, maximum 7.495 seconds
- reported selected-answer usage: 57,909 tokens / USD 0.120321

Local-only package:
`output/research-evidence/experiments/2026-09-10-source-diversity-completeness-seven-case-gate/`.
Its `manifest.json` SHA-256 is
`ee5b6741c39df6ef354d5347a53e5d921932260f6326eb12743dd3628cd824ce`.

## Status and evidence boundary

**Published and tested candidate; seven-case gate failed; not promoted.**

The previous export remains the rollback snapshot. The document-diversity
change ensured that all three document names reached the answer context, but it
did not ensure that the relevant passage from each document was selected.
Prompt-only completeness and source-separation rules also did not resolve every
verified omission or schema merge. Do not run the full 20-case suite or promote
this candidate from this result.
