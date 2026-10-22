# Code-node sources

- [`backend_file_registry.py`](backend_file_registry.py): parses the backend-authorized `aw5.source-registry.v1` envelope. Checks structure, UUIDs, duplicates, membership of documents in datasets and size limits; emits the shortlist wrapper consumed by the Resolver. Authentication remains the backend's responsibility.
- [`context_selector.py`](context_selector.py): current six-input selector extracted from the portable template. Retains required-source anchors, applies STRICT by document ID, caps context at 15 chunks and preserves provenance. Other-source selection uses only existing retrieval candidates; it does not perform another search.

`candidate_coverage` is source-candidate coverage, not semantic sufficiency. Exact source/quote validation alone does not prove a claimed relationship. Use the export's inputs/outputs when wiring nodes; do not paste fixture IDs or corpus-specific mappings into production logic.
