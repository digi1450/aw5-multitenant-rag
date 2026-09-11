# AW5 Evaluation Scoring Rubric

Status: pre-run scoring specification. Apply the same frozen rubric to every
variant. Do not change labels after seeing which variant produced an answer.

## 1. Units of scoring

- **Fact:** smallest independently true/false gold statement or list member.
- **Facet:** independently requested part of the question.
- **Claim:** smallest factual assertion in the produced answer.
- **Evidence group:** one or more alternative passages sufficient for a labeled
  fact/facet.
- **Attempt:** one workflow execution, including a timeout or error.
- **Query outcome:** all attempts generated from one benchmark question under the
  predeclared retry policy.

All fractions use gold weights when declared; otherwise each unit has weight 1.
Report per-item values and macro averages so long lists do not dominate the set.

## 2. Retrieval metrics

| Metric | Formula | Scale |
| --- | --- | --- |
| Evidence Recall@K | covered required evidence groups / required evidence groups | 0–1 |
| Precision@K | retrieved passages judged relevance > 0 / K | 0–1 |
| Graded relevance@K | sum of relevance labels / `2K` | 0–1 |
| Facet Recall@K | answerable required facets with sufficient evidence in Top K / answerable required facets | 0–1 |
| Source Recall@K | required sources with sufficient retrieved evidence / required sources | 0–1 |

Deduplicate identical passage/chunk IDs before scoring. For `answerability=none`,
report irrelevant-passage rate and do not fabricate a recall denominator.

## 3. Answer metrics

### Factual correctness

`correct material answer claims / all material answer claims`. Map each claim to
an expected fact, contradiction or unsupported claim; contradictions and
unsupported additions remain in the denominator and score incorrect. Score 1
only when every asserted material claim is correct. Report both the 0–1 fraction
and strict binary correctness. Omitting a fact affects completeness rather than
claim correctness.

### Completeness

- **Fact completeness** = covered required fact weight / total required fact
  weight.
- **Facet completeness** = supported required facet weight satisfactorily
  answered / total supported required facet weight.

A facet is satisfactorily answered only when all facts marked `required` for it
are present. For partial-answer items, an unsupported facet receives credit only
when the answer explicitly states the limitation without guessing.

### Groundedness / faithfulness

`answer claims directly entailed by allowed retrieved/validated evidence / all
answer claims`. Score 0–1 and report unsupported claim count. Formatting,
conversational transitions and clearly marked limitations are not factual claims.
Any fabricated identifier, value, relationship, source statement or absolute
permission claim is unsupported.

If the answer contains no factual claims, groundedness is **N/A**, not 1. A
refusal cannot earn perfect groundedness through an empty denominator; evaluate
it using no-answer accuracy, supported-facet completeness and over-refusal.

### Citation and source correctness

Report separately:

- **Citation precision** = cited claim-source links directly supporting the claim
  / all cited claim-source links.
- **Citation coverage** = supported answer claims with at least one correct
  citation / supported answer claims requiring citation.
- **Source attribution accuracy** = claims attributed to the correct source /
  attributed claims.

Displaying a source anywhere in the answer does not support every claim.

### Zero-denominator policy

Never convert an undefined fraction into a perfect score.

| Metric condition | Recorded value | Companion metric that evaluates behavior |
| --- | --- | --- |
| No material factual claims | Correctness and groundedness `N/A` | No-answer accuracy, completeness, over-refusal |
| No citations emitted | Citation precision `N/A` | Citation coverage is 0 when citations were required; otherwise `N/A` |
| No attributed claims | Attribution accuracy `N/A` | Attribution requirement/completeness is 0 when attribution was required |
| No answerable facets or evidence groups | Retrieval Recall and Facet Recall `N/A` | Retrieved-noise rate and no-answer accuracy |
| No required sources | Source Recall `N/A` | Source-restriction compliance when applicable |
| K is zero | Precision@K and graded relevance `N/A` | Configuration error when K should be positive |
| No valid proposed quotes | Valid-quote acceptance and false-rejection rates `N/A` | False acceptance on invalid controls |
| No invalid proposed quotes | False-acceptance rate `N/A` | Valid-quote acceptance and false rejection |

Aggregates exclude `N/A` values and always report their contributing numerator
and denominator. Strict-pass logic uses applicable metrics plus expected
answer/no-answer behavior; it does not require an inapplicable metric to equal 1.

### Source-restriction compliance

Binary. Pass only if every used/cited evidence item belongs to the allowed source
set and the answer does not import a fact known only from a forbidden source. If
the allowed source lacks the fact, the correct result is the labeled limitation
or refusal.

### No-answer accuracy

Use a three-state gold label:

- `none`: 1 for full refusal without factual guessing; otherwise 0.
- `partial`: score two primary components separately: **safe partial behavior**
  (binary: no unsupported facet is asserted as fact and limitations are stated)
  and **supported-facet completeness** (0–1 using the ordinary facet formula).
- `all`: score through normal correctness/completeness; an unnecessary refusal
  is 0 for answer utility and completeness.

