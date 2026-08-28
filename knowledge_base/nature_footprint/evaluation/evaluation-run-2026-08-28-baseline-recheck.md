# AW5-RAG Baseline Recheck — 2026-08-28

## Purpose

Re-run the 19 executable v1 evaluation cases through the current Published Dify Service API before deciding whether the heavier Production Core workflow should become the development base. The API trace exposed the expected 9-step source-routing architecture with two LLM calls:

```text
START -> LLM 1 -> Route Queries -> Retrieve TOR / SDS / ER
      -> Merge Context -> LLM 2 -> Answer
```

The raw sanitized runner output remains under the ignored `output/evaluation/` directory. It contains no API key, dataset IDs, full prompts, or retrieved chunk text.

## Primary-run results

| Metric | Result |
| --- | ---: |
| Executable cases | 19 |
| Route match | 19/19 |
| Successful primary executions | 18/19 |
| Eventual citation-source boundaries after bounded retry | 19/19 |
| Strict semantic quality after bounded retry | 16/19 |
| Median end-to-end latency | 13.87 s |
| Mean end-to-end latency including provider stalls | 39.75 s |
| p95 end-to-end latency including provider stalls | 228.50 s |
| Median latency for successful cases below 60 s | 12.75 s |
| p95 latency for successful cases below 60 s | 21.79 s |
| Median total tokens | 4,856 |
| Mean total tokens | 5,057 |
| Total primary-run tokens | 96,083 |
| Recorded LLM-node price | approximately USD 0.1314 total |

Every question executed all three retrieval nodes, for 57 retrieval executions across 19 cases, even though Merge Context included only sources enabled by the route. Because the retrievers execute in parallel, conditional retrieval is primarily a cost/load optimization and is expected to save only the slowest retrieval duration on the critical path.

## Demonstrated semantic failures

### ER-01 — incomplete schema answer

The authoritative ER query contained all six required identifiers:

`UM_USER`, `UM_ROLE`, `UM_USER_ROLE`, `UM_FUNCTION`, `UM_ROLE_FUNCTION`, `UM_USER_ORG`

Retrieval and citation routing were correct, but LLM 2 omitted `UM_FUNCTION`. The loss occurred during answer generation, not routing.

### XDOC-02 — incomplete cross-document answer

The primary LLM 2 call failed with Gemini `503 UNAVAILABLE` due high demand. A bounded retry succeeded with TOR, SDS, and ER citations, but the answer omitted `UM_USER` and `UM_USER_ORG` even though the ER query contained the complete six-table set. This is both a provider-reliability event and a semantic completeness failure.

### EDGE-03 — unsupported inference from insufficient evidence

The answer correctly found no named AWS, Google Cloud, or Azure provider, but one run omitted the SDS Cloud/Offsite-storage distinction and a retry strengthened the unsupported conclusion to “does not use external cloud.” The safe conclusion is only that the documents do not specify which named cloud provider is used.

## Provider and latency observations

- `TOR-03`: LLM 1 took 227.88 s while retrieval and LLM 2 remained normal.
- `XDOC-01`: LLM 1 took 207.26 s while the answer remained correct.
- `XDOC-02`: the primary LLM 2 call failed with Gemini `503 UNAVAILABLE`; a retry succeeded in 41.03 s.
- An `ER-01` diagnostic retry also encountered a provider failure.

These events must be reported separately from workflow semantic quality. The primary-run median is representative of the normal path; the mean and p95 expose operational provider risk.

## Decision

Use `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml` as the primary development base and performance control. Production Core v1 improved strict semantic quality in its recorded regression (`18/19`) but required four LLM calls, 27 nodes, median latency about 23.17 s, and median usage about 9,622 tokens. It remains a safety-heavy experiment rather than the main line.

The next candidate should be a lean adaptive derivative of the baseline:

1. execute only routed retrieval sources;
2. preserve explicit schema identifiers and requested facets from the existing route as an answer contract;
3. run deterministic post-answer coverage checks where exact anchors exist;
4. invoke repair only when those checks fail; and
5. enforce a deterministic insufficient-evidence directive for unsupported provider claims.

The default path should retain two LLM calls. Any third model call must be conditional and justified by a detected failure.

## Limits

- This is one full primary run plus bounded diagnostic retries, not a stability proof.
- The Service API node trace structurally matched the baseline, but a new owner export is required to prove byte-for-byte equality with the repository YAML.
- `ISO-01` remains excluded until a synthetic Project B fixture and trusted tenant/project filtering exist.
- Provider availability and model behavior can change; compare candidates in the same test window and knowledge-base state.
