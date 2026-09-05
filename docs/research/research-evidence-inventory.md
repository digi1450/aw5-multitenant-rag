# AW5 Research Evidence Inventory

## Inventory status

- Inventory baseline date: **2026-09-04 (Asia/Bangkok)**
- Latest material status update: **2026-09-06 (Asia/Bangkok)**
- Repository: `AW5Project`
- Branch at capture: `feature/dify-self-hosted`
- HEAD at capture: `a742a4d2695f119cffb224da65691f4652f4961e`
- Purpose: preserve a publication-ready map of what evidence exists, where it is
  stored, what it proves, and what remains unverified.
- This inventory does not convert historical experiments into evidence for the
  current self-hosted target.
- No experiment was rerun to create this inventory.
- No file was committed or pushed while creating it.

The local machine-readable artifact snapshot is stored at
`output/research-evidence/research-evidence-artifact-manifest-2026-09-04.json`.
It catalogs 183 research-related files using repository-relative paths, byte
sizes, modification times, SHA-256 hashes, Git status, and evidence class.
The snapshot itself is local-only and ignored by Git. It predates the addition of
the 2026-09-04 and 2026-09-06 self-hosted workflow exports, records and
diagnostics, so its 183-file count must not be interpreted as a live count after
these updates.

| Snapshot property | Value |
| --- | ---: |
| Generated | `2026-09-04T18:38:58+07:00` |
| Cataloged artifacts | 183 |
| Total cataloged bytes | 37,663,393 |
| Git-versioned artifacts | 43 |
| Needs-review artifacts | 9 |
| Local-only artifacts | 131 |
| Snapshot SHA-256 | `e58adadd98d32dcb774cfa5e3870cc13ec46a0508d451d5432339de4fef75992` |

## Evidence language

This inventory uses these status terms consistently:

| Status | Meaning |
| --- | --- |
| **Verified** | Supported by a durable artifact, reproducible file hash, Git record, saved trace, or direct system inspection recorded at the time. |
| **Owner-observed** | Reported or shown by the project owner, including Dify UI screenshots, but not yet preserved as a durable repository artifact or reproducible run. |
| **Partial** | Some parts are supported, while an important dimension such as citations, repeatability, cost, or live-state identity remains unverified. |
| **Historical** | Valid evidence for an earlier workflow or decision, retained as a control and not attributed to the current target. |
| **Planned** | Proposed work with no implementation or test evidence. |
| **Missing** | Required evidence is not available and must not be reconstructed by assumption. |

## Timeline of material work and evidence

### 2026-08-14 to 2026-08-20 — corpus preparation and project setup

| Date | Activity and evidence | Status | Current relevance |
| --- | --- | --- | --- |
| 2026-08-14 | Nature Footprint corpus metadata records four provenance sources: TOR PDF, 474-page SDS PDF, visual ER PDF, and 643-line/37-table dbdiagram text. Original SHA-256 values are retained in `knowledge_base/nature_footprint/manifest.json`. Derived SDS and ER text files have local timestamps from this date. | **Verified local evidence** | Establishes corpus provenance. Source and derived content remain private and excluded from Git. |
| 2026-08-18 | Repository initialized in commit `232e27c`. The initial commit added DS1, course requirements, corpus metadata/profile, repository documentation, and candidate evaluation questions. | **Verified Git evidence** | Beginning of the durable Git history. Work before this date is represented only by source metadata and local file timestamps. |
| 2026-08-20 | Local TOR derived-text artifact has a later timestamp than the initial corpus extraction. | **Verified file existence; process detail partial** | Confirms a local derived artifact existed, but no separate run log records the exact transformation sequence. |

Primary artifacts:

- `docs/deliverables/ds1/submitted/AW5-ProjectConcept.pdf`
- `docs/course-requirements/ds1-ds3-requirements.md`
- `knowledge_base/nature_footprint/manifest.json`
- `knowledge_base/nature_footprint/notes/corpus-profile.md`
- Private originals under `knowledge_base/nature_footprint/sources/`
- Private extractions under `knowledge_base/nature_footprint/derived/text/`

