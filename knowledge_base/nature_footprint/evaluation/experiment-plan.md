# AW5 V9.1 Experimental Plan

Status: ordered research plan only. It does not authorize implementation,
workflow changes, Dify changes or cloud inference.

## Phase 0 — Build, partition and verify benchmark

1. Create 36 development items from verified sources and known failure classes.
2. Author and human-verify a separate 72-item held-out senior-project set without
   copying answers from model runs or prompts. Seal its execution inputs from all
   model runs until the pre-confirmatory freeze.
3. Label atomic facets, facts, evidence groups, source boundaries, answerability,
   forbidden claims and conversation pairs.
4. Pool candidate passages, judge only the pooled passages, and mark incomplete
   qrels explicitly.
5. Run the pre-freeze cross-stratification audit for category × answerability,
   category × language, difficulty × language and difficulty × answerability;
   repair or document serious confounding.
6. Have a second human reviewer inspect held-out gold labels; adjudicate
   differences. One-source questions require verified evidence from that source,
   not an artificial second document.
7. Seal and hash Held-out 72 plus its gold labels. Record access, and do not send
   any held-out question to A/B/C/D during development.

Exit gate: every held-out item is `gold_verified`, answerability is explicit,
evidence passages are directly inspectable, CSV/JSON validation passes, and no
item has been used to tune V9.1.

## Phase 1 — Development-only implementation and pilot

Use **Development 36 only** to measure V9.1 diagnostically; implement and debug
A/B/C/D; build deterministic, versioned shape-only adapters; develop the
deterministic renderer and evaluation tooling; and pilot the rubric and
practical decision margins. Held-out 72 model outputs remain unopened.

Exit gate: all variants and tools operate correctly on Development 36; margins
and analysis rules are set without held-out outputs; missing telemetry is
declared.

## Phase 2 — Pre-confirmatory freeze

Freeze and hash A/B/C/D, prompts, model parameters, adapter code, deterministic
renderer, scoring code, rubric, decision margins, corpus/index, retrieval replay,
timeout/retry policy, repetition schedule and analysis plan. An adapter may only
convert representation shape; it may not rank, select, summarize, deduplicate,
add facts or reason about evidence.

Exit gate: a diff audit proves each contrast changes only its declared component,
and the complete confirmatory batch can run without code or rubric edits.

## Phase 3 — Confirmatory downstream ablation on Held-out 72

Feed A–D the same ordered frozen retrieval pool per question. Collect every
predeclared attempt and repetition before inspecting results. Use a fresh
conversation for every single-turn item.

Recommended contrasts:

- B − A estimates facet-selector contribution.
- D − B estimates deterministic validator plus fail-closed evidence-boundary
  behavior while retaining the same Final Writer model, parameters and answer
  contract wherever possible.
- D − C estimates Final Writer contribution using the same validated ledger.
- C − B changes both validation and rendering, so report it as a system-level
  comparison rather than a clean single-component causal estimate.

Run all 72 items once and the preregistered balanced 24-item panel three times as
one locked collection batch. Do not inspect the first pass before repetitions
complete.

Exit gate: paired quality, latency, tokens, reported cost and layer errors are
available for every contrast.

After unblinding, failures may inform future work, but Held-out 72 then becomes
an observed regression set. A tuned successor requires a fresh untouched set or
another predeclared external validation design for a new confirmatory claim.

## Phase 4 — Decide one versus two LLMs

Apply the predeclared C/D decision rule in `scoring-rubric.md`. Reviewers see
randomized answers without variant names. Do not retain the writer solely because
its prose looks better.

Exit gate: safety non-inferiority, practically meaningful utility difference and
deployment latency/cost limits have been evaluated with confidence intervals.

## Phase 5 — Retrieval experiments

Only after the downstream architecture is selected, compare one retrieval
variable at a time:

1. K10
2. K20
3. K30
4. K30 candidate retrieval -> reranker -> final K10

Use the same queries, corpus/index version and downstream path. Primary outcomes
are evidence-group Recall@K, Facet Recall@K, Source Recall@K, judged relevance,
end quality, latency and reported cost.

Decision evidence required:

- **Reranker:** candidate-pool recall is high, required evidence is ranked below
  the usable cutoff, and reranking improves facet/source recall or end quality
  repeatably without unacceptable latency/cost or new disclosure concerns.
- **Reduce Top K:** recall/facet/source metrics and strict quality remain within a
  predeclared non-inferiority margin while latency/tokens/cost improve.

No reranker or Top-K change is justified by answer aesthetics alone.

Develop retrieval changes on Development 36. Because Held-out 72 has already
been opened in Phase 3, it may be used only as a labeled regression set afterward;
it cannot support a fresh confirmatory retrieval claim. Freeze any selected
retrieval candidate and evaluate it on a new untouched retrieval-confirmation
set or another predeclared external validation design.

## Phase 6 — Conversational retrieval benchmark

Run fixed multi-turn sequences and paired standalone rewrites. Measure current
raw follow-up retrieval separately from generation and history leakage. Keep
normal benchmark questions isolated in fresh conversations.

Exit gate: paired follow-up versus standalone Facet Recall@K and error codes show
whether unresolved references materially harm retrieval.

## Phase 7 — Conditional query contextualization experiment

Proceed only if Phase 6 demonstrates C1 retrieval/context failures. Compare raw
`sys.query` against one frozen contextualization candidate while keeping all
other variables fixed. Measure referent resolution, retrieval facets, unsupported
history leakage, latency, tokens and cost.

No query rewriting is justified if follow-up retrieval is already adequate or
if it improves recall by introducing unsupported prior claims.

## Phase 8 — Validator and heuristic ablations

Run the controlled mutation benchmark first, then isolate one change at a time:

- quote normalization;
- `source_score`;
- comparison markers.

Decision evidence required:

- **Normalization:** current false rejection is material on semantically
  equivalent mutations, proposed normalization reduces it, and negative-control
  false acceptance does not increase beyond the predeclared safety margin.
- **Remove `source_score`:** removal is non-inferior on correct-source acceptance,
  restriction and final quality, and reduces documented misranking or complexity.
- **Remove comparison markers:** removal is non-inferior on comparison/conflict
  completeness and does not increase silent merges; otherwise retain until a
  separately tested replacement exists.

## Evidence packages and reporting

Each phase gets a dated, atomic, local-only package with configuration identity,
suite/rubric hashes, raw attempts, sanitized summary, manifest and limitations.
Formal runs must preserve private chunks locally and must not commit credentials,
raw private evidence or vector indexes.

## Stop rules

Stop a phase before modification when:

- the frozen identity cannot be established;
- gold labels are disputed or incomplete;
- a required telemetry field is missing for the research question;
- the operational retry limit is exceeded;
- a variant changes more than the declared independent variable;
- a held-out item has leaked into implementation prompts or tuning.

## What must remain unchanged before benchmark readiness

- V9.1 export, Draft/runtime graph and prompts;
- corpus source files, Knowledge Bases, chunks and index;
- models, parameters, retrieval Top K/weights and reranker state;
- memory and `sys.files` behavior;
- validator, normalization, `source_score` and comparison logic;
- timeout/retry rules after protocol freeze;
- held-out questions, gold labels and scoring rules after unblinding.