Also report binary **unsafe answer rate** for `none` items and **over-refusal
rate** for answerable items.

An optional `0 / 0.5 / 1` partial-answer label may summarize `unsafe / safe but
incomplete / safe and complete` in descriptive tables. It is ordinal, must not
be averaged as the primary continuous research metric, and never replaces the
two component measures above.

### Comparison correctness

Four equally weighted components unless gold specifies otherwise: left side,
right side, aligned comparison dimension, and correct relation/conclusion. Each
component is binary; total is 0–1. A silent merge of conflicting values scores 0
for relation and source attribution.

### Schema literal accuracy

`correct required schema literals / required schema literals`, where literals
include exact table/field identifiers, data types, constraints and explicitly
declared references. Any altered identifier or inferred relationship is an
error. Explanatory meaning is scored only if a retrieved source explicitly
provides it.

### Naturalness/readability

Blinded human ordinal rating:

1. unusable or incoherent;
2. difficult to understand;
3. understandable with avoidable awkwardness/repetition;
4. clear and concise;
5. exceptionally clear for the task.

Naturalness never offsets an unsupported claim or missing required facet.

## 4. Strict outcome labels

- **Pass:** correctness, groundedness, source-restriction compliance and schema
  literal accuracy (when applicable) are all 1; fact and facet completeness are
  1; no-answer behavior matches gold; no critical error.
- **Partial:** no unsupported material claim, but one or more supported facts or
  facets are safely omitted, or a correct partial limitation loses supported
  content.
- **Fail:** any unsupported/incorrect material claim, wrong-source use,
  restriction breach, incorrect no-answer, schema invention, or missing core
  answer makes the result misleading.
- **Operational failure:** no scorable completed answer due to timeout/provider/
  runtime error. Keep separate from semantic fail while including it in
  reliability and retry-inclusive cost/latency.

## 5. Validator-specific metrics

Use human-verified proposed quote labels and source bindings.

| Metric | Formula |
| --- | --- |
| Accepted valid quote rate (quote recall) | valid proposed quotes accepted / all valid proposed quotes |
| False rejection rate | valid proposed quotes rejected / all valid proposed quotes |
| False acceptance rate | invalid proposed quotes accepted / all invalid proposed quotes |
| Accepted quote precision | valid accepted quotes / all accepted quotes |
| Incorrect-source acceptance rate | accepted quotes bound to wrong source / all accepted quotes |
| Facet coverage after validation | supported required facets with ≥1 valid accepted quote / supported required facets |
| Validator-induced facet loss | facets with valid selector evidence but no accepted quote / facets with valid selector evidence |
| Validator-induced fact loss | gold facts supported by valid selector evidence but unsupported after validation / gold facts supported by valid selector evidence |

Layer diagnosis for each facet:

1. no sufficient Top-K passage -> retrieval failure;
2. sufficient Top-K passage but selector omits it -> selector miss;
3. selector proposes irrelevant evidence -> selector precision failure;
4. selector proposes valid evidence but validator rejects it -> validator false
   rejection;
5. validator accepts invalid or wrong-source evidence -> validator false
   acceptance/source failure;
6. valid accepted evidence exists but final answer fails -> renderer/generation
   failure.

## 6. One-LLM versus two-LLM decision rule

Compare C and D using identical validated ledgers. Predeclare primary safety
metrics (correctness, groundedness, unsupported claims, restriction/no-answer
compliance) and utility metrics (completeness and naturalness). Report paired
latency, token and cost differences.

Keep the Final Writer only if all conditions hold:

1. it is non-inferior on every safety metric within a predeclared practical
   margin;
2. it produces a reproducible improvement on a named utility metric;
3. that improvement exceeds the minimum practically important difference agreed
   before the confirmatory run;
4. added p95 latency and retry-inclusive reported cost remain within the
   predeclared deployment budget.

Establish margins in a small blinded pilot by asking reviewers what answer
difference would change usability, and by measuring the existing latency/cost
distribution. Freeze the resulting values before held-out testing. Do not choose
thresholds after seeing C/D results. If utility improvement is negligible, its
confidence interval includes only trivial effects, or any safety metric worsens,
prefer C's simpler deterministic renderer.

## 7. Reliability and economics

- First-attempt success = completed first attempts / original queries.
- Timeout rate = timed-out attempts / all attempts.
- Retry rate = queries with an operational retry / original queries.
- Query latency includes all failed-attempt waiting plus retry time.
- Attempt latency describes each execution separately.
- Cost per successful answer = reported total cost / completed answers.
- Cost per benchmark query = cost of every attempt, including retries / original
  queries.

Report p50 and p95 over attempts and over retry-inclusive query latency. Do not
replace a timeout with its successful retry in the reliability denominator.

## 8. Aggregate reporting

Publish each metric overall and by preregistered primary stratum, answerability
and language. Include numerator/denominator with every percentage. The primary
architecture comparison uses paired item-level differences and 95% confidence
intervals. Strict pass rate is a release gate; a weighted total score may be
shown descriptively but cannot hide a groundedness or restriction failure.
