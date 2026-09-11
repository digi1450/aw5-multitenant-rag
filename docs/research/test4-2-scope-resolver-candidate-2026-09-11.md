# Test4.2 Scope Resolver candidate — evidence handoff

## Status and scope

Test4.2 is the **owner-confirmed primary candidate and qualified frozen
candidate for the Test4.2 experiment stage** as of 2026-09-12. It is not the
owner-confirmed current main workflow, a production-readiness claim, or a formal
tenant-isolation result. Preserve it unchanged. Any later architecture
experiment must start from a duplicate/new candidate. V9.1 remains the frozen
research comparator, Test4.1 is the previous candidate, and the owner-confirmed
2026-09-06 workflow remains current main until Test4.2 is explicitly promoted.

This record summarizes the retained local-only raw logs under
`output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/`
and a static, read-only inspection of the owner-supplied export
`AW5-RAG Test4.2 - Scope Resolver Candidate.yml`. The supplied export was not
copied into the repository because this documentation task did not authorize
renaming, recreating, or modifying the frozen workflow. Its inspected SHA-256
was `905fc9557905b8a9941f157e69370cf64b8583e9778e9405b1d33ed7008ca987`.

No workflow, prompt, model, Knowledge Base, retrieval setting, metadata,
dataset, Code 2 logic, branch, answer configuration, or experiment fixture was
changed or run while preparing this handoff.

The five raw `.txt` logs contain retrieved private project excerpts, document
and dataset identifiers, and runtime trace identifiers. They are **local-only
evidence and must not be committed**. They are stored with the package's local
`report.md`, `evidence.json`, and `manifest.json`. Their identities at review
time are:

| Evidence file | SHA-256 |
| --- | --- |
| `gate-a-resolver-robustness.txt` | `30241f224e91fd61e9085639828250dcc607f771b02db0032ed8ece307a1afd7` |
| `gate-b-known-source-e2e.txt` | `4af1b1c799601f14d46315146aaa8fadd6aecc1f58e671a2ba822411ea1bb1e9` |
| `b06-resolver-stability.txt` | `e9e1db32a0ce7c72486a4496e79496872f255ff9b8e225006ead4ee017e59c76` |
| `gate-c-fail-open.txt` | `1584df36eda1e4b140bf697a3d97ac7aae60ee3879d455f7769e1c5f38e5a353` |
| `final-candidate-regression.txt` | `2e5d7ff11bd013cd360d0c4cf621c7d4a8c77eed47cf834f8f4b9cee56273020` |

## Causal record: Test4.1 to Test4.2

The architecture history has three distinct states:

1. **Frozen Test4.1 candidate:** `User query -> Knowledge Retrieval` with
   metadata filtering disabled `-> Code 2 source restriction/post-filter ->
   IF/ELSE -> Answer LLM or deterministic fallback`.
2. **Intermediate rejected experiment:** Dify stock Automatic Metadata
   Filtering was tested during the transition and was rejected because its
   routing was highly sensitive to query wording. Test4.1 was then restored to
   metadata filtering disabled. Owner/conversation history recalls an
   approximately `1/10` successful strict/source-routing trial, but its raw log
   is not in the five preserved Test4.2 evidence files. That value is not a
   raw-log-backed result and is not used to qualify Test4.2.
3. **Frozen Test4.2 candidate:** `User query -> Scope Resolver -> retrieval_query`
   for semantic search, with `scope` controlling Dynamic Manual Metadata
   Filtering `-> Knowledge Retrieval -> Code 2 -> IF/ELSE -> Answer LLM or
   deterministic fallback`.

| Stage | Evidence-backed record |
| --- | --- |
| Observed problem | Test4.1 was source-aware, but its preserved repository snapshot had metadata filtering disabled and resolved exact filename/stem or canonical `document_type` restrictions in Code 2 after retrieval. It did not provide a general, verified way to translate natural source-attribution and source-exclusion language into a retrieval scope before retrieval. |
| Hypothesis | A dedicated upstream Scope Resolver could translate natural-language intent into a small generic contract more reliably than wording-sensitive Automatic Metadata Filtering or corpus-specific routing rules embedded in application code. |
| Controlled change | Add one Scope Resolver LLM before the existing retrieval path. Feed its `retrieval_query` to Knowledge Retrieval and its `scope` to Dynamic Manual Metadata Filtering. Leave the downstream Knowledge Retrieval → Code 2 → IF/ELSE → answer/fallback structure intact. |
| Expected behavior | Generic questions use `ALL/NON_STRICT`; source attribution uses the named source with `NON_STRICT`; explicit exclusion uses the named source with `STRICT`; exact filenames may route directly; unknown sources must return no evidence rather than fall open to `ALL`. |
| Experiments | Gate A tested resolver behavior over 24 queries; Gate B tested eight known-source end-to-end cases; B06 was repeated ten times at the resolver; Gate C tested two unknown-source paths; a final ten-case end-to-end regression covered the qualified matrix. |
| Observed result | Gate A is semantically 24/24 after diagnosing a checker false negative; Gate B retained one real routing anomaly; the anomaly did not reproduce in ten resolver-only attempts; Gate C was 2/2 fail-closed; the final regression was 10/10 structural with no critical safety or routing/STRICT failure in that matrix. |
| Decision | Keep and freeze Test4.2 for this experiment stage. Preserve the Gate B anomaly and evidence limits. Reject Automatic Metadata Filtering for this candidate architecture; do not modify Test4.2 in place. |

