# AW5 V9.1 Formal Evaluation Protocol

Status: research-methodology specification. No benchmark run is authorized by
this document. V9.1 remains frozen and unchanged.

## 1. Scope and research questions

The study evaluates evidence handling after one authorized-corpus retrieval
step. It does not evaluate unrelated RAG features or claim production readiness.

- **RQ1 — Facet selection:** Does facet-level evidence selection improve factual
  correctness and required-facet completeness over direct RAG?
- **RQ2 — Deterministic validation:** Does exact-quote validation improve
  groundedness, source correctness, citation correctness and no-answer behavior,
  and what valid evidence does it reject?
- **RQ3 — Final writer necessity:** Given the same validated evidence ledger,
  does a second LLM improve the answer enough to justify its risks and cost over
  deterministic rendering?
- **RQ4 — Efficiency tradeoff:** What paired quality, latency, token and reported
  cost differences exist among one- and two-LLM paths?
- **RQ5 — Capability robustness:** How do results vary across factual, list,
  multi-facet, schema, multi-document, restricted-source, comparison,
  duplicate/conflict, answerability and language conditions?
- **RQ6 — Conversation:** How much does an unresolved follow-up reduce retrieval
  and answer quality relative to an equivalent standalone question, and can
  history introduce unsupported claims?
- **RQ7 — Layer attribution:** For each failure, can it be localized to
  retrieval, selection, validation, generation, conversation or runtime rather
  than assigned only to the final answer?

RQ7 is included because architecture decisions require knowing which layer
failed; it does not add a new architecture feature.

## 2. Compared variants

| Variant | Conceptual path | Isolated contribution |
| --- | --- | --- |
| A — Direct RAG | Retrieval -> provenance packaging -> grounded Answer LLM | Control without facet selection or exact validation |
| B — Selector | Retrieval -> facet Evidence Selector LLM -> Answer generation | Contribution of decomposition and evidence selection |
| C — Validated one-LLM | Retrieval -> Selector LLM -> deterministic validator -> deterministic renderer | Whether validated evidence is sufficient without a writer LLM |
| D — Full V9.1 | Retrieval -> Selector LLM -> deterministic validator -> Final Writer LLM | Incremental value and risk of natural generation |

These are specifications, not implemented variants. The first downstream
ablation must replay the **same ordered retrieval result** for A–D. Record its
query, Top K, rank, score, source identity, chunk identity and content hash. Do
not rerun retrieval separately per variant for this comparison. A separate live
end-to-end experiment may later measure operational behavior.

For the cleanest C-versus-D test, replay the same validated ledger into both
renderers. This removes selector and validator randomness from the question of
whether the Final Writer is useful.

Fair-comparison controls:

- use the same question text, corpus version and ordered retrieval package for
  all variants;
- use the same selector model, parameters and prompt wherever a selector exists;
- use the same answer model, parameters, output limit and equivalent answer
  contract wherever a writer exists;
- use fixed, versioned interface adapters only to convert each variant's context
  into the expected input shape; adapters may not filter, rank or add facts;
- use the same timeout, retry, conversation and logging protocol;
- randomize execution order within blocks to reduce time/provider drift;
- hash every variant and adapter and verify that only the intended component
  differs before accepting a run.

The downstream replay experiment estimates component contribution under fixed
retrieval. A later randomized live end-to-end block is required before making
claims about total latency or provider reliability.

For the D − B contrast, B and D must use the same Final Writer model, model
parameters, output limit and answer contract wherever their input shapes permit.
The adapter between selector representation and writer input must be frozen,
versioned and deterministic. It may rename fields, preserve ordering and
serialize representation; it may not rank, select, reject, summarize,
deduplicate, add facts or perform any other evidence reasoning. D − B therefore
estimates the combined effect of deterministic validation and the fail-closed
evidence boundary, not quote matching alone.

## 3. Dataset design

Every item must have a methodological purpose and independently reviewed gold
labels. Categories may overlap as secondary tags, but each single-turn item has
one primary stratum for balanced sampling.

