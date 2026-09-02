# Lean Adaptive v1.4 Full Regression — 2026-08-29

## Status and scope

- Candidate: `AW5-RAG Lean Adaptive v1.4 Candidate`
- Executable cases: 19
- Execution: Dify Service API, streaming mode
- Primary run: one pass through all 19 cases without configuration changes
- Bounded retry: `ER-02` once after a Gemini `503 UNAVAILABLE`
- User-visible citation checks: `ER-01`, `XDOC-02`, and `EDGE-03` in Dify UI
- Raw sanitized traces: retained only under ignored `output/evaluation/`

This report separates semantic RAG quality, user-visible citations, workflow
latency, and provider reliability. The Service API stream returned empty
`retriever_resources` even when Dify UI citations were correct, so this run does
not claim a 19/19 API citation audit.

## Primary-run metrics

| Metric | Result |
| --- | ---: |
| Route match | 19/19 |
| Successful primary executions | 18/19 |
| Provider failures | 1/19 (`ER-02`, Gemini 503) |
| Primary latency p50 | 9.10 s |
| Primary latency mean | 9.80 s |
| Primary latency p95 | 14.66 s |
| Primary latency range | 5.84–14.66 s |
| Primary tokens | 113,879 |
| Mean primary tokens/question | 5,994 |
| Recorded primary LLM price | USD 0.1658 |
| Conditional Repair executions | 2/19 (`EDGE-03`, `EDGE-04`) |

The failed `ER-02` execution reached LLM 2 with correct ER-only routing and six ER
chunks, then failed after 11.58 seconds with Gemini `503 UNAVAILABLE`. Its bounded
retry succeeded in 5.64 seconds with 4,627 tokens and returned `UM_USER`,
`WRONG_PWD_COUNT`, `IS_LOCK`, and `LAST_ATTEMPT_LOGIN` correctly.

Including the failed call and bounded retry, the measured API consumption was
118,506 tokens and approximately USD 0.1714, or about USD 0.0090 per delivered
answer for this run.

## Effective latency after bounded retry substitution

For semantic comparison only, replacing the failed `ER-02` duration with its
successful bounded retry gives:

| Metric | Result |
| --- | ---: |
| p50 | 8.94 s |
| mean | 9.32 s |
| p95 | 13.34 s |
| range | 5.64–13.34 s |

This substitution does not erase the failed call or its cost. Operationally, the
user experienced a failed attempt followed by retry, so provider reliability must
remain a separate release constraint.

## Semantic and citation observations

Manual review of the returned answer text found all expected factual facets after
the bounded `ER-02` retry. The three failures demonstrated by the 2026-08-28
baseline recheck were corrected:

- `ER-01`: all six required UM tables; ER-only route and user-confirmed ER-only UI
  citation;
- `XDOC-02`: TOR two levels, SDS three groups, and all six ER tables; user-confirmed
  TOR + SDS + ER UI citations;
- `EDGE-03`: stated only that AWS, Google Cloud, and Azure are not specified, while
  reporting the NSTDA server evidence; user-confirmed TOR + SDS UI citations.

`EDGE-03` and injection case `EDGE-04` invoked the conditional Repair path. They
used 13,950 and 13,793 tokens respectively in the primary run. The Repair rate was
2/19 (10.5%), isolated to the named-provider evidence boundary.

The provisional semantic result is 19/19 after bounded provider retry. A strict
19/19 citation score is not claimed because only the three targeted cases were
manually verified in the Dify UI and the current Service API citation stream is not
usable as citation evidence.

## Baseline comparison

| Metric | Baseline recheck (2026-08-28) | Lean v1.4 (2026-08-29) |
| --- | ---: | ---: |
| Route match | 19/19 | 19/19 |
| Strict/provisional semantic after retry | 16/19 strict | 19/19 provisional semantic |
| Primary p50 | 13.87 s | 9.10 s |
| Primary mean | 39.75 s | 9.80 s |
| Primary p95 | 228.50 s | 14.66 s |
| Primary tokens | 96,083 | 113,879 |
| Recorded primary price | ~USD 0.1314 | ~USD 0.1658 |

The latency comparison is not a controlled model-load experiment: the baseline run
contained two extreme provider stalls, while v1.4 did not. v1.4 used about 18.5%
more primary tokens and about 26.2% more recorded primary price. Including its
failed call and bounded retry, the measured price was about 30.5% above the
baseline primary-run price.

## Usability decision

> **Historical recommendation, superseded on 2026-09-02.** The owner has since
> confirmed the [single-retrieval, self-hosted Dify direction](../../../docs/architecture/current-direction-2026-09-02.md).
> The recommendation below is not the current work sequence. Results, limitations,
> and the original rubric remain unchanged; no new evaluation has been run.

v1.4 is a stronger Phase 1 candidate than the fresh baseline on the three targeted
semantic failures. It is suitable for continued prototype evaluation, but it is
not yet production-ready:

1. one of 19 primary calls failed due provider high demand;
2. two provider-boundary cases more than doubled token use through Repair;
3. the user observed UI response times above 20 seconds, while the Service API
   workflow p95 was 14.66 seconds, so browser/UI end-to-end timing remains unmeasured;
4. only three cases have user-verified UI citation precision in this run; and
5. tenant/project isolation and `ISO-01` remain outside Phase 1.

The next optimization should target the provider-boundary contract so `EDGE-03`
and `EDGE-04` normally pass on the two-LLM path, then repeat the same suite. Do not
weaken evidence grounding merely to remove Repair. Separately measure user-perceived
request-to-render latency in the UI and retain a bounded retry policy for transient
provider errors.
