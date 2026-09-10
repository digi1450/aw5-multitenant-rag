# AW5 RAG improvement plan — 2026-09-09

Status: owner-requested investigation and proposed experiments; not an implemented architecture, promotion, or new formal evaluation.

Follow-up: the owner subsequently authorized the [isolated layer-separation diagnostic](rag-layer-diagnostic-2026-09-09.md). It completed 12 answer calls and identified an additional first-priority change: bypass answer generation when no usable evidence is returned. It also confirmed parser failure and missing ER evidence, with residual grounding issues under sufficient table fixtures. The proposal below remains a plan; only the linked diagnostic and offline resolver checks have been executed.

## Inspection and identity

Read-only inspection of local Docker/PostgreSQL confirmed that AW5-RAG Test2's active Published workflow remains `77d702d8-fc78-4fe8-8850-0c2c6ec7e77e`, version `2026-09-07 11:30:16.917465`. Its current Draft node data equals Published node data after excluding the UI `selected` field. Draft updated_at is `2026-09-08 18:30:19.035309` as returned by PostgreSQL; a newer edit timestamp does not demonstrate a configuration change. This comparison covers node data, not corpus/index identity or complete graph byte identity.

The inspected path is:

`User Input -> Code 1 -> Knowledge Retrieval -> Code 2 -> LLM -> Answer`

The repository's owner-promoted main remains the separate five-node 2026-09-06 snapshot. The 13/20 result applies to the six-node evaluated snapshot, not that main export. No runtime configuration was changed and no inference/evaluation was run during this review. Small local Regex probes were executed.

Live configuration:

- Code 1 extracts filename-like strings; one match becomes `source_filter`, otherwise an empty string.
- Retrieval uses manual `source_file contains source_filter`; its query is still the original `sys.query`.
- Three KBs all currently use high-quality hybrid retrieval, Top K 10, semantic/keyword weights 0.7/0.3, no model reranker, and disabled score threshold. Node-level final Top K is also 10. These are two selection layers, not a guarantee that every source will reach the answer model.
- Code 2 prefixes document_name and dataset_name while copying result objects. It does not recover missing evidence, deduplicate, enforce a context budget, resolve aliases, or establish document authority.
- Answer model is gemini-3.5-flash, Minimal thinking, output cap 6,601, history window 10. Temperature is not explicitly set on this answer node. The stored metadata-model temperature 0 is not proof of an automatic-filter call: the active mode is manual.
- The prompt already requests completeness, provenance, conflict separation, insufficient-evidence handling, and resistance to document instructions. Adding the same checklist again is not a demonstrated solution.

## Evidence and limits

The 2026-09-07 formal run recorded 13 pass, 4 partial, 3 fail; 39 attempts and 11 timeouts. Its 4.186 s p50 / 14.287 s p95 describe selected completed answers, not retry-inclusive user waiting time. Reported selected usage was 103,537 tokens / USD 0.234393 (approximately 5,177 tokens and USD 0.01172 per selected answer); stopped attempts and other unreported charges are excluded.

All three failed cases lacked a required source. UC-11 and UC-13 missed ER; UC-20 missed TOR and ER. UC-06, UC-09, UC-18 and UC-19 had unsupported generalization or omitted facets. Returned document presence alone does not establish that every necessary passage reached the LLM. API citation resources also do not prove claim-level entailment or capture the complete intermediate candidate pool.

Earlier automatic-metadata diagnostics alternated TOR/SDS retrieval even at temperature 0. Those used different graphs. They justify investigating that mechanism and retaining manual controls, but do not establish the root cause of any remaining variation in the current manual workflow. Exact generated automatic conditions were not preserved.

Sources: `self-hosted-real-use-case-evaluation-2026-09-07.md`; local reports under `output/research-evidence/experiments/2026-09-07-real-use-case-formal-evaluation/`, `2026-09-07-test2-temp0-repeatability-diagnostic/`, and `2026-09-07-conversation-memory-filename-diagnostic/`.

## Confirmed parser behavior and unresolved risks

Local probes reproducing the current extraction expressions showed:

| Input | Extractor output / problem |
| --- | --- |
| Thai question followed by Attach_TOR_1.pdf | Extracts the filename |
| What is the project code in Attach_TOR_1.pdf? | Captures `What is the project code in Attach_TOR_1.pdf` as the filename |
| Unquoted Thai filename | No filename detected |
| TOR without an extension | No filename detected |
| TOR.pdf and tor.pdf | Two distinct names; filter becomes empty |
| Two explicitly named files | Filter becomes empty; no representation of the requested pair |

