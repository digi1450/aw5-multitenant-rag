# AW5 Natural Answer V9 Candidate — 2026-09-10

Status: untested Draft candidate. It has not been Published.

This candidate changes the final response stage so the answer is written as a normal, concise response instead of exposing internal facet labels such as `ประเด็นที่ 1`. Exact evidence is still selected and validated before the final writer receives it. Duplicate claims from compatible sources may be merged in the prose while source metadata remains available for Dify citations.

Static inspection:

- 10 nodes and 9 edges
- 2 LLM nodes
- no corpus-specific filename, document ID, dataset ID, expected answer, or test-question routing was added to code, prompts or branches; existing Knowledge Base references remain in retrieval configuration
- exported with `include_secret=False`
- no API key, secret key, authorization header, or bearer-token marker found
- export SHA-256: `6a975a7677d50fb16df4d33c24fa68a247f1825319b76f19e3b0444f6ef388fc`

Runtime correctness, citation behavior, latency, and cost have not been tested for V9. Import and run it as a separate candidate before promotion.

Rollback snapshot: `aw5-rag-structured-evidence-v8-1-candidate-2026-09-10.yml`.
