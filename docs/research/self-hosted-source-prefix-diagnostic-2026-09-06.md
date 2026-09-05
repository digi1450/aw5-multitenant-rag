# Self-hosted source-prefix diagnostic — 2026-09-06

## Classification

**Targeted exploratory diagnostic.** This report preserves a sanitized summary
for project handoff. It is not a formal evaluation, release gate, or replacement
for historical scored evidence. Raw answers, retrieved text, segment metadata and
runtime traces remain local-only under `output/research-evidence/experiments/`.

## Question and change under test

The diagnostic examined two demonstrated failures in the simple self-hosted
workflow:

1. Dify's LLM Context rendering passed retrieved content without the source
   metadata needed to enforce named-document attribution consistently.
2. TOR section 4.7.5 crossed a parent-chunk boundary after item (5), so the
   retrieved TOR parent omitted items (6)–(9).

The owner added one deterministic Code node after the existing Knowledge
Retrieval node. It prefixes each retrieved content value with the item's
`document_name` and `dataset_name` while retaining result order and other fields.
The owner also moved TOR items (6)–(9) into the parent containing their section
heading and regenerated its child chunks. No metadata filter, reranker, answer
model, retrieval weight, Top K value, source router, or extra LLM call was added.

## Compared Published runs

Both runs used the same five questions in fresh conversations through the local
Published Service API. Each attempt had a 20-second cutoff and one permitted
retry. Neither accepted run set required a retry.

| State | Published path | Pass | Partial | Fail | Wall-time median |
| --- | --- | ---: | ---: | ---: | ---: |
| Before publishing Code | Retrieval -> LLM | 2 | 2 | 1 | 2.355 s |
| After publishing Code | Retrieval -> Code -> LLM | 4 | 1 | 0 | 4.207 s |

The after-state result was:

| Case | Result | Sanitized finding |
| --- | --- | --- |
| TOR section continuation | Pass | Returned all nine items and attributed them to the named TOR pages. |
| SDS `ORG_LOCATION` | Pass | Returned the six SDS fields without adding ER-only audit/version fields. |
| ER `ORG_LOCATION` | Pass | Returned all ten ER fields with their documented types and constraints. |
| SDS/ER comparison | Pass | Kept both field lists separate and reported their retrieved differences. |
| TOR/SDS indicator comparison | Partial | Recognized both sources and the same four categories, but overstated them as identical in every respect. |

The final five runs completed in 3.614–5.610 seconds. Knowledge Retrieval took
1.698–2.180 seconds, Code took 0.030–0.048 seconds, and the LLM took
1.618–3.563 seconds. The answer model reported 21,634 tokens and USD 0.048096 in
total; embedding cost was not included.

## Verified runtime boundary

Read-only Dify database inspection confirmed that the after-state Service API
runs used Published workflow ID `6e57ac51-4428-42eb-8410-edecfccda87e` and the
five-node path `start -> knowledge-retrieval -> code -> llm -> answer`. Every
rendered LLM prompt contained the source prefixes. This distinguishes the final
run from the earlier four-node Published control, which bypassed Code.

## Interpretation and limits

The result supports promotion to the project's current main development workflow:
it resolved the demonstrated missing-source recognition failure and the tested
TOR cross-page completeness failure without another retriever or model call. The
Code node's measured latency was small in this run.

The result does not establish repeatability, formal-suite accuracy, citation
quality across the corpus, conversation-memory behavior, provider stability,
production readiness, or tenant isolation. The source-prefix and chunk changes
were both present in the final state, so this comparison cannot attribute every
improvement to only one change. A later formal evaluation requires explicit owner
authorization and a frozen workflow, corpus state, suite and rubric.