Other risks requiring verification: partial-name collisions with `contains`; missing/null metadata behavior with an empty condition; unknown or misspelled filenames; Unicode normalization; duplicate versions; names in document content being mistaken for provenance; and filtering away a second source needed by a cross-document question.

The previous suggestion to automatically hard-filter whenever a filename is mentioned is too broad for AW5's existing design contract. Naming a source establishes an attribution requirement, not automatically an exclusive search scope. The default remains broad retrieval within the authorized project. Exclusive source selection should be explicit product behavior (for example, a user-selected file scope), separately agreed and tested. A document resolver must never grant tenant access.

## Proposed shortest normal path

`Trusted project scope -> resolve document references and query intent -> one authorized-corpus retrieval -> evidence packaging -> one answer LLM -> lightweight output validation`

These are responsibilities, not a requirement to create one Dify node per box. Reuse Code 1/Code 2 where practical. Ordinary questions should require one answer-model call. No unconditional second judge, repair LLM, or per-file retrieval branches are proposed.

1. Resolve document references against an authorized document registry populated at ingestion. Store canonical identity, display name, optional aliases, source checksum, version and explicit authority where known. Do not embed TOR/SDS/ER mappings or known answers in prompts/code. Ambiguous abbreviations must not silently choose one source.
2. Keep the original user question. A separate retrieval-query candidate may remove only confidently resolved filename spans while retaining entities, identifiers, clauses, negation and comparison intent. Compare this with the unchanged query; do not adopt arbitrary user-word deletion. If a filename is itself the requested content, preserve it. Unknown names should be reported accurately rather than silently treated as a successful file selection.
3. Use explicit optional document scope rather than relying on `contains ""` as an off switch. Verify the exact supported Dify implementation before choosing an ID filter or equivalent backend restriction. All search/retry paths must retain trusted tenant authorization.
4. Package coherent evidence with stable source references, document identity/version, available section/page metadata and intact citation objects. Deduplicate repeated parents and enforce a measured token budget without cutting a table, requirement list or necessary comparison side. Never invent page numbers. A code check can validate reference membership; it cannot prove factual support.
5. Keep a concise generic answer contract: cover requested facets, bind claims to evidence, expose conflicts/uncertainty, and avoid treating previous assistant answers as evidence. Validate citation IDs and output completion deterministically; semantic completeness still needs evaluation.

## Staged experiments and stop criteria

### A. Freeze and locate the failing layer

Before tuning, preserve Published export, effective model parameters, KB settings, source/chunk checksums and ordered evidence identity. Capture original query, resolved mentions, effective filters, candidates before/after final selection where observable, final context hash/order/token count, answer, citations and per-stage timing. Instrument embedding/provider, vector search and local CPU/RAM/I/O only for relevant diagnostic windows.

Proposed diagnostic matrix: exact filename / alias / no filename; fresh / continuing conversation; repeated retrieval with fixed settings; then repeated answer generation using a frozen evidence package, question and history. Use a third offline condition with independently verified sufficient evidence to estimate whether retrieval or generation is the dominant limit. Replay is an experimental capability to build; existing sanitized citations alone are insufficient for exact prompt replay.

Interpretation: changed filter -> reference resolution; same filter but different candidates -> retrieval/index/provider path; same ordered context and history but different correctness -> generation; same context plus different history -> history sensitivity. A document list match is not enough: compare actual context hashes. Fixing one stage cannot establish repeatability of another.

### B. Repair reference handling without increasing model calls

Replace free-text Regex matching as the final authority with registry-backed resolution. Add local cases covering English prefixes, Thai/Unicode names, quoting, case, escapes, abbreviations, unknown names, duplicate names across projects, multiple files, and mere mentions versus explicit scope. Compare broad retrieval with the current manual condition before selecting product behavior. Keep original questions available to the LLM.

### C. Improve evidence recall and context efficiency

Inspect failed-case candidates at both KB and node levels before editing chunks. If evidence is not in the candidate pool, reranking cannot recover it. Audit ER table boundaries/relationships and TOR headings/lists across pages. Preserve originals and work in a rollback-capable candidate ingestion state; do not universally rewrite every field or reindex the entire corpus before identifying the missing units.

Compare one variable at a time: query representation; candidate limits/weights; table/section-aligned chunk repair; optional reranker; final evidence budget. Model reranking is conditional on demonstrated ranking failure and must include added provider cost/latency and image compatibility. Larger candidate pools need not become larger LLM contexts. No fixed per-file quota is assumed to improve relevance.

