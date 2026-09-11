# AW5 Evaluation Error Taxonomy

Assign every observed error to the earliest demonstrated failing layer. Multiple
codes are allowed when later layers add independent errors. Record evidence for
the code; do not infer a root cause from the final answer alone.

| Code | Layer | Definition | Required evidence |
| --- | --- | --- | --- |
| R1 | Retrieval | No directly sufficient passage for a required answerable facet appears in Top K | Gold evidence group and ordered retrieval output |
| R2 | Retrieval | Irrelevant/noisy passages crowd the result or a wrong passage is ranked as useful | Judged qrels and ranks/scores |
| R3 | Retrieval/source | Required source is absent although gold requires it | Required source labels and Top-K provenance |
| R4 | Retrieval | Duplicate chunks consume material Top-K capacity | Stable chunk/content hashes and ranks |
| S1 | Selector | Sufficient evidence was retrieved but omitted by selector | Top-K evidence plus selector output |
| S2 | Selector | Selector chose evidence that does not support its facet | Facet label, selected quote and human entailment judgment |
| S3 | Selector | Selector covers only part of the required facets | Per-facet gold and selector coverage |
| S4 | Selector/source | Quote is assigned to the wrong source before validation | Retrieved provenance and selector source binding |
| V1 | Validator | Valid exact/allowed evidence is rejected | Proposed quote, source content and validator decision |
| V2 | Validator | Unsupported or altered quote is accepted | Accepted quote and source content comparison |
| V3 | Validator | Quote is accepted under the wrong source | Accepted binding versus retrieved provenance |
| V4 | Validator | Validation removes all evidence for a facet that had valid selector evidence | Before/after facet ledger |
| G1 | Generation | Final answer adds a claim unsupported by validated evidence | Accepted ledger and claim-level answer audit |
| G2 | Generation | Final answer omits a supported required fact/facet | Gold labels, accepted ledger and answer |
| G3 | Generation | Final answer synthesizes supported pieces incorrectly | Evidence and claim decomposition |
| G4 | Generation | Final answer attributes a claim to the wrong source | Claim-citation/source mapping |
| G5 | Generation | Final answer alters a schema literal or invents schema meaning/relationship | Literal gold and answer |
| N1 | Evidence boundary | Answers when zero facets are supported | Answerability label, validated count and output |
| N2 | Evidence boundary | Refuses when all required facets are supported | Gold/validated evidence and output |
| N3 | Evidence boundary | Mishandles partial answerability: guesses unsupported facets or loses supported ones | Per-facet support state and output |
| C1 | Conversation | Follow-up referent is resolved incorrectly or not resolved | Conversation sequence and standalone pair |
| C2 | Conversation | Prior assistant claim is reused as evidence without document support | History, retrieved/validated evidence and answer |
| C3 | Conversation | Information from another benchmark conversation contaminates an item | Conversation IDs and run logs |
| X1 | Runtime | Timeout, provider error, stalled node or workflow failure | Attempt trace and timing/error code |
| X2 | Runtime | Retry creates an orphan/concurrent task or duplicate charge | Stop/retry IDs and provider/Dify trace |
| M1 | Measurement | Required trace, token, cost, source or timing field is missing | Evidence-package audit |
| A1 | Annotation | Gold label is ambiguous, incomplete or contradicted by verified source evidence | Reviewer disagreement and source inspection |

## Assignment rules

1. Inspect retrieval before assigning selector/validator/generation codes.
2. Use R1 when evidence is absent from Top K; use S1 only when it is present but
   not selected.
3. Use V1 only when the selector proposed valid evidence and the validator
   rejected it.
4. Use G codes only when sufficient accepted evidence reached the renderer/writer.
5. Use N codes for the system's answer/refusal decision; pair them with the
   upstream cause when known.
6. Use X1 independently of semantic scoring. A successful retry does not erase
   the first X1 attempt.
7. Use A1 instead of forcing an architecture error when gold is not defensible.

Each result record should contain `primary_error_code`, `secondary_error_codes`,
`evidence_pointer`, `reviewer`, `adjudication_status` and a short causal note.
