# AW5 Natural Answer V9.1 Correctness Cleanup Candidate — 2026-09-11

Status: frozen research comparator. It remains an isolated Draft that has not
been Published or promoted; Test4.2 is the owner-confirmed primary candidate as
of 2026-09-12.

This candidate is derived from Natural Answer V9 and makes only the requested
correctness cleanup. The preserved V9 export remained byte-identical at SHA-256
`6a975a7677d50fb16df4d33c24fa68a247f1825319b76f19e3b0444f6ef388fc`.

## Static change record

- Graph after import and export: **9 nodes / 8 edges / 2 LLM nodes**.
- Removed `Code 1`; no node was added.
- Rewired every former `Code 1.original_query` consumer to `sys.query`:
  - Knowledge Retrieval query
  - `Prepare retrieved evidence.query`
  - Evidence Selector user prompt
  - `Validate Evidence Ledger.query`
  - Final Answer user prompt
- Removed the unused `language` field from the Evidence Selector structured
  output. Nothing downstream consumed it. The selector prompt and remaining
  `facets` schema behavior were otherwise preserved.
- Reused the existing IF/ELSE node after `Validate Evidence Ledger` and renamed
  it `Validated evidence exists?`.
- Exact condition before invoking `Write grounded answer`:
  `Validate Evidence Ledger.accepted_quote_count > 0` as a number comparison.
- The false branch returns the existing deterministic insufficient-evidence
  response and does not invoke the Final Answer LLM.
- Candidate export SHA-256:
  `0d72301d424f4c2166b7587b399c722c441e73ff33bc60a7b2d1440a8ec41e35`.

Knowledge Retrieval remains Top K 30 with vector/keyword weighting `0.7/0.3`,
reranking disabled, and the same three Knowledge Base references. The selector,
validator, `source_score`, comparison-marker and quote-normalization behavior,
Final Answer model and prompt, conversation memory, and `sys.files` behavior are
unchanged apart from the direct query selectors and removal of the unused
structured-output field described above.

## Bounded smoke diagnostic

The owner authorized three exploratory tests against the isolated Draft and
authorized transmission of retrieved private project evidence to the configured
Gemini cloud models for these tests.

| Case | Result | Retrieved chunks | Accepted quotes | Branch | Final Answer LLM | Wall time | Reported tokens | Reported cost |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Normal answerable | Pass | 17 | 1 | true | invoked | 6.815 s | 9,137 | USD 0.014088 |
| Irrelevant / no answer | Pass after one operational retry | 18 | 0 | false | not invoked | 1.861 s | 8,793 | USD 0.0134895 |
| Chunks retrieved but none validated | Pass | 21 | 0 | false | not invoked | 4.011 s | 10,540 | USD 0.0161475 |

The first attempt of the irrelevant case exceeded the 20-second cutoff before
retrieval completed, was stopped, and reported no model usage. Its permitted
fresh-conversation retry completed and passed. This is retained as an
operational reliability anomaly rather than representative latency.

The critical invariant passed in both zero-evidence cases:

`accepted_quote_count = 0 -> false branch -> no Final Answer LLM -> deterministic fallback`

Detailed questions, answers, node traces, timings, citations and limitations are
retained locally under
`output/research-evidence/experiments/2026-09-11-v9-1-correctness-cleanup-smoke/`.
This three-case exploratory diagnostic is not a formal evaluation and does not
establish repeatability, production readiness or trusted tenant isolation.

Rollback/source snapshot: `aw5-rag-natural-answer-v9-candidate-2026-09-10.yml`.
