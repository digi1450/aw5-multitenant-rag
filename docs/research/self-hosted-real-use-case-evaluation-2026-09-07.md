# Self-hosted real-use-case evaluation — 2026-09-07

## Status and evidence boundary

**Sanitized summary of an owner-authorized 20-case formal evaluation with a
supplementary repeated-retry phase.** Detailed answers, retrieved-chunk evidence,
and the English PDF report remain local-only under `output/`.

This run evaluated a live Published workflow that was newer than and different
from the repository's owner-confirmed 2026-09-06 current-main export. After the
run, the owner supplied `AW5-RAG Test2.yml`; its byte-identical repository
snapshot is
`dify/exports/aw5-rag-real-use-case-evaluated-2026-09-07.yml`, SHA-256
`3d3e588a93d56bc35c4176365939009995936fcd133aeda0c104747aa4992f93`.
The tested graph had 6 nodes / 5 edges:

```text
User Input -> Code 1 -> Knowledge Retrieval -> Code 2 -> LLM -> Answer
```

The export was correlated with a graph retained by `workflow_runs`. After
normalizing portable Knowledge Base references and UI-only canvas/selection
fields, both graphs were equal with normalized SHA-256
`72c100b664c15aaad40bd188d5676340f250bde2e93361876ade782a98389393`.

This run therefore applies to the evaluated 2026-09-07 snapshot. It does **not**
validate or promote either:

- `dify/exports/aw5-rag-self-hosted-main-2026-09-06.yml`; or
- `dify/exports/aw5-rag-automatic-metadata-temp0-candidate-2026-09-07.yml`.

The 2026-09-06 export remains the owner-confirmed current main. The automatic
metadata temperature-zero file remains an unpublished, unevaluated candidate,
while the 2026-09-07 six-node file is a tested but unpromoted snapshot.

## Frozen identity and configuration observed for the run

- Published version: `2026-09-07 11:30:16.917465`.
- Graph SHA-256:
  `0e59ff7964d24d6bffa4db767c8755b59ae9b3ff8228fc4ca94c348017dce66d`.
- System-prompt SHA-256:
  `412d7e9920fcdb8ce344bf5a3fd2d668a63e6e0c651b817289ced496a1a9a26a`.
- Dify API image: `langgenius/dify-api:1.17.0`.
- One Knowledge Retrieval node referenced the three current Knowledge Bases.
- Retrieval: multiple retrieval, Top K 10, semantic/keyword weights `0.7/0.3`,
  reranker disabled, and manual metadata filtering.
- Embedding: `gemini-embedding-2` through the AW5 plugin.
- Answer model: `gemini-3.5-flash`, Minimal thinking, 6,601 maximum output
  tokens.
- Each case started a fresh conversation.

## Protocol

The primary run used the frozen 20-case real-use-case suite, a 20-second
per-attempt cutoff, and bounded retry for operational stalls. After the primary
run, the owner directed the runner to repeat the same question until the local
Knowledge Retrieval completed, noting that its expected normal range was about
5–10 seconds.

The latest completed fresh-session answer for each case was used for semantic
scoring. Every stalled or stopped attempt remained part of the reliability
evidence. The supplementary repeated-retry instruction is a protocol deviation
and must be retained when comparing this run with future repeatability results.

## Results

| Measure | Result |
| --- | ---: |
| Strict pass | 13/20 (65%) |
| Partial | 4/20 (20%) |
| Fail | 3/20 (15%) |
| Pass or partial | 17/20 (85%) |
| Required-source coverage | 17/20 (85%) |
| Cases with a completed answer after retries | 20/20 |
| Total attempts | 39 |
| Timed-out attempts | 11/39 (28.2%) |
| Selected-answer latency p50 | 4.186 seconds |
| Selected-answer latency p95 | 14.287 seconds |
| Selected-answer latency maximum | 14.351 seconds |
| Reported selected-answer usage | 103,537 tokens / USD 0.234393 |

Reported usage is a lower bound because stopped attempts did not provide
complete usage records.

Ten attempts stopped while Knowledge Retrieval was still running. One
additional attempt completed Knowledge Retrieval in 18.294 seconds, leaving
1.375 seconds for the LLM before the task cutoff. Read-only aggregate node
records showed successful Retrieval p50 1.718 seconds, p95 11.586 seconds, and
maximum 18.294 seconds. These records verify the stalled node, but do not prove
whether the root cause was local Docker resources, the embedding plugin or
provider, network behavior, vector search, or another layer.

## Findings

1. All three failed cases lacked at least one required source. Two missed the ER
   artifact; the cross-layer auditability case missed both TOR and ER evidence.
2. Partial answers omitted requested facets or made an over-broad authorization
   statement. Missing facets included the time dimension, browser/device
   testing, and restore modes.
3. SDS and `er-dbdiagram.txt` are not field-identical for several tables,
   including `CALC_INTERMEDIATE_RESULT`. The run establishes a representation or
   version difference, but not which artifact is newer or authoritative.
4. Retrieval reliability is a release blocker independent of answer quality.
   Repeated retries produced a completed answer for every case, but do not erase
   the 28.2% attempt timeout rate.

## Recommended sequence

1. Instrument query embedding, plugin/provider calls, vector search, and
   container CPU/RAM/I/O separately before changing retrieval-quality settings.
2. Declare a canonical schema artifact with version, effective-date, and
   authority metadata.
3. Create a table-aligned ER retrieval candidate and retest the three failed
   cases before running the full suite.
4. Add a generic completeness and insufficient-evidence check, then retest the
   four partial cases.
5. Run the full suite repeatedly against a frozen export, corpus, prompt, and
   protocol before making repeatability or production-readiness claims.

## Local evidence

These artifacts remain ignored and local-only because they contain private
derived evaluation content:

- `output/research-evidence/experiments/2026-09-07-real-use-case-formal-evaluation/`
  - `report.md` SHA-256
    `68d4e1db1fef4f46d6e365dac217ef8bfd5290f57b8eb9ba3ed5572b76e4a58a`
  - `evidence.json` SHA-256
    `6d9855e9b0e6034a9c86c877765ab0720078f18bf143605b0379a6d7121a9cc4`
  - `manifest.json` SHA-256
    `c54c682c090d3c65501c78f0df5a177bcddc5c9bb6b9c9c64bcc5e06ab9d51a0`
  - `scores.json` SHA-256
    `6bcedd33e4bb1fc65187356112541b0b55f10b25548e455cdc3a8c592221fda5`
- `output/pdf/aw5-nature-footprint-real-use-case-evaluation-2026-09-07.pdf`
  SHA-256
  `a7b64d5d4869318d3c8dff309d868ffe8f62bfa9eeaaee0e572963521260d95c`.
- `output/evaluation/use-case-questions-2026-09-07/suite.json` SHA-256
  `2903a9b8956f4608b49b6a25db9ba6002eabc7d63ff963e0652a10a0b02ed171`.

No private question text, answers, retrieved chunk text, credentials, API key,
dataset ID, database dump, or vector-index data is included in this Git-safe
summary.

## Non-claims

This run does not establish production readiness, repeatability, tenant
isolation, cross-tenant authorization, current-main export quality, or the root
cause of local Retrieval stalls. Its semantic and reliability results apply to
`aw5-rag-real-use-case-evaluated-2026-09-07.yml` only.