### 2026-08-25 — baseline diagnosis, source-routing implementation, and full evaluation

| Evidence | Result | Status and limit |
| --- | --- | --- |
| Representative baseline, six fresh cases | Strict `2/6`; answer content `5/6`; all three single-source cases had extra-source citations; cross-document case `0/1`; safety cases `2/2`. | **Historical verified run.** Demonstrated citation pollution, lost cross-document facets, and excessive context before source routing. |
| Post-fix representative retest | Five targeted cases passed after source-specific routing; ER Top K increased from 3 to 6 based on retrieved evidence. | **Historical verified targeted retest.** Not a full-suite result by itself. |
| Full-suite post-fix evaluation | Strict `19/19`; TOR/SDS Top K 3, ER Top K 6, weighted semantic/keyword `0.5/0.5`, reranking disabled. | **Historical verified scored evaluation.** `ISO-01` excluded. The saved draft was not Published at capture. |
| Final workflow export | `aw5-rag-source-routing-final-2026-08-25.yml`, SHA-256 `2c0a5c2abfd4b180c5fcc9d20bf52f610ad496aee8fd4a2566268933ea125aa7`; 9 nodes/10 edges. | **Historical verified snapshot.** Repository handoff completed in commit `64418f8`. |

Primary artifacts:

- `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-representative-baseline.md`
- `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-full-suite-postfix.md`
- `knowledge_base/nature_footprint/evaluation/evaluation-suite-v1.md`
- `dify/exports/aw5-rag-source-routing-final-2026-08-25.yml`
- Git commits `73930ea`, `0e532ef`, and `64418f8`

### 2026-08-26 — status and agent guidance

Commit `5f02474` refreshed project status and added repository agent guidance.
This is **verified documentation history**, not a separate RAG evaluation.

### 2026-08-27 — diagnostic suite and conditional-routing experiments

| Evidence | Result | Status and limit |
| --- | --- | --- |
| Diagnostic v2, 20 new questions | First-attempt workflow success `17/20`; provisional strict outcome `14/20` after controlled retries; 94,585 primary tokens; USD 0.1189807 primary price; primary median 18.441 s. All three retrievers executed for every case, including 33 disabled-route executions. | **Historical verified diagnostic.** Exact final citation attachments were not retained by that runner version. |
| Conditional Gating v1 full regression | `12/19` strict; all 19 workflows completed; exact predefined routing `16/19`; 108,455 tokens; USD 0.1545191; median 19.735 s. | **Historical verified failed candidate.** Proved conditional gates executed correctly but routing/query/answer quality regressed. |
| Final Route Guard smoke | Owner-reviewed `7/7` routes and answers after fixing `tor` matching inside `indicator`; ER Top K 7 was justified by `UM_USER` at retrieval position 7. | **Historical owner-reviewed smoke evidence.** No fresh 19-case regression after the final fix. |
| Route Guard export | 19 nodes/23 edges; SHA-256 `52a4598dad3f2d56d5deee5f058bf5fdfce82a43523d050b858b66d9b2864754`. | **Historical candidate.** Not promoted. |

Primary artifacts:

- `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-diagnostic-v2.md`
- `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-conditional-gating-v1-regression.md`
- `knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-27-route-guard-smoke.md`
- `dify/exports/aw5-rag-route-guard-candidate-2026-08-27.yml`
- Git commit `a14ccd8`

### 2026-08-28 — baseline repeatability and provider behavior

The Published Service API baseline recheck ran 19 executable cases:

| Metric | Recorded value |
| --- | ---: |
| Route match | 19/19 |
| Successful primary executions | 18/19 |
| Eventual citation boundaries after bounded retry | 19/19 |
| Strict semantic quality after bounded retry | 16/19 |
| Median latency | 13.87 s |
| Mean latency including provider stalls | 39.75 s |
| p95 latency including provider stalls | 228.50 s |
| Median tokens | 4,856 |
| Primary-run tokens | 96,083 |
| Recorded price | approximately USD 0.1314 |

Demonstrated failures were incomplete `ER-01`, incomplete cross-document
`XDOC-02`, and an unsupported strengthening in `EDGE-03`. Provider evidence
included Gemini `503 UNAVAILABLE` and two LLM 1 stalls above 200 seconds. This
run is **historical verified regression evidence** and demonstrates that the
earlier `19/19` result was not a stability guarantee.

Primary artifact:
`knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-28-baseline-recheck.md`.
The related status was committed in `77c9575`.

### 2026-08-29 — Lean Adaptive v1 to v1.4 experiments

| Candidate/run | Recorded result | Status and limit |
| --- | --- | --- |
| v1 `ER-01` smoke | Complete six-table answer; 6.82 s; 5,765 tokens; citation boundary included SDS+ER instead of ER only. | **Historical strict fail.** |
| v1.1 two `ER-01` runs | Complete answer and ER-only guarded route; 12.54/7.40 s; zero citations in both runs. | **Historical repeated strict fail.** |
| v1.2 two `ER-01` runs | Complete answer and ER-only route; 7.72/11.43 s; zero streaming citations despite retained metadata. | **Historical repeated strict fail.** |
| v1.3 `ER-01` smoke | Complete answer; ER-only merge; 13.40 s; zero citations. | **Historical strict fail.** |
| v1.4 targeted smoke | `ER-01` and `XDOC-02` complete; user confirmed precise citations in Dify UI. | **Historical targeted pass.** Streaming API still returned no citation resources. |
| v1.4 full regression | Route `19/19`; 18/19 primary executions; one Gemini 503; provisional semantic `19/19` after retry; p50 9.10 s; p95 14.66 s; 113,879 primary tokens; USD 0.1658; Repair used in 2/19. | **Historical partial evidence.** Only three cases had user-verified UI citation precision, so strict citation `19/19` was not claimed. |

Lean Adaptive artifacts were added to Git on 2026-09-02 in commit `a742a4d`,
but the direction they supported was superseded on that same date. They remain
controls and must not be presented as the current target implementation.

### 2026-08-30 to 2026-09-01 — study and planning interval

The project owner confirmed on 2026-09-04 that this interval mainly consisted of
planning, studying, and small adjustments. Some informal tests may have occurred,
but no material experimental movement or durable test result was produced.

Inventory treatment: **no material recorded activity**. This is an intentional
and plausible research-history gap, not evidence that a missing experiment passed
or failed. No retrospective metrics will be invented for this interval.

### 2026-09-02 — architecture reset and self-hosted foundation

#### Current-state snapshot and architecture decision

- Owner supplied `AW5-RAG 1.2` as the then-current workflow export.
- Export SHA-256:
  `7e1d7d7e49f711bf0653db38ed6b3923f590cf83d5b4d46538db6ae4fe2f320d`.
- Static graph: 9 nodes/10 edges, two LLM nodes, separate TOR/SDS/ER retrieval,
  weighted `0.5/0.5`, TOR/SDS Top K 3, ER Top K 10, reranking disabled.
- The export was preserved byte-for-byte but not newly runtime-tested or matched
  against Published state.
- Owner confirmed a new target: self-hosted Dify, local persistent knowledge/files,
  cloud model APIs, one Knowledge Retrieval node, generic prompts, and no
  TOR/SDS/ER source-router flags.

Status: **verified Git snapshot and owner-confirmed decision**, committed in
`a742a4d`. It is not evidence that the new target was implemented.

#### Local Dify installation

- Dify 1.17.0, upstream commit
  `09a855dcef24c0edc7431c46c0cfaa494481daf5`.
