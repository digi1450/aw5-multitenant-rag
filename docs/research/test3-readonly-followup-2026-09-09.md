# Test3 read-only follow-up — image forwarding and missing evidence

Classification: **Incident evidence**. No new model calls, search reruns, workflow edits or corpus changes.

## Findings

### Image provenance

Three image attachments in the two unnamed-query Draft replays are bound to existing SDS parents 11 (one image) and 31 (two images). Their database creation records are dated September 2, before the tests. They are not screenshots newly uploaded by the user. No image pixels were inspected.

Retrieval and Code 2 both had zero explicit `files` items in API and replay traces. The difference first appears in LLM input `#context_files#`: zero for API, three for Draft. The installed graphon LLM implementation calls an attachment loader using the metadata `segment_id`. It can therefore attach stored images without a nonempty result `files` list.

The loader checks execution-local segment grants. The installed scope code permits account/debugger access differently from end-user API access. This establishes a mechanism for path differences, but the prior API grant state was not captured; it does not prove precisely why its grant was unavailable. A future controlled replay must preserve caller identity, authorized attachment scope and modalities. Do not strip citation metadata or bypass the access check to force equality.

### Source state

All 538 checked parent IDs, content hashes, enabled flags and statuses match the earlier Test3 environment capture. This corroborates the owner's statement for those fields; child-index/vector history was not captured earlier and is not claimed unchanged.

The required project code exists in enabled, completed TOR parent 1 and SDS parent 9 and their children. It was not absent from the stored corpus. In the original full-filename trace, the ten recorded child hits reconstruct to seven SDS parents; neither relevant project-code parent appears.

ER parents 33 and 34 contain complete factor and factor-history table blocks, with 41 and 43 children respectively. Children are individual lines, including isolated field declarations and closing braces. The current subchunk separator is newline. The table name, source-reference field and history fields are therefore separated at the child-search level, despite coherent parents. This is a concrete configuration finding and a plausible semantic-recall weakness, not proof that re-chunking will fix the query.

### Candidate-selection boundary

The installed implementation performs per-KB retrieval/fusion, then final selection across candidates, then child-to-parent reconstruction. With node reranking disabled, the final high-quality merge sorts existing scores and takes Top K; it does not recompute the configured node weights. Parent count may be below Top K and does not alone imply a disabled document or missing database record.

The prior traces contain final results only. They cannot establish whether the missing child was absent from its KB candidate pool, displaced at the cross-KB cutoff or lost during formatting. No exact failed-stage claim is made.

## Next bounded diagnostic

Request approval for two retrieval-only executions of the existing named-project-code and factor-history questions. Capture each KB's pre-merge candidates, post-merge selection and reconstructed parents without changing settings or invoking the answer model. This may call query embeddings. Only after this comparison choose between query representation, candidate selection and ER subchunk changes in a separate copy.

## Evidence

- Local evidence package: `output/research-evidence/experiments/2026-09-09-test3-readonly-followup/`. Private excerpts remain ignored by Git.
- The package contains `report.md`, `evidence.json`, `manifest.json`, the inspection script and targeted runtime findings.
- Prior evidence: [Test3 diagnostic](test3-prefilter-guard-diagnostic-2026-09-09.md).
- Five inspected local Dify source files match the installed container hashes. The installed graphon node was read directly and hashed.

No workflow/source edit, publish, commit or push occurred.
