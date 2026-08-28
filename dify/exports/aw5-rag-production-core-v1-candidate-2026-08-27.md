# AW5-RAG Production Core v1 Candidate — 2026-08-27

## Artifact

- DSL: `aw5-rag-production-core-v1-candidate-2026-08-27.yml`
- SHA-256: `1c51fe4a3e942f7950208a4b58ef80f9614127b89c777354b46250581b17bbca`
- Source: `aw5-rag-route-guard-candidate-2026-08-27.yml` plus the verified live Merge selector correction
- App name inside DSL: `AW5-RAG Production Core v1 Candidate`
- Graph: 26 nodes / 31 edges
- Status: local structurally validated candidate; not imported, Published, or evaluated live

## Architecture

```text
START
  -> LLM 1 source planner
  -> Route Queries normalization
  -> ROUTE GUARD (single route authority)
  -> conditional TOR / SDS / ER retrieval
  -> Merge Context
  -> Evidence Sufficiency LLM
  -> Normalize Evidence Decision
  -> Evidence Gate
       IF sufficient
         -> LLM 2 draft
         -> Answer Verifier LLM
         -> Finalize Verified Answer
       ELSE
         -> Insufficient Evidence Response
  -> Select Final Response
  -> Answer
```

## Changes justified by evaluation evidence

1. **Single route authority** — Gate, Retrieve, Merge, and diagnostics use `ROUTE GUARD`; this removes the split-authority wiring found in the prior export.
2. **Fail-closed normalized queries** — blank queries remain blank, generic fallback retrieval is disabled, repeated query tokens are removed, and enabled queries are capped at 200 characters.
3. **Security Design route control** — explicit `Security Design` questions are treated as SDS design questions unless database/schema evidence is explicitly requested.
4. **SDS Top K 5 candidate** — increased from 3 only in this candidate because `SDS-03`, `VIS-02`, `VIS-03`, and `XDOC-01` showed missing or conflicting SDS evidence. It must be retained only if before/after tests improve strict evidence quality.
5. **Evidence Sufficiency Gate** — exact references require direct evidence; a caption, table-of-contents line, nearby UI, or correct-document citation alone is insufficient.
6. **Safe insufficient-evidence branch** — unsupported exact facts do not reach the answer generator.
7. **Answer Verifier** — a second grounded LLM removes unsupported draft claims, repairs only Context-supported omissions, and emits a final answer plus diagnostic issues.

## Local validation

- YAML parsed successfully.
- All 26 node IDs are unique.
- All 31 edge endpoints exist.
- Every Code node compiles as Python.
- Every context/input/condition selector references an existing node or `sys`.
- Route Guard fixtures pass for explicit `Security Design`, source isolation, query de-duplication, and the earlier `TOR`/`INDICATOR` token-boundary defect.
- Evidence decision, insufficient response, and finalization fixtures pass.
- Secret-pattern scan must remain clean before commit.

## Expected trade-offs

- Evidence and answer verification add two LLM calls on answerable questions, increasing latency and model cost.
- The candidate should reduce unsupported answers, but it may return insufficient evidence more often until visual/OCR retrieval is improved.
- SDS Top K 5 may improve recall while adding irrelevant context; evaluation decides whether it remains.
- No node-level provider retry is encoded because retry/error-handler fields are not present in the verified DSL schema. A bounded Service API retry remains necessary until a Dify-supported node error branch is exported and validated.
- This candidate does not implement multi-tenant isolation, conversation memory, backend authorization, or `ISO-01`.

## Import and validation

1. Import the YAML as a **new app**; do not overwrite or unpublish the Route Guard baseline.
2. Confirm the app name is `AW5-RAG Production Core v1 Candidate`.
3. Confirm the canvas contains the seven new production-core nodes and that TOR/SDS/ER datasets plus all Gemini models resolve.
4. Do not change prompts or retrieval settings during import.
5. Publish only the new test app, create its Service API key, and store it under a new local prefix such as:

```dotenv
DIFY_AW5_PROD_V1_API_KEY=replace-locally
DIFY_AW5_PROD_V1_API_BASE_URL=https://api.dify.ai/v1
DIFY_AW5_PROD_V1_TEST_USER=aw5-codex-prod-v1-eval
```

6. Run targeted controls first: `SDS-03`, `VIS-02`, `VIS-03`, `XDOC-01`, `ER-01`, `SDS-02`, and `EDGE-04`.
7. If the candidate imports and targeted traces are structurally correct, run all 19 cases and compare strict answer/citation quality, latency, tokens, route authority, evidence-gate decisions, and verifier issues.

Do not promote this candidate unless it improves strict quality without hiding retrieval defects behind generic insufficient-evidence responses.
