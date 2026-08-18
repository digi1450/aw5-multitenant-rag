# Nature Footprint Knowledge Base

This directory is an ingestion-ready, source-backed corpus for the AW5 Multi-Tenant RAG senior project. It is intentionally independent of any chunking library, embedding model, vector database, or RAG framework.

## Purpose

The corpus represents connected software-project artifacts from several SDLC stages:

| Artifact | SDLC role | Primary RAG value |
| --- | --- | --- |
| Nature Footprint TOR | Requirements and contractual scope | Requirement retrieval and traceability |
| System Design Specification | Analysis and design | Long-document retrieval across requirements, UI, database, security, and calculation design |
| ER diagram PDF | Visual database design | Diagram and layout-aware retrieval challenge |
| dbdiagram text | Structured database design | Schema-aware retrieval and ground truth for the ER diagram |

## Directory layout

```text
nature_footprint/
├── manifest.json
├── sources/          Original, byte-preserved source copies
├── derived/text/     Reproducible plain-text extractions
├── notes/            Corpus profile and ingestion cautions
└── evaluation/       Candidate questions; not yet a scored gold dataset
```

## Important boundaries

- The source files are preserved without modification. Their SHA-256 checksums are recorded in `manifest.json`.
- Extracted text is derived data and may be regenerated.
- No embeddings or vector index are committed yet. Those decisions belong after the DS2 scope and requirements are agreed.
- Permission to publish or distribute these documents has not been established. Treat the corpus as private project material unless the owner confirms otherwise.
- The TOR extraction contains legacy Thai glyph/encoding artifacts. The ER diagram extraction does not preserve visual reading order reliably.

## Recommended first use

Use this corpus for a controlled proof of concept:

1. Retrieve a requirement from the TOR.
2. Retrieve its implementation/design explanation from the System Design Specification.
3. Retrieve the relevant tables and relationships from `er-dbdiagram.txt`.
4. Verify that all results are scoped to the Nature Footprint project.
5. Record document, page/section, and chunk provenance for every answer.

