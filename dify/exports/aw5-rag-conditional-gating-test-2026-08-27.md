# AW5-RAG Conditional Retrieval Gating — Import Test

## Status

- DSL: `aw5-rag-conditional-gating-test-2026-08-27.yml`
- Source: `aw5-rag-source-routing-final-2026-08-25.yml`
- App name inside DSL: `AW5-RAG Conditional Gating Test`
- Local structural validation: passed as 18 nodes / 22 edges
- Live Dify import: **verified by Service API app identity and gated node traces**
- Live Service API behavior: **targeted conditional-gating controls passed**
- Published state: **test app is Service API-accessible; original AW5-RAG state was not changed by this validation**
- This file is an experiment and must not replace `CURRENT.md` or the frozen baseline until validated.

## Superseded by the live Route Guard export

The final live candidate was exported after adding the deterministic Route Guard and changing ER Top K from 6 to 7. Continue from `aw5-rag-route-guard-candidate-2026-08-27.yml`, not from the generated DSL documented here. Its status and remaining validation boundary are recorded in `CURRENT.md` and `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-route-guard-smoke.md`.

## Service API validation attempt — 2026-08-27

- `/info` returned app name `AW5-RAG`, not `AW5-RAG Conditional Gating Test`.
- `PERF-01` succeeded as an answer, but the trace contained the original 9 steps and no Gate or Variable Aggregator nodes.
- `Retrieve TOR`, `Retrieve SDS`, and `Retrieve ER` all executed while the observed route was TOR-only.
- Conclusion: the API key used for this attempt points to an ungated app/version. The conditional-gating DSL has **not** been validated live.

## Successful Service API validation — 2026-08-27

After replacing the key with one from the imported test app, `/info` returned `AW5-RAG Conditional Gating Test`. Four targeted calls then verified branch execution:

| Case | Observed route | Knowledge Retrieval nodes executed | Result |
|---|---|---|---|
| `PERF-01` | TOR only | `Retrieve TOR` | Gate pass; correct answer and TOR-only citations |
| `SRC-02` | SDS only | `Retrieve SDS` | Gate pass; correct SDS answer and citations |
| `ER-05` | SDS + ER | `Retrieve SDS`, `Retrieve ER` | Gate pass for the observed route; TOR did not execute. Router over-selection remains a separate defect because this schema question was expected to be ER-only. |
| `INJ-02` | no sources | none | Gate pass; all three Empty Results paths executed and no retrieval citation was returned |

- All four workflows succeeded with zero exceptions.
- Total usage: 19,163 tokens; USD 0.0253226 model price.
- Conditional retrieval is now live-verified: a disabled source does not execute its Knowledge Retrieval node.
- End-to-end latency is not proven to improve consistently. `PERF-01` took 26.371 seconds because LLM 2 alone took 23.869 seconds; provider/model latency remains a separate issue.
- This targeted validation does not replace the v1 `19/19` baseline and does not validate multi-tenant isolation.

## Full executable v1 regression — 2026-08-27

- The 19 executable v1 questions were rerun through the Service API.
- All 19 workflows completed, and conditional gating matched the observed router flags in all 19.
- Strict result: **12/19**, with seven failures across router/source precision, visual retrieval/query grounding, and answer completeness.
- No provider retry was used because no provider or transport failure occurred.
- Promotion status: **failed**. Keep this app as an experimental candidate and retain the original v1 `19/19` workflow as the verified correctness baseline.
- Detailed evidence: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-conditional-gating-v1-regression.md`

## Intended graph change

Each source now has an exclusive branch:

```text
Route Queries
  -> Gate SOURCE
       IF true  -> Retrieve SOURCE -> Select SOURCE Results
       ELSE     -> Empty SOURCE [] -> Select SOURCE Results
  -> Merge Context
```

`Select SOURCE Results` is a Dify Variable Aggregator with `array[object]` output. Merge Context reads its `output` variable. TOR, SDS, and ER use the same pattern and remain independent parallel branches.

Unchanged core data was compared against the frozen source export for Start, Answer, both LLM nodes, Route Queries, and all three Knowledge Retrieval nodes. The Merge Context Python code is unchanged; only its three result selectors now point to the aggregators.

## One-time import steps

1. In Dify Studio, import `aw5-rag-conditional-gating-test-2026-08-27.yml` as a new app.
2. Confirm the imported app is named `AW5-RAG Conditional Gating Test`; do not import over or Publish the original AW5-RAG app.
3. Confirm the canvas shows 3 Gate nodes, 3 Empty Results code nodes, and 3 Select Results Variable Aggregators.
4. Confirm the existing TOR, SDS, and ER datasets and model dependencies resolve successfully.
5. Publish only the test app when ready for Service API validation.
6. Create an API key for the test app and add these local-only variables to `.env.aw5.local` without removing the baseline variables:

```dotenv
DIFY_AW5_FIX_API_KEY=replace-locally
DIFY_AW5_FIX_API_BASE_URL=https://api.dify.ai/v1
DIFY_AW5_FIX_TEST_USER=aw5-codex-fix-eval
```

Do not paste the key into chat or commit `.env.aw5.local`.

## Validation gate

Run targeted Service API cases with:

```sh
python3 scripts/run_dify_diagnostic_v2.py --env-prefix DIFY_AW5_FIX --start 18 --limit 1
```

`PERF-01` passes the structural goal only if `node_finished` events show `Retrieve TOR` executing while `Retrieve SDS` and `Retrieve ER` do not execute. After that, run one SDS-only, one ER-only, and `INJ-02` no-source case before a limited v1 regression.