| Primary stratum | Capability and likely failure | Primary metric | Pass condition |
| --- | --- | --- | --- |
| Simple single fact | Finds and states one supported fact; reveals basic miss or hallucination | Fact correctness | Required fact correct, no contradictory/unsupported material claim |
| Complete list | Recovers every required member; reveals plausible partial lists | Fact/facet completeness | All required members present and no unsupported member |
| Multi-facet | Preserves independent requests; reveals dropped facets | Facet completeness | Every supported required facet answered; unsupported facets explicitly limited |
| Schema / ER | Preserves literal identifiers, types, constraints and explicit relationships | Schema literal accuracy | Exact required literals; no inferred meaning or relationship |
| Multi-document trace | Joins requirement, design and/or schema evidence without source substitution | Source recall and synthesis | Every required document facet supported and correctly attributed |
| Explicit source restriction | Obeys an exclusive named-source boundary | Restriction compliance | Uses only allowed source; refuses facts available only elsewhere |
| Cross-document comparison | Compares like dimensions and retains disagreement | Comparison correctness | Both sides present, aligned and attributed; no silent merge |
| Duplicate information | Consolidates compatible evidence without repetitive answers or inflated confidence | Deduplication and groundedness | One complete claim/list with all necessary support; no repeated source-by-source prose |
| Conflicting sources | Preserves incompatible claims and provenance | Conflict handling and attribution | Both claims remain separate and attributed; no silent winner or merge |
| Evidence boundary / no answer | Rejects insufficient or unrelated evidence | No-answer accuracy | Behavior matches zero/some/all-supported-facet policy below |

Secondary tags ensure coverage of Thai, English, mixed Thai-English, ambiguous,
answerable, unanswerable, irrelevant, typo/OCR-sensitive, duplicate,
conflicting, prompt-injection and hostile-document-content conditions. Ambiguous
items must have a predeclared acceptable clarification or bounded interpretation;
they cannot be scored against an unstated preferred interpretation.

Secondary-condition scoring is also explicit:

| Secondary condition | Capability/failure exposed | Primary metric | Pass condition |
| --- | --- | --- | --- |
| Thai | Handles the corpus's primary user language | Strict answer score | Correct evidence-grounded Thai answer |
| English | Cross-language retrieval/answering | Facet recall and strict answer score | Same required facts/facets, answered in English |
| Mixed Thai-English | Preserves identifiers and code-switched intent | Literal and facet accuracy | No translated/corrupted identifier or dropped language-dependent facet |
| Ambiguous | Avoids confident unsupported interpretation | Clarification/limitation accuracy | Uses a gold-approved bounded interpretation or asks for the labeled clarification |
| User prompt injection | Treats hostile user instructions as untrusted | Groundedness and source compliance | Does not fabricate, bypass evidence or suppress required provenance |
| Hostile document content | Treats instructions inside evidence as content | Groundedness and instruction resistance | Uses factual evidence only and does not execute embedded instructions |
| Conversational follow-up | Resolves referents without treating history as evidence | Context-resolution accuracy | Matches standalone gold and introduces no unsupported history claim |

Hostile-document-content cases require a separately approved synthetic fixture.
Until one exists, keep those rows as `planned` placeholders. Do not insert hostile
text into the private primary corpus merely to complete the benchmark.

## 4. Recommended sizes

Counts below refer to single-turn items. Conversation sequences and validator
mutations are separate because they have different units of analysis.

| Primary stratum | Development (36) | Senior final (72) | Publication target (120) |
| --- | ---: | ---: | ---: |
| Simple single fact | 5 | 10 | 16 |
| Complete list | 4 | 8 | 14 |
| Multi-facet | 4 | 8 | 14 |
| Schema / ER | 5 | 10 | 16 |
| Multi-document trace | 5 | 10 | 16 |
| Explicit source restriction | 4 | 8 | 12 |
| Cross-document comparison | 3 | 6 | 10 |
| Duplicate information | 2 | 3 | 5 |
| Conflicting sources | 1 | 3 | 5 |
| Evidence boundary / no answer | 3 | 6 | 12 |

Orthogonal targets:

| Condition | Development | Senior final | Publication target |
| --- | ---: | ---: | ---: |
| Answerable / unanswerable | 27 / 9 | 54 / 18 | 84 / 36 |
| Thai / English / mixed | 24 / 6 / 6 | 50 / 12 / 10 | 72 / 24 / 24 |
| Conversational sequences, ideally 3 turns each | 4 | 8 | 16 |
| Validator cases: transformed positives + negative controls | 30 | 50 | 80 |

The 36-item set is for fast iteration and cannot support broad claims. The
72-item held-out set is the recommended minimum final senior-project benchmark:
it supports meaningful paired comparisons while remaining affordable. The
120-item target provides better subgroup coverage, but is publication-oriented
only if gold labels, blinding and repetitions are adequately resourced. More
weakly labeled questions are less useful than fewer independently verified ones.

Legacy questions already used for tuning remain a named **development
regression set**. A new, independently reviewed split must be frozen as the
confirmatory held-out set. Never move an item from development to held-out after
observing model output.

### Development/held-out firewall

Development 36 is the only set used while implementing or debugging A/B/C/D,
adapters, deterministic rendering, evaluators, logging, score calculations and
practical decision margins. Pilot model outputs and margin setting use
Development 36 only.

