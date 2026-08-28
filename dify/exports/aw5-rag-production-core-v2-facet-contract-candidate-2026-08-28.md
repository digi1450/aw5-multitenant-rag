# AW5-RAG Production Core v2 Facet Contract Candidate — 2026-08-28

## Artifact

- DSL: `aw5-rag-production-core-v2-facet-contract-candidate-2026-08-28.yml`
- SHA-256: `7bfc598f377a34d06315d9694a1b008bd51a18dcfe66e5b03d5a2c2c97fa8a08`
- Builder: `../../scripts/build_dify_production_core_v2.rb`
- Source: `aw5-rag-production-core-v1-coverage-candidate-2026-08-28.yml`
- App name: `AW5-RAG Production Core v2 Facet Contract Candidate`
- Graph: 28 nodes / 33 edges
- Status: locally validated candidate; not imported, Published, or live-tested

## Architecture change

```text
Merge Context
  -> REQUEST FACET CONTRACT
  -> EVIDENCE SUFFICIENCY
  -> NORMALIZE EVIDENCE DECISION / contract integrity
  -> EVIDENCE GATE
       IF answerable
         -> LLM 2
         -> ANSWER VERIFIER
         -> FINALIZE VERIFIED ANSWER
         -> FINAL ANSWER COVERAGE CHECK
       ELSE
         -> INSUFFICIENT EVIDENCE RESPONSE
  -> SELECT FINAL RESPONSE
  -> Answer
```

`REQUEST FACET CONTRACT` decomposes the user request into independently answerable facets without answering it. `EVIDENCE SUFFICIENCY` must return exactly one evidence result for every facet. The normalize node derives the final decision from the facet map rather than trusting the judge's top-level decision.

## Deterministic integrity rules

- Every facet ID must have exactly one evidence mapping.
- Unknown, duplicate, missing, or malformed mappings fail closed.
- A supported facet must contain atomic supported facts and at least one exact required answer term per fact.
- Facet source must be enabled by `ROUTE GUARD`; `cross` requires a multi-source route.
- `request_terms` and `exact_reference` must appear in the user question or authoritative source queries.
- The final coverage node checks both the global required-term union and every supported facet's term list.
- A correct partial answer may be approved only when supported facets are covered and unavailable facets are explicitly bounded.

## Local validation

- YAML parsed successfully.
- 28 unique nodes / 33 valid edges form an acyclic graph.
- All 67 node/prompt selectors reference an existing node or trusted system variable.
- All embedded Python Code nodes compile.
- Build is deterministic with SHA-256 `7bfc598f377a34d06315d9694a1b008bd51a18dcfe66e5b03d5a2c2c97fa8a08`.
- Complete three-facet security fixture passed.
- Missing Audit Log facet evidence failed closed.
- Final answer omitting one Audit Log term failed coverage and identified `facet_3`.
- Secret-pattern scan found no API key, bearer token, credential, or client secret.

## Expected trade-offs

- One additional Gemini Flash call increases latency and cost.
- Fail-closed integrity may return more safe errors while the facet/evidence prompts are calibrated.
- The facet contract reduces silent omissions but does not prove semantic correctness until live repeated evaluation passes.
- Provider availability remains separate from semantic RAG quality.

## Promotion boundary

Keep `aw5-rag-source-routing-final-2026-08-25.yml` at commit `64418f8` as the verified `19/19` rollback baseline. Import this candidate only into a Production Core test app, verify the Published trace contains `REQUEST FACET CONTRACT`, and execute the staged evaluation plan before considering promotion.