- Local Compose project `aw5-dify`; PostgreSQL, Redis, Weaviate and application
  storage retained locally; nginx published only at `127.0.0.1:8080`.
- At the recorded final check, 15 long-running services were running with zero
  restarts; configured health checks passed; `/install` returned HTTP 200.
- Installation evidence JSON SHA-256:
  `ef0eb99993cd9dab51e57936d92a9bbd2fe07eed88c427c229cf508ff06096a4`.
- Backup/restore and long-term stability were not tested.

Status: **verified installation evidence**, committed in `f6aee70`.

#### Custom embedding plugin signing and installation

- Gemini Embedding 2 (AW5) plugin 0.1.4 was signed with an owner-controlled key
  and accepted by Dify 1.17.0.
- Original package SHA-256:
  `04365e1cc3b23f685dc5d9d75c226e978a0bb5b2d8bf490d8d38fb158c570c72`.
- Signed package SHA-256:
  `dc916b77b4dff9b1bacd8df1d35327ad45d3ea8edd100101db0fa0daa25a2e3e`.
- Private key and `.difypkg` files remain local and must never be committed.

Status: **verified installation evidence**, committed in `f6aee70`. The provider
was locally trusted by the owner; this is not Dify Marketplace endorsement.

#### Synthetic multimodal retrieval pilot

- Two-page synthetic PDF; no Nature Footprint material.
- Dify indexed native text and an image-only page using `gemini-embedding-2`.
- All three queries ranked the expected source first.
- Indexing latency was 4.694 s. Answer LLM, reranker, distractor documents,
  repeated trials, cost, query latency, real Thai corpus quality and tenant
  isolation were not tested.
- Fixture SHA-256:
  `387165bc7dde9d93273fc5a7eafdc46b7363b9c6a6ed7adbfa3d26f3d4e09a1e`.

Status: **verified synthetic ingestion/retrieval smoke evidence**, with the
sanitized report committed in `f6aee70`. Supporting files remain local under
`output/pdf/aw5-local-pilot-2026-09-02/`.

### 2026-09-03 — project-tenant boundary and self-hosted corpus work

- Owner locked the business definition: one AW5 tenant equals one software
  project; `tenant_id` is the only AW5 project-scope identifier. The current
  tenant is `tenant_id = 1`, `tenant_name = Nature Footprint`.
- Three Knowledge Bases are used for the current tenant, one per primary file:
  TOR, SDS and ER/dbdiagram, connected to the same retrieval node.
- Owner-provided Dify UI evidence shows local Knowledge Base creation, document
  ingestion, metadata and chunk inspection. At that date, the repository did not
  yet contain a current target DSL export, database snapshot, or structured
  evaluation trace.
- SDS figure-related parent chunks around figures 4-20 through 4-24 were manually
  inspected and repaired in the Dify UI. Garbled extracted text was removed and
  image attachments were used where appropriate. Exact before/after chunk bodies
  and saved TOR/SDS ingestion settings are not preserved as durable evidence.

Status: tenant definition is **owner-confirmed and documented**, committed in
`f6aee70`.
The Dify corpus/chunk work is **owner-observed current-state evidence** and needs
a durable sanitized snapshot before publication claims.

### 2026-09-04 — chunking investigation, ER alternatives, and current gap analysis

- Owner-provided Dify UI evidence for the ER Knowledge Base showed Parent-child,
  High Quality, Hybrid Search and `gemini-embedding-2`.
- Observed ER settings: parent delimiter `\n\n`, parent maximum 1,200 characters;
  child delimiter `\n`, child maximum 512 characters; consecutive-whitespace
  preprocessing enabled; 46 parent chunks.
- One-line children improve exact column matching but repeated generic fields such
  as audit columns have weak table identity in their child text. Parent retrieval
  restores table context after a child is selected, but cannot guarantee exhaustive
  retrieval of every table containing the same column.