Humans may author and verify held-out labels, but no A/B/C/D model output may be
generated or inspected for Held-out 72 until all variants, prompts, adapters,
renderer behavior, rubric, margins, execution tooling and analysis code are
frozen and hashed. All predeclared repetitions must be collected as one locked
batch before result inspection.

The Held-out 72 run is confirmatory. After it is opened, its failures may
motivate future versions, but it becomes an observed test set. A tuned successor
may report regression results on it but cannot claim them as a new independent
confirmatory result. A fresh untouched set or another predeclared external
validation design is required for a new confirmatory claim.

### Pre-freeze cross-stratification audit

Before freezing Held-out 72, publish count tables for:

- `primary_category × answerability`;
- `primary_category × language`;
- `difficulty × language`;
- `difficulty × answerability`.

Also list secondary tags by language and answerability. This is a coverage audit,
not a fully balanced Cartesian matrix. Flag and repair serious confounding when
feasible: unanswerable items should span source-restriction, multi-facet, schema
and multi-document strata; English and mixed-language items must not be confined
to simple facts; and no language group should contain only one difficulty level.
Document unavoidable sparse cells before freezing.

## 5. No-answer policy

Gold labels must distinguish three states:

| Supported facets | Expected behavior |
| --- | --- |
| Zero | Full deterministic refusal/insufficient-evidence response; no factual answer |
| Some | Answer only supported facets and explicitly identify each unsupported facet; no inference from similar passages |
| All | Normal grounded answer |

The no-answer subset must include: unrelated questions; an in-domain topic whose
requested fact is absent; semantically similar but insufficient passages;
exclusive-source questions whose answer exists only outside the allowed source;
and partially answerable multi-facet questions.

V9.1's current whole-answer branch is measured as-is. If it fully refuses a
partially answerable item, score the supported-facet loss rather than changing
the workflow during the benchmark.

## 6. Conflicting-source fixtures

Each conflict item must identify two independently verified evidence passages,
the exact incompatible claim dimension, and the expected response:

1. state both claims;
2. attribute each claim to its actual source;
3. avoid selecting a winner unless precedence is part of the gold evidence;
4. avoid combining incompatible values into one statement.

Use naturally occurring verified conflicts when available. Otherwise use a
clearly labeled, isolated synthetic fixture approved for evaluation. A missing
field in one retrieved excerpt is not automatically a conflict.

## 7. Retrieval evaluation

Annotators label **evidence groups**, not every duplicate chunk. One evidence
group represents a fact/facet and may contain multiple acceptable passage IDs.
Passages receive relevance `0` (irrelevant), `1` (useful context) or `2`
(directly sufficient). A lightweight pool is formed from the union of top results
from all compared retrieval settings plus human-located gold passages. Only that
pool requires judgment initially; unresolved items are marked `incomplete_qrels`.

For question `q` and ordered top `K`:

- **Evidence-group Recall@K** = covered required evidence groups / all required
  evidence groups. A group is covered when any acceptable passage is retrieved.
- **Judged Precision@K** = passages with relevance > 0 / K. Also report graded
  relevance `sum(relevance)/(2K)`.
- **Facet Recall@K** = required answerable facets with at least one directly
  sufficient retrieved passage / all required answerable facets.
- **Source Recall@K** = required source documents represented by directly
  sufficient evidence / all required source documents.

Report macro averages across questions and results by category. If three facets
exist and evidence for two is retrieved, Facet Recall is `2/3` even if the final
answer sounds complete. Unanswerable items do not receive ordinary recall; score
their retrieved noise and no-answer behavior instead.

## 8. Conversation benchmark

Every normal single-turn item runs in a fresh conversation. Conversation cases
are separate sequences with a fixed turn order and one shared conversation ID.
For each sequence, create:

- the natural follow-up form containing pronouns or omitted subjects;
- an equivalent standalone form with the referent made explicit;
- per-turn gold facets and evidence groups;
- prohibited carry-over claims from previous model answers.

Measure raw follow-up versus standalone Retrieval Facet Recall@K, answer
correctness, context-resolution accuracy, unsupported-history leakage and
latency. Retrieval currently receives only the current `sys.query`; this
experiment measures that behavior and does not assume query rewriting.

## 9. Validator mutation benchmark

Normative validity is assigned independently from the current validator. Each
case records human-verified `semantic_equivalence`, `source_binding_correct`,
`gold_validity` and `gold_should_accept`. Runtime output records
`observed_validator_decision` separately. A formatting-equivalent quote may have
`gold_should_accept=true` and an observed rejection, which counts as a false
rejection. Current implementation behavior never defines gold truth.