## Architecture facts

Static inspection of the supplied frozen export and the retained execution logs
supports the following facts:

- Graph: `User Input -> Scope Resolver -> Knowledge Retrieval -> Code 2 ->
  IF/ELSE`; the true branch runs `LLM -> Answer`, while the false branch returns
  deterministic `Answer 2`.
- Scope Resolver: `gemini-3.5-flash`, structured output enabled, with exactly
  `scope`, `strict`, and `retrieval_query` required by the schema.
- Retrieval uses `retrieval_query` as its query. `scope` is interpolated into
  Dynamic Manual Metadata Filtering, which ORs the generic contracts
  `search_scope contains scope`, `source_file is scope`, or built-in
  `document_name is scope`.
- `strict` is produced and scored as part of the resolver contract, but the
  frozen export has no downstream selector, condition, filter or branch that
  consumes it. In Test4.2, source-specific `STRICT` and `NON_STRICT` outputs
  therefore use the same scope-driven retrieval filter.
- In the current frozen Test4.2, `strict` is classification/protocol output
  only; it is not downstream execution control. For example, both `ตาม TOR ...`
  (`scope = TOR`, `strict = NON_STRICT`) and `ใช้เฉพาะ TOR ...`
  (`scope = TOR`, `strict = STRICT`) execute TOR-filtered retrieval because
  `scope`, rather than `strict`, controls the filter. Test4.2 does not yet
  implement different fallback, retrieval or writer behavior for these two
  classifications.
- The inspected Scope Resolver prompt uses generic placeholders rather than
  corpus-specific filenames, aliases, or test answers.
- The retained tests verify emitted `STRICT`/`NON_STRICT` values and observed
  source results for their matrices. They do not demonstrate a separate
  strictness-controlled execution path or establish a universal authorization
  or tenant-isolation boundary.
- The qualified resolver model for this frozen candidate is Gemini 3.5 Flash.
  The `metadata_model_config` retained inside the retrieval node is not the
  active Automatic Metadata Filtering path because `metadata_filtering_mode` is
  `manual`.

The repository's preserved Test4.1 export records
`metadata_filtering_mode: disabled`; its source-aware restriction logic occurs
in Code 2 after retrieval. Therefore the stronger statement that the preserved
Test4.1 snapshot itself used Dynamic Manual Metadata Filtering is not supported
by the inspected repository artifact. Test4.2 is the inspected artifact that
demonstrates the upstream resolver-controlled manual filter.

## Experiment observations

### Gate A — resolver robustness

Local-only raw file: `output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/gate-a-resolver-robustness.txt`

- Automated first pass: **23/24** overall.
- Scope: **24/24**; strictness: **24/24**.
- The apparent EN04 rewrite failure returned the correct
  `ER / STRICT / Whether CM_STAT exists` contract.
- The checker searched for the alias `ER` as a substring and found it inside
  the ordinary word `Whether`. This was a harness false negative, not a resolver
  routing failure.
- Corrected semantic result: **24/24 PASS**. The raw log remains unchanged and
  continues to show its original `23/24` and `GATE_A_FIRST_PASS = FAIL` output.
- The extra EN04 retests also include one 37.2-second resolver call. It is an
  observed latency outlier, not evidence of a semantic routing failure.

### Gate B — known-source end-to-end matrix

Local-only raw file: `output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/gate-b-known-source-e2e.txt`

- Structural result: **7/8 PASS**.
- B06 asked which table `CM_STAT` connects to in ER and expected
  `ER / NON_STRICT`.
- One actual run returned `ALL / NON_STRICT`; retrieval consequently included
  SDS, ER, and TOR. This is a real observed routing anomaly and must not be
  normalized into an 8/8 result.
- The completed answer remained evidence-bounded and did not invent a
  `CM_STAT` relationship. This distinguishes a routing failure from a
  demonstrated factual hallucination.

### B06 resolver stability retest

Local-only raw file: `output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/b06-resolver-stability.txt`

- Configuration was not changed before the targeted retest.
- Ten resolver-only attempts returned `scope = ER`,
  `strict = NON_STRICT`, and the intended semantic query: **10/10 PASS**.
- Reproduction attempts: **10**; reproduced failures: **0**.
- This narrows the observed anomaly to a non-reproduced event under the tested
  conditions. It does not prove that routing can never fail again.

### Gate C — unknown-source fail-open safety

Local-only raw file: `output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/gate-c-fail-open.txt`