- Local parser prototypes and three generated ER variants were created for
  comparison. They remain exploratory and local-only:
  `dbml_preprocessor.py`, `dbml_column_prefix.py`,
  `dbml_schema_retrieval.py`, and outputs under `output/dify/`.
- The current direction is to retain the original ER source and current
  Parent-child experiment while deferring structured exhaustive lookup until a
  requirement demands complete enumeration across all tables.
- The deferred design is recorded in
  `knowledge_base/nature_footprint/notes/er-exhaustive-column-lookup-contingency.md`.
- Recent general-user questions and Docker/UI checks were exploratory. The owner
  observed usable answers after fixing an inaccessible chunk, but no fixed suite,
  saved raw traces, scores, latency distribution, token totals or cost record were
  produced. They are therefore not counted as a new evaluation run.
- A read-only live Docker check during Inventory creation could not connect because
  the Docker API socket was absent. This does not invalidate the dated installation
  evidence or owner screenshots; it means live status was **not reverified** at the
  Inventory capture time.
- Owner supplied `AW5-RAG-2.yml` from the local self-hosted system and identified
  it as the new main workflow. The byte-identical repository snapshot is
  `dify/exports/aw5-rag-self-hosted-main-2026-09-04.yml`, SHA-256
  `b843323262447b25eca4d17304c2b94d521cb53cdc75a18d6f30153e93c25b6d`.
- Static inspection confirmed 4 nodes/3 edges:
  `User Input -> Knowledge Retrieval -> LLM -> Answer`. One retrieval node
  references three Knowledge Bases; weighted search is semantic/vector `0.7` and
  keyword `0.3`, Top K 10, with reranking and score threshold disabled.
- The answer model is `gemini-3.5-flash`; the generic prompt is evidence-grounded;
  conversation memory is enabled with a window of 10.
- The export was parsed and preserved without executing it. Its main-workflow
  status is owner-confirmed; live-app equality, Published/draft state, answer
  quality, citations, latency, cost and project-tenant isolation remain unverified.

Status at capture: **owner-confirmed then-current main workflow with verified
static export, plus owner-observed exploratory corpus work**. It was superseded
on 2026-09-06. No self-hosted RAG quality score was claimed for this snapshot.

### 2026-09-05 — named-source diagnosis and evidence handoff rules

- Bounded read-only runtime inspection demonstrated that Knowledge Retrieval
  results contained `document_name` and `dataset_name`, while the LLM Context
  rendering exposed retrieved content without those source identifiers.
- A generic prompt alone could therefore not enforce named-document attribution
  reliably. The owner added a deterministic Code node that prefixes retrieved
  content with those two metadata values while retaining result order and the
  other fields. It does not add a source router or metadata filter.
- Exploratory filename retrieval and metadata-filtering attempts remain failures,
  not proof of a ranking, filter, configuration or indexing remedy. Filename
  search remains outside the current priority.
- `AGENTS.md` now defines runtime evidence checkpoints, the boundary between test
  tasks and the scheduled collector, and the owner-directed 20-second cutoff with
  one fresh-conversation retry for local diagnostics.
- Raw reports, answers and retrieval details remain local-only under
  `output/research-evidence/experiments/`.

Status: **verified diagnostic finding and owner-directed workflow change; local
evidence only at this date**. No formal evaluation was run.

### 2026-09-06 — TOR chunk repair and current-main promotion

- TOR section 4.7.5 was split between consecutive parent chunks after item (5).
  The owner moved items (6)–(9) into the parent containing the section heading
  and regenerated child chunks. A bounded retest returned all nine items. This is
  a targeted runtime repair, not a proven corpus-wide chunking method.
- The first five-case Published API diagnostic exercised the earlier four-node
  graph because Code had not yet been Published. It produced 2 pass, 2 partial
  and 1 fail; the LLM prompts contained no source prefixes.
