# AW5-RAG — Self-hosted Main Workflow, 2026-09-06

## Provenance and status

- The owner supplied `AW5-RAG Test-2.yml` after publishing the tested workflow
  and promoted it to the current main workflow on **2026-09-06**.
- Original local path: `/Users/digital/Downloads/AW5-RAG Test-2.yml`.
- Repository snapshot:
  [aw5-rag-self-hosted-main-2026-09-06.yml](aw5-rag-self-hosted-main-2026-09-06.yml).
- SHA-256: `8ad21cbfbebc7fd87f0f6ac193098623db0bb43acf994745b74716ca77668cea`.
- System/user prompt SHA-256:
  `2187f3880ade614df328ae7f2969a009cae00ea636111e049a793acf0c6895ca`.
- Code SHA-256:
  `15d41ddaec2ddcd6e0f624fe33f1b0e5465c69981a89289a34a764fce73b024c`.
- The repository copy is byte-identical to the supplied file. Its application
  label remains `AW5-RAG Test`; promotion changes its project status, not the
  preserved DSL contents.
- Mode: `advanced-chat`; DSL version: `0.7.0`.
- Verified local application ID: `f21f9d51-dbf4-43f0-b2ad-2c78dd18540e`;
  self-hosted Dify version: `1.17.0`.

**Status: owner-confirmed current main workflow; Published state and the five-node
runtime path were verified on 2026-09-06.** The recorded five-case run is a
targeted exploratory diagnostic, not a formal evaluation or evidence of tenant
isolation, production readiness, or repeatability.

## Inspected graph and configuration

```text
User Input -> Knowledge Retrieval -> Code -> LLM -> Answer
```

- 5 nodes, 4 edges and one answer-model call.
- One Knowledge Retrieval node searches the three current Knowledge Bases.
- The deterministic Code node reads the retrieval `array[object]`, prefixes each
  item's `content` with its `metadata.document_name` and
  `metadata.dataset_name`, and retains the other object fields and result order.
- The LLM Context is `Code.result`; the system prompt includes `{{#context#}}`.
- Answer returns the LLM output.

| Configuration | Current snapshot |
| --- | --- |
| Answer model | `gemini-3.5-flash` via `langgenius/gemini/google` |
| Maximum output | 6,601 tokens |
| Thinking level | `Minimal` |
| Conversation memory | Enabled, window size 10 |
| Retrieval mode | Multiple-dataset weighted semantic/keyword search |
| Retrieval weights | Semantic/vector `0.7`; keyword `0.3` |
| Top K | 10 |
| Reranking | Disabled |
| Score threshold | `null` / disabled |
| Metadata filtering | Disabled |
| Embedding | `gemini-embedding-2` via `digi1450/gemini_embedding_2_aw5/gemini_embedding_2_aw5` |

The prompt is generic and evidence-grounded. It requires source-specific
attribution, careful handling of named documents, separate treatment of differing
field lists, and explicit limits when retrieved evidence is insufficient. It does
not contain source-specific answers, test cases, a TOR/SDS/ER router, or hard-coded
document gates.

## Runtime evidence

The owner-authorized Published Service API retest used five fresh conversations,
a 20-second cutoff per attempt, and at most one retry. All five cases completed on
their first attempt:

- four passed the bounded manual rubric;
- one was partial because `เหมือนกันทุกประการ` overstated exact identity while
  the two documents supported the same four indicator categories with differing
  wording and section references;
- zero failed and zero timed out;
- wall time was 3.614–5.610 seconds, median 4.207 seconds;
- the Code node took 0.030–0.048 seconds;
- answer-model usage was 21,634 tokens and USD 0.048096 in total; embedding cost
  was not included.

Read-only runtime inspection confirmed Published workflow ID
`6e57ac51-4428-42eb-8410-edecfccda87e`, the five-node path, and source prefixes in
every rendered LLM prompt. See the
[sanitized diagnostic report](../../docs/research/self-hosted-source-prefix-diagnostic-2026-09-06.md).

## Knowledge-state dependency

Before the final retest, the owner repaired a TOR parent-chunk boundary: section
4.7.5 items (6)–(9), originally isolated at the start of the following page
parent, were moved into the parent containing the section heading and items
(1)–(5). Child chunks were regenerated. This made the retrieved parent contain
all nine items in the demonstrated case.

This Knowledge Base edit is Dify runtime state and is not embedded in the DSL.
The local evidence package retains the segment identifiers and measured
before/after state; the private chunk text remains excluded from Git.

## Limits and open boundaries

- The five-case diagnostic is too small and has no repeated trials; it does not
  establish general correctness or reliability.
- Historical `19/19` and `16/19` scores belong to older source-routing workflows
  and must not be attributed to this workflow.
- The source-prefix Code and TOR chunk repair changed together across the broader
  diagnostic interval, so the final five-case result does not isolate every
  causal contribution.
- Trusted backend enforcement of the AW5 project `tenant_id` remains
  unimplemented/unverified. Metadata filtering is disabled and `ISO-01` remains
  N/A.
- Knowledge Base chunks, vector indexes, private corpus, credentials and raw
  traces remain local-only and cannot be reconstructed from this export.

## Preservation and security checks

- Static YAML parsing confirmed the graph, settings, prompt wiring and Code.
- Source/copy SHA-256 equality was verified.
- A bounded scan found no common API-key, bearer-token, password, private-key or
  credential patterns. Matches for `max_output_tokens` are configuration fields.
- Dataset references are retained as opaque Dify export values and are not
  treated as credentials.