Exhaustive schema enumeration cannot be guaranteed by similarity Top K. Keep the existing `er-exhaustive-column-lookup-contingency.md` deferred; activate a deterministic derived catalog or narrow read-only structured lookup only if exhaustive queries become a real requirement.

### D. Improve answer completeness with fixed evidence

Audit missing facets against the exact final context. Do not lower the rubric to hide source/version conflicts; have a reviewer adjudicate acceptable source-specific answers and whether a required-source label is justified. SDS/ER differences must remain unresolved unless the owner establishes authority.

Compare the present prompt with a shorter generic prompt and separately compare Minimal versus Low thinking using the same frozen evidence. Keep the current model initially. The 6,601 output cap is a ceiling, not usage; measure input, output and thinking tokens separately. Shortening output blindly can cause truncation. Keep history bounded and test follow-up questions: current retrieval reads only sys.query, so a question such as “and its permissions?” lacks a resolved subject. Add conditional follow-up resolution only when this failure is demonstrated; never insert previous model answers as trusted document evidence.

### E. Operational reliability and bounded recovery

Investigate the ten Retrieval stalls before attributing them to local hosting or assuming cloud migration fixes them. Use per-stage deadlines, cancellation and bounded retry; confirm stopped tasks actually terminate before retrying to avoid concurrent orphan work and duplicated charges. Existing diagnostic default: 20 s cutoff, at most one fresh retry, then stop/report. A changed formal protocol requires explicit agreement.

Report both per-attempt reliability and full user request time/cost including retries. Distinguish service failure from insufficient evidence. Consider embedding/result caching only after correctness is established; keys must include authorization scope, corpus/index version, query/filter, model/configuration and relevant history, with invalidation on updates or revoked membership. Do not use cached answers to claim model repeatability.

### F. Final evaluation and deployment boundary

Retain the existing 20 cases as a development regression set. After repeated tuning, they are not a held-out measure of generalization. Freeze a new independently reviewed held-out use-case set and rubric, then run repeated trials with a predeclared retry policy. A provisional design is three fresh-session repeats per case plus separate multi-turn sequences; report uncertainty, not just an average score. Record all attempts, do not select the best answer or retry semantic failures until they pass.

Proposed pilot targets for owner agreement (not universal standards or current achievements): strict correctness at least 90% on an adequate held-out suite; no material fabricated source attribution; p50 <=5 s / p95 <=15 s for ordinary requests measured end-to-end; timeout/error rate <=1% in a sufficiently large operational sample. Report complex questions separately. A small 60-trial batch cannot establish a precise 1% failure bound. Latency must not be bought by incomplete answers. Start cost comparison from current selected-answer usage but establish an all-attempt baseline before setting a total cost cap; improvements must not inflate prompt/context cost without a measured quality gain.

Before multi-tenant release, implement trusted membership-derived tenant_id enforcement and synthetic conflicting Project B tests. Also cover corpus updates/deletion, stale caches/history, concurrent users, KB partial outages, user/document prompt injection, malformed or missing metadata, citation/source collisions, table/image evidence loss, missing-evidence refusals, backup/restore and access revocation. No corpus-specific fix or high semantic score substitutes for authorization testing.

## External references and limits

- Dify Knowledge Retrieval: https://docs.dify.ai/en/cloud/use-dify/nodes/knowledge-retrieval — documents two selection layers, metadata filtering, structured retrieval output and multimodal caveats. Current documentation is conceptual guidance; deployed 1.17.0 behavior must be verified locally.
- Gemini 3.5 guide: https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5 — recommends default sampling parameters and describes Minimal/Low effort tradeoffs. Temperature zero is not this plan's stability fix; model guidance does not prove AW5 quality.

## Immediate next work

The minimal trace/replay capability, offline registry-backed resolver probe and
approved layer-separation diagnostic have now been completed. Subsequent
September 10 experiments showed that source-name diversity alone does not ensure
relevant-passage coverage, while structured exact-quote validation reduced
unsupported source use in the targeted cases. Natural Answer V9 is the latest
stored Draft candidate and remains untested.

Next, run a bounded fresh-session diagnostic of V9 that checks normal answer
presentation, claim-level citations, requested-facet coverage, end-to-end and
node latency, tokens and reported cost. Preserve the V8.1 export as rollback.
Do not promote V9 from static structure alone. Trusted project-tenant enforcement
and `ISO-01` remain separate release blockers rather than workflow-prompt fixes.