- After the owner Published Code, the same five questions exercised
  `User Input -> Knowledge Retrieval -> Code -> LLM -> Answer`. Read-only runtime
  inspection confirmed source prefixes in every rendered LLM prompt.
- The after-state produced 4 pass, 1 partial and 0 fail, with no timeout or retry.
  Wall time was 3.614–5.610 seconds (median 4.207); Code took
  0.030–0.048 seconds; answer-model usage totaled 21,634 tokens and USD 0.048096,
  excluding embedding cost.
- The partial result correctly identified the same four indicator categories in
  TOR and SDS but overstated them as `เหมือนกันทุกประการ` despite differences in
  wording and cited sections.
- The owner promoted the Published workflow to current main and supplied
  `AW5-RAG Test-2.yml`. The byte-identical repository snapshot is
  `dify/exports/aw5-rag-self-hosted-main-2026-09-06.yml`, SHA-256
  `8ad21cbfbebc7fd87f0f6ac193098623db0bb43acf994745b74716ca77668cea`.
- Static inspection confirmed 5 nodes/4 edges, one LLM call, one retrieval node,
  weighted search `0.7/0.3`, Top K 10, reranking/threshold/metadata filtering
  disabled, and LLM Context wired to `Code.result` with `{{#context#}}` present.

Status: **owner-confirmed current main with verified static export, Published
five-node path and positive targeted exploratory evidence**. Formal-suite
accuracy, repeatability, production readiness and tenant isolation remain
unverified. See
`docs/research/self-hosted-source-prefix-diagnostic-2026-09-06.md`.

## Evaluation evidence catalog

The versioned evaluation directory contains 18 Git-tracked artifacts: 16 Markdown
files and two JSON suite definitions.

| Category | Files and role |
| --- | --- |
| Suite definitions | `evaluation-suite-v1.md`, `evaluation-suite-v1-executable.json`, `evaluation-suite-v2-diagnostic.md`, `evaluation-suite-v2-diagnostic.json` |
| Templates/candidates | `evaluation-run-template-v1.md`, `question-candidates.md` |
| 2026-08-25 runs | Representative baseline and strict `19/19` full-suite post-fix report |
| 2026-08-27 runs | Conditional Gating `12/19`, Diagnostic v2 provisional `14/20`, Route Guard `7/7` smoke |
| 2026-08-28 run | Published baseline recheck `16/19` strict after bounded retry |
| 2026-08-29 runs | Lean Adaptive v1, v1.1, v1.2, v1.3, v1.4 smoke reports and v1.4 full report |

The local ignored `output/evaluation/` directory contains 103 sanitized JSON
trace files totaling 2,949,265 bytes. These files are valuable raw evidence but
remain outside Git. A filename family is not treated as a result unless a report
or direct trace audit establishes its meaning.

| Raw trace family | Files | Bytes | Evidence treatment |
| --- | ---: | ---: | --- |
| `aw5-rag-diagnostic-v2` | 10 | 201,325 | Local raw support for Diagnostic v2 |
| `aw5-rag-v1-executable-regression` | 7 | 373,674 | Local raw regression attempts; interpret through dated reports where available |
| `aw5-rag-route-guard` | 5 | 505,717 | Local raw Route Guard runs |
| `aw5-rag-production-core-v1` | 4 | 430,793 | Local experimental traces; no standalone tracked publication summary |
| `aw5-production-v1-postfix` | 29 | 437,363 | Local baseline/post-fix and retry traces |
| `aw5-verifier-medium` | 10 | 142,702 | Local verifier experiment traces; no promoted result |
| `aw5-coverage-v1` | 25 | 558,650 | Local coverage experiment traces; no promoted result |
| Lean Adaptive v1 | 1 | 10,086 | Local v1 smoke trace |
| Lean Adaptive v1.1 | 2 | 18,866 | Local v1.1 smoke traces |
| Lean Adaptive v1.2 | 2 | 21,990 | Local v1.2 smoke/diagnostic traces |
| Lean Adaptive v1.3 | 1 | 8,979 | Local v1.3 smoke trace |
| Lean Adaptive v1.4 | 7 | 239,120 | Local v1.4 smoke, full, retry and instability traces |

