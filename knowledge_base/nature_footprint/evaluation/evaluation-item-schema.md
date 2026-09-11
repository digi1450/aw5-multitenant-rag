# Evaluation Item Schema

This schema defines one benchmark item. The CSV is an authoring view; nested
labels are JSON text and should later be converted to a versioned JSON dataset
for execution. `gold_verified` requires direct verification against every
legitimate source needed by the item and completion of the declared human-review
procedure. One legitimate source is sufficient for a naturally single-source
question; this status never requires two independent documents merely to have
two sources. For Held-out 72, an evidence verifier establishes the source labels
and a second human reviewer checks the item; disagreements are adjudicated
before freezing.

## Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | string | Dataset schema version, for example `1.0` |
| `question_id` | string | Stable unique ID; never reuse after publication |
| `split` | enum | `development`, `held_out`, `conversation`, `validator_mutation` |
| `status` | enum | `placeholder`, `draft`, `gold_verified`, `retired` |
| `primary_category` | enum | One sampling stratum from the protocol |
| `secondary_tags` | JSON array | Orthogonal capabilities/failure modes |
| `language` | enum | `th`, `en`, `th_en`, or documented alternative |
| `difficulty` | enum | `simple`, `moderate`, or `complex`, assigned before model output |
| `question` | string | Exact user-visible input |
| `answerability` | enum | `all`, `partial`, `none` |
| `expected_behavior` | enum | `answer`, `partial_with_limitations`, `refuse` |
| `required_facets` | JSON array | Independently scored facet objects |
| `expected_facts` | JSON array | Atomic fact objects, each linked to facets/evidence |
| `expected_sources` | JSON array | Stable source IDs and whether each is required/allowed |
| `expected_evidence_groups` | JSON array | Acceptable passage alternatives for facts/facets |
| `forbidden_claims` | JSON array | Specific unsupported or contradictory claims |
| `gold_version` | string | Version/hash of the adjudicated label set |
| `corpus_version` | string | Frozen manifest/index identifier used to establish gold |
| `adjudication_status` | enum | `unreviewed`, `single_review`, `adjudicated` |
| `evidence_verifier_id` | string | Human who verified gold against legitimate source evidence |
| `second_reviewer_id` | string or null | Independent reviewer; required for held-out confirmation |

## Conditional fields

| Field | Type | Required when |
| --- | --- | --- |
| `source_restriction` | JSON object or null | Question limits evidence to named source(s) |
| `comparison_requirement` | JSON object or null | Question compares sources, values or versions |
| `conversation_group_id` | string or null | Item belongs to a multi-turn sequence |
| `turn_index` | integer or null | Conversation item; starts at 1 |
| `conversation_context` | JSON array or null | Exact preceding user/assistant turns supplied at run time |
| `standalone_pair_id` | string or null | Follow-up has an equivalent explicit standalone item |
| `ambiguity_notes` | string or null | More than one reasonable interpretation exists |
| `injection_type` | enum or null | `user`, `document`, or `none` |
| `mutation_spec` | JSON object or null | Validator mutation case |
| `scoring_weights` | JSON object | Non-default facet/fact weights, justified before testing |
| `notes` | string | Provenance, unresolved label issue or retirement reason |

## Nested objects

### Required facet

```json
{
  "facet_id": "F1",
  "description": "PLACEHOLDER: independently verifiable request",
  "answerability": "supported",
  "weight": 1.0,
  "required_fact_ids": ["FACT1"],
  "required_evidence_group_ids": ["EG1"],
  "unsupported_behavior": null
}
```

`answerability` is `supported` or `unsupported`. For a partially answerable
question, unsupported facets must set `unsupported_behavior` to
`state_limitation_without_guessing`.

### Expected fact

```json
{
  "fact_id": "FACT1",
  "facet_id": "F1",
  "canonical_value": "PLACEHOLDER_VERIFY_FROM_SOURCE",
  "acceptable_variants": [],
  "value_type": "string",
  "weight": 1.0,
  "required": true
}
```

Lists use one fact per required member plus an optional ordered-list rule. This
makes partial completeness measurable. Do not store an entire list as one
unscorable prose string.

### Expected source

```json
{
  "source_id": "manifest-document-id",
  "display_name": "PLACEHOLDER",
  "role": "required",
  "source_version": "sha256-or-version"
}
```

`role` is `required`, `allowed`, or `forbidden`. Display names are labels;
execution and scoring use stable source IDs.

### Evidence group

```json
{
  "evidence_group_id": "EG1",
  "facet_ids": ["F1"],
  "fact_ids": ["FACT1"],
  "minimum_relevance": 2,
  "acceptable_passages": [
    {
      "source_id": "manifest-document-id",
      "passage_id": "stable-chunk-or-manual-span-id",
      "page_or_section": "PLACEHOLDER_OR_NULL",
      "exact_quote": "PLACEHOLDER_VERBATIM_QUOTE",
      "quote_sha256": "PLACEHOLDER",
      "annotation_method": "human_verified"
    }
  ]
}
```

Alternative passages that independently support the same fact belong to one
group. A retrieved duplicate therefore does not inflate recall.

### Source restriction

```json
{
  "mode": "exclusive",
  "allowed_source_ids": ["source-a"],
  "forbidden_source_ids": ["source-b"],
  "if_answer_only_elsewhere": "refuse"
}
```

### Comparison requirement

```json
{
  "dimensions": ["PLACEHOLDER_DIMENSION"],
  "left_source_ids": ["source-a"],
  "right_source_ids": ["source-b"],
  "expected_relation": "same|different|conflict|undetermined",
  "must_attribute_each_side": true,
  "precedence_rule": null
}
```

### Mutation specification

```json
{
  "base_quote_id": "BQ1",
  "transformation": "unicode_normalization",
  "semantic_equivalence": true,
  "source_binding_correct": true,
  "gold_validity": "valid",
  "gold_should_accept": true,
  "negative_control": false
}
```

`gold_validity` is `valid` or `invalid` and is assigned from the verified base
quote, semantic equivalence and source binding. It never describes expected
current implementation behavior. Store the execution result separately:

```json
{
  "question_id": "MUTATION_CASE_ID",
  "attempt_id": "RUN_ATTEMPT_ID",
  "observed_validator_decision": "accept",
  "observed_reason": "OPTIONAL_RUNTIME_DETAIL"
}
```

## Gold-label workflow

1. Draft question for a declared category and failure mode.
2. Locate direct evidence manually; do not use model output as ground truth.
3. Split the expected answer into atomic facets and facts.
4. Record acceptable passage alternatives and stable source identity.
5. Add forbidden claims and source/comparison rules.
6. For held-out items, a second human reviewer checks question clarity, evidence
   sufficiency and labels. A single-source item still uses its one legitimate
   source; the second review is a person-level check, not a second-document rule.
7. Resolve disagreements and record adjudication.
8. Freeze dataset and corpus hashes before any held-out run.

If evidence cannot be verified, retain `placeholder` or retire the item. Do not
invent a gold answer to fill a required field.
