# Test3 candidate-stage diagnostic — 2026-09-09

**Exploratory, partial completion.** Existing Published Test3 settings were used without workflow or corpus changes. One retrieval-only question completed; UC-11 collection failed twice and was stopped. No answer LLM calls were made.

For the named TOR question, all three Knowledge Bases returned 10 candidates. The relevant TOR child was third within TOR but 13th globally (score 0.458249). The final Top K of 10 selected only SDS candidates (minimum score approximately 0.4909), reconstructed into seven parents. This locates the loss at the cross-KB cutoff for this trace. Retrieval completed in 7.979 seconds; no repeatability or formal accuracy claim follows.

The direct instrumented service call is not an exact end-user API replay. Two UC-11 host collections exceeded 45 seconds without a retained complete trace; actual retrieval completion and enforcement of the configured 20-second internal cutoff are unknown. These attempts have no semantic score. A broader mapping audit also failed collection; unmatched IDs from the initial join are not proof of stale indexes or changed chunks.

Next: repair diagnostic collection handling before more runtime tests, then compare common relevance ranking over the same candidate pool under separate authorization. Source enrichment alone cannot recover discarded evidence. No production promotion or reranker/reindex change is justified by this single trace.

Local private evidence: `output/research-evidence/experiments/2026-09-09-test3-candidate-trace/` (`report.md`, `evidence.json`, `manifest.json`, scripts and retained attempts). Embedding usage/cost was not measured. Current main is unchanged.