## Dify workflow and architecture artifact catalog

| Artifact group | Quantity/status | Evidence boundary |
| --- | --- | --- |
| Git-tracked Dify exports after this update | 18 files: 8 YAML and 10 Markdown records | Includes the owner-confirmed self-hosted main export, previous snapshots, frozen baseline and historical candidates. Static export verification is not runtime validation. |
| Current export pointer | `dify/exports/CURRENT.md` | Separates the current self-hosted main workflow, previous snapshot, frozen baseline and historical candidates. |
| Local installation evidence | Four Markdown/JSON records from 2026-09-02 | Reviewed, sanitized and committed in `f6aee70`; contain no private corpus content by design. |
| Runtime state | Sibling `dify-local` directory and Docker volumes | Local-only. Git cannot reproduce admin state, providers, Knowledge Bases, attachments, embeddings or vector indexes. |
| Custom plugin packages/keys | Ignored `.difypkg` files and local signing keys | Local-only; private key and credentials must never enter Git. |

## Corpus and local artifact catalog

| Group | Files | Bytes | Git policy |
| --- | ---: | ---: | --- |
| Private provenance sources | 4 | 17,207,750 | Local-only until publication permission is explicit |
| Derived corpus/parser files | 7 | 3,986,711 | Local-only by current repository policy; parser code can later be reviewed separately if adopted |
| Cleaned ingestion PDFs and generated evaluation PDFs outside the synthetic pilot | 5 | 12,546,529 | Local-only |
| Synthetic pilot bundle | 9 | 269,996 | Local-only raw evidence; sanitized summary is a commit candidate |
| Generated ER ingestion variants | 3 | 96,256 | Local-only exploratory output |

Source checksums, page/line counts and public-safe metadata are preserved in
`knowledge_base/nature_footprint/manifest.json`. The original files, extracted
text, cleaned PDFs, images and generated outputs remain private by default.

## Current uncommitted work snapshot

At the beginning of the 2026-09-04 inventory pass, Git CLI reported:

- branch `feature/dify-self-hosted` at `a742a4d`;
- `HEAD...origin/main` divergence `0 0`;
- seven modified tracked files with `+103/-45` tracked-line changes;
- six untracked, potentially Git-safe evidence/decision files.

The owner separately reported that the Codex UI displayed total local changes of
`+841/-45`. This broader figure likely includes new untracked file contents that
plain `git diff --stat` does not count. Both observations establish the same
important status: **the latest self-host work is still local and has not been
committed or pushed**.

Modified tracked files present before this inventory:

- `AGENTS.md`
- `README.md`
- `dify/exports/CURRENT.md`
- `docs/architecture/current-direction-2026-09-02.md`
- `knowledge_base/nature_footprint/README.md`
- `knowledge_base/nature_footprint/manifest.json`
- `knowledge_base/nature_footprint/notes/corpus-profile.md`

Untracked commit candidates present before this inventory:

- `docs/architecture/dify-local-installation-2026-09-02-evidence.json`
- `docs/architecture/dify-local-installation-2026-09-02.md`
- `docs/architecture/gemini-embedding-2-local-pilot-2026-09-02.md`
- `docs/architecture/gemini-embedding-2-local-signing-2026-09-02.md`
- `docs/architecture/tenant-project-boundary-2026-09-03.md`
- `knowledge_base/nature_footprint/notes/er-exhaustive-column-lookup-contingency.md`

This inventory adds one more untracked commit candidate:
`docs/research/research-evidence-inventory.md`. No staging, commit or push had
occurred at the baseline capture point. Later on 2026-09-04, the owner authorized
reviewing this local change set and committing/pushing the Git-safe evidence. That
authorization does not include the local-only artifacts classified below.

