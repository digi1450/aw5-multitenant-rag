# AW5 Test3 prefilter and empty-evidence guard diagnostic — 2026-09-09

**Exploratory diagnostic; not a formal evaluation or workflow promotion.**

The owner authorized the previously proposed 12 end-to-end runs and six frozen-evidence replays. The App API identity was verified as AW5-RAG Test3. Its Published workflow had removed the disabled obsolete source-filter condition that remained in the supplied export; other export differences were UI/export flags.

## Verified outcomes

- Twelve Published API runs completed in fresh conversations: six query forms, twice each, no timeout or retry.
- Two unnamed-query runs fully answered the requested project code and full name. The ten other runs did not complete the requested task. This deliberately targeted sample is not general accuracy and must not replace the historical 13/20 evaluation.
- Full Thai filename and abbreviation returned only SDS. English filename and two-document comparison returned TOR but lacked the project-code passage. Factor-history questions lacked ER.
- Code 2 exposed actual source metadata. Presence of a document among results was insufficient when the relevant passage was absent.
- Six frozen-evidence replays preserved text evidence. Four also had identical rendered prompts to their API seed. Two unnamed replays had three image attachments in the rendered Draft prompt versus zero in their API seed, so they are not exact multimodal-context repeats. This path difference requires separate investigation.
- An additional empty-fixture execution reached the fixed Answer 2 in 0.650 seconds without executing the LLM.
- Residual generation issues included source-appendix confusion, overbroad absence claims, official project-name versus application-label conflation, and Thai answers to English queries.

## Timing and usage

Published requests: p50 3.816 seconds, nearest-rank p95 7.955 seconds (n=12). Retrieval p50 0.952 seconds, p95 4.012 seconds. The small sample is not an operational guarantee.

The twelve API answers reported 68,172 tokens / USD 0.114378 (5,681 tokens per request on average). All eighteen answer calls reported 110,238 tokens / USD 0.185547. Twelve retrieval executions additionally used embeddings; embedding cost, hidden retries and unreported charges are excluded. No exact provider HTTP-call count is claimed.

## Decision and next work

Keep the source metadata and empty-evidence guard. Do not promote Test3 as a demonstrated quality improvement. The primary next diagnostic is missing-passage recall at KB and final-selection layers, followed by a controlled original-query versus confidently resolved filename-separated query comparison. Dynamic document identity alone cannot recover missing evidence. Inspect ER table boundaries before choosing reindexing or a reranker. Preserve original user questions and avoid case-specific routing, expected answers or source quotas.

After sufficient evidence is available, test generation grounding and language adherence on frozen evidence. Investigate API-versus-Draft image forwarding separately before interpreting multimodal repeatability or token differences. Context compression and history changes remain untested proposals.

## Evidence and limits

Local-only package: `output/research-evidence/experiments/2026-09-09-test3-prefilter-guard/`, including `report.md`, `evidence.json`, `manifest.json`, pre/post exports, run plan, selected API traces, replay traces and Knowledge Base/document/parent-segment checksum references.

Original Test3 Published and Draft graphs were unchanged at final readback. The replay copy was restored and remains unpublished. No corpus edits, reindexing, model changes, Git commit/push or promotion occurred.

Assessment is assistant-reviewed, not independent grading. Missing answers and unsafe hallucinations are different outcomes. Per-KB pre-merge candidates were not captured, so exact ranking/embedding/index causes remain unverified. Citation resources alone do not prove claim-level correctness. No held-out evaluation, multi-turn, tenant-isolation, concurrent-load or full vector-index reproducibility claim is made.