The initial diagnostic should use three verified base quotes spanning Thai
prose, English/schema text and table/PDF extraction. Apply eight transformations
to each: ordinary whitespace, line breaks, PDF hyphenation, Unicode normalization,
zero-width characters, Thai combining-mark representation, curly/straight
punctuation and table-format changes. Add six meaning-changing or wrong-source
negative controls: 30 cases total.

For the senior final set, use five bases × eight transformations plus ten
negative controls (50). Publication target: eight bases × eight transformations
plus sixteen controls (80). Gold labels state semantic equivalence, source
binding and normative acceptance independently of observed validator behavior.
This measures current behavior; it does not authorize normalization changes.

## 10. Reliability, token and cost accounting

Record every attempt, including stalls. Use a 20-second per-attempt cutoff and at
most one fresh-conversation retry for an operational timeout. Never retry a
completed semantic failure to obtain a pass. Report:

- first-attempt success, timeout and retry rates;
- successful-run and retry-inclusive p50/p95/end-to-end latency;
- per-node latency and provider/error code when available;
- selected answer latency separately from total user waiting time;
- retrieval count;
- selector input/output tokens;
- Final Writer input/output tokens;
- total Dify-reported workflow tokens and price;
- cost per completed answer and cost per original query including retries.

Dify totals may omit embedding, retrieval-provider or plugin costs. Label them
`reported cost`, never complete monetary cost, unless provider invoices reconcile
all components.

## 11. Frozen run protocol

Before a formal run, record and freeze:

1. suite version/hash, split and rubric version;
2. workflow export hash, normalized graph hash and Draft/Published identity;
3. prompt hashes and all model names/parameters;
4. Dify and plugin versions;
5. Knowledge Base IDs, document checksums, chunk configuration and index/corpus
   version;
6. retrieval mode, Top K, weights, thresholds, reranker and metadata settings;
7. timeout, retry and repetition policy;
8. exact logging fields and redaction boundary.

Use one fresh conversation per single-turn question. Preserve raw outputs,
ordered retrieval results, selected ledger, validator decisions, final answer,
citations, node timings, token/cost fields and all failed attempts in a local-only
atomic evidence package. Do not modify a workflow, corpus, prompt, model or
scoring rule during a run.

For the senior final evaluation, collect all predeclared held-out attempts before
inspecting any answer: one attempt for all 72 items per variant plus three
attempts for a preregistered balanced 24-item repeatability panel. Deterministic
rendering need not be repeated when its input ledger is byte-identical. For
publication-quality claims, three independent attempts per item are preferred;
if unaffordable, report the reduced repetition scope and do not make broad
reliability claims.

## 12. Human, deterministic and optional LLM judging

- Deterministic scoring: exact IDs/literals, expected-fact membership, required
  facets, source IDs, quote substring/source binding, branch/no-answer behavior,
  retrieval metrics, timing, tokens and cost.
- Human scoring: semantic equivalence of paraphrases, conflict synthesis,
  ambiguous-question handling and naturalness. Use two reviewers for held-out
  items where possible and adjudicate disagreements before unblinding variants.
- Optional LLM judge: exploratory naturalness or semantic triage only. Calibrate
  against a human-scored sample; do not use it as the sole correctness judge.

Randomize answer order, hide variant names, remove latency/cost fields from
quality reviewers and use the same rubric. The evaluator must not know which
answer contains the architecture favored by the researcher.

## 13. Statistical reporting

Report counts, percentages and 95% confidence intervals for binary outcomes;
mean plus median for quality/cost; and p50/p95 for latency. Compare variants on
the same items using paired differences. Bootstrap paired confidence intervals
are sufficient for most continuous scores. McNemar's test is appropriate for a
predeclared binary pass comparison; Wilcoxon signed-rank may be used for paired
ordinal ratings. Report effect sizes and confidence intervals even when a
significance test is used. Treat subgroup results with small denominators as
descriptive, and do not search many categories for a favorable p-value.

## 14. Methodological risks

- Legacy items are tuning-contaminated and cannot establish generalization.
- Gold evidence may be incomplete when PDFs, figures or tables extract poorly.
- Cloud model/provider drift can change repeated results despite frozen prompts.
- Retrieval replay improves causal comparison but does not represent full live
  latency or reliability; report replay and end-to-end experiments separately.
- Human source interpretation may disagree; preserve adjudication notes.
- The current corpus does not prove tenant isolation, and no score transfers to
  an unimplemented Project B fixture.
- Reported Dify tokens/cost can be incomplete.

## 15. External-validity boundary

Results support claims only for the evaluated Nature Footprint organizational
project corpus, its documented languages and question strata, the frozen AW5
configurations and the measured environment. They do not establish general
superiority over RAG systems, models, corpora, organizations or document domains
that were not evaluated. Broader claims require replication on independent
corpora and deployment settings.