## Git classification policy

| Class | Default handling | Examples |
| --- | --- | --- |
| **Git-versioned / commit candidate** | Review for accuracy, privacy and secrets; commit only as a meaningful evidence milestone. | Sanitized experiment reports, suite definitions, architecture decisions, scripts intended for reproducibility, source metadata/checksums, reviewed secret-free DSL exports. |
| **Local-only** | Preserve on the owner machine and back up outside Git. | Private PDFs/TXT, extracted text, raw retrieved chunks, raw JSON traces, screenshots containing project content, cleaned ingestion files, Dify databases/volumes, vector indexes, `.env`, credentials, signing private keys, `.difypkg`. |
| **Needs review** | Do not stage automatically. Decide whether to sanitize, adopt, archive locally, or discard. | Exploratory parsers, generated variants, incomplete notes, UI screenshots, undocumented raw experiments. |

An automated evidence task must never use `git add -A` or stage all modified
files. It may update the inventory and prepare an exact candidate list, but it
must skip a commit when unrelated owner changes are mixed into the working tree.
Push remains a separate explicit action.

## Confirmed gaps and non-claims

1. There is no complete process log before the Git repository began on
   2026-08-18. Source metadata and local timestamps are the available evidence.
2. The 2026-08-30 to 2026-09-01 interval contains no material recorded run by
   owner confirmation. Informal study and small adjustments are not reconstructed
   as experiments.
3. Historical `19/19` results apply only to dated historical workflows and
   rubrics. They do not validate the self-hosted target.
4. The current self-hosted workflow has a reviewed, byte-identical DSL export and
   a verified Published five-node runtime path. Only a targeted five-case
   diagnostic exists; formal-suite accuracy and repeatability remain unverified.
5. The TOR 4.7.5 chunk repair has structured local evidence and a sanitized
   summary, but cross-page chunk quality across the rest of the corpus is not
   established.
6. TOR/SDS/ER Knowledge Base creation and selected chunk settings are observed,
   but the complete current database, document, chunk and vector-index state is
   not portable or reproducible from Git.
7. Backup/restore, long-term service stability and disaster recovery are untested.
8. Trusted backend enforcement of the AW5 `tenant_id` and cross-tenant isolation
   remain unimplemented/unverified. `ISO-01` remains N/A.
9. Publication permission for Nature Footprint documents remains unknown; the
   repository and corpus must remain private.
10. Docker was not live-reverified at inventory capture because its API socket was
    unavailable.

## Fields required for future evidence

Each future material experiment should record:

1. evidence/run ID and Asia/Bangkok timestamp;
2. question or hypothesis and the decision it is intended to support;
3. exact workflow export and SHA-256;
4. Knowledge Base document/version and chunking configuration;
5. embedding, reranker and answer-model/provider versions;
6. retrieval mode, weights, Top K, threshold and metadata filters;
7. fixed questions and scoring rubric used;
8. retrieved source/chunk identities and citation evidence without private text;
9. answer correctness, requested-facet completeness and insufficient-evidence behavior;
10. end-to-end p50/p95, node latency, tokens, estimated cost and provider errors;
11. number of repeats, retries and configuration changes during the run;
12. raw local artifact paths and hashes;
13. privacy class, Git class and publication suitability;
14. `verified`, `partial`, `failed`, `planned` or `missing` status with explicit limits.

## Schedule handoff boundary

The local `AW5 Daily Research Evidence` scheduled collector inventories, hashes,
classifies and summarizes evidence that test tasks have already captured. It is
not an evaluation runner and must not reconstruct transient runtime evidence,
change Dify/Docker, reclassify results, or commit/push local-only artifacts. Its
default remains report-only; any future auto-commit requires separate owner
authorization and a sanitized allowlist proven not to mix in unrelated changes.