- Unknown-source NON_STRICT and STRICT cases: **2/2 PASS**.
- Both retained `scope = ABCXYZ.pdf`, returned zero evidence, set
  `has_evidence = false`, selected the false branch, executed deterministic
  fallback, and skipped the answer-writing LLM.
- No TOR, SDS, or ER source leaked into retrieval in these two runs.
- This behavior resulted from the resolved unknown `scope` producing no match
  in Dynamic Manual Metadata Filtering. It was not enforced by downstream use
  of `strict`, because the frozen graph does not consume that field.
- This is positive fail-closed evidence for the tested cases, not proof that
  metadata-filter fail-open is impossible under all inputs or environments.

### Final candidate regression

Local-only raw file: `output/research-evidence/experiments/2026-09-11-test4-2-scope-resolver-qualification/final-candidate-regression.txt`

- Coverage: generic ALL; TOR/SDS/ER NON_STRICT; TOR/SDS/ER STRICT; exact
  filename; unknown-source NON_STRICT; unknown-source STRICT.
- Structural result: **10/10 PASS**.
- Critical safety failures: **0**; routing/STRICT failures: **0**.
- End-to-end latency: mean **5140.22 ms**, p50 **5005.32 ms**, minimum
  **2813.39 ms**, maximum **7713.25 ms**.
- The clean final regression qualifies the freeze decision for this experiment
  stage. It does not erase the earlier B06 anomaly or establish production-grade
  reliability.

## Rejected approach

Dify Automatic Metadata Filtering is not part of Test4.1 or Test4.2. It was an
intermediate transition experiment: the owner records that it was highly
wording-sensitive, it was rejected, and Test4.1 was restored to metadata
filtering disabled before Test4.2 introduced resolver-controlled Dynamic Manual
Metadata Filtering. Owner/conversation history recalls an approximately `1/10`
successful strict/source-routing trial, but the rejection raw run is not among
the five preserved Test4.2 logs. Accordingly, `1/10` is retained only as
owner/conversation history, not as a formally raw-log-backed result. The
evidence-backed repository conclusion is that Automatic Metadata Filtering was
rejected and its rejection log is not currently preserved in this package.

## Harness and debugging incidents

- During development, a `model_selector: null` field allowed backend execution
  but crashed the Dify editor. Removing the null key was a frontend/data
  normalization repair, not a model or architecture experiment. The inspected
  frozen export and logs confirm that the key is now absent.
- An early Gate B harness attempt raised SQLAlchemy
  `DetachedInstanceError`. Session handling was corrected before the retained
  eight-case matrix. The exception is not present in the final five evidence
  logs, so it is recorded as owner-provided harness history and is not counted
  as a Test4.2 workflow/model failure.

Neither incident changes Gate A/B/C or final-regression scores.

## Known limitations

1. **Evidence presence is not evidence sufficiency.** Code 2 uses nonempty
   retrieval output for `has_evidence = true`; it does not determine whether
   the chunks are semantically sufficient to answer the question.
2. **Answer proportionality remains variable.** The writer may return more
   grounded detail than requested, such as a full schema for an existence
   question or many VALUE-related fields for a broad query. The observed extra
   content is an answer-quality/proportionality issue, not a demonstrated
   hallucination.
3. **No NON_STRICT secondary fallback exists.** The `strict` output is not
   consumed downstream, and Test4.2 does not run a second cross-source retrieval
   when the preferred source is insufficient. Its intended future semantic role
   is to permit an explicitly designed secondary cross-source retrieval for
   `NON_STRICT`, while `STRICT` remains source-isolated. That distinction is
   future architecture and is not current Test4.2 behavior.
4. The measured matrices do not prove zero error, zero hallucination, perfect
   routing, production-grade reliability, or source isolation for every query.
5. These tests do not verify trusted AW5 `tenant_id` enforcement before
   retrieval.

## Future experiments — not implemented

Possible later experiments are semantic evidence-sufficiency gating, a bounded
NON_STRICT secondary retrieval strategy, and writer proportionality. Each must
use a duplicate/new candidate, state the failure it addresses, preserve STRICT
source boundaries, and collect separate correctness, citation, latency, cost,
and reliability evidence. None is part of Test4.2 and none was implemented by
this documentation update.

## Evidence boundary and freeze decision

Architecture facts above come from static inspection of the supplied frozen
export. Experiment observations come from the five retained raw logs. The
Automatic Metadata Filtering rejection and the two debugging incidents include
owner-provided history whose raw precursor artifacts are not in this evidence
set. Keeping those classes separate prevents a configuration fact, harness
repair, or owner decision from being promoted into an experiment result.

The frozen YAML is not stored in this repository; this review identifies the
owner-supplied file by its SHA-256. Reproduction therefore also requires that
exact export and the recorded runtime dependencies.

**Decision:** Test4.2 is frozen as the qualified primary candidate for this
experiment stage. V9.1 remains the frozen research comparator, Test4.1 remains
the previous candidate, and the 2026-09-06 workflow remains current main until
an explicit Test4.2 promotion. Future work must preserve this evidence and
branch from a duplicate rather than edit Test4.2 in place.
