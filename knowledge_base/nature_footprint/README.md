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
└── evaluation/       Versioned evaluation suite, run templates, and scored evidence
```

## Important boundaries

- The source files are preserved without modification. Their SHA-256 checksums are recorded in `manifest.json`.
- Extracted text is derived data and may be regenerated.
- Dify Cloud knowledge bases and hosted vector indexes were used for the recorded RAG evaluation. Embeddings and vector-index data are not committed to this repository and cannot be reconstructed from Git alone without recreating the Dify knowledge bases.
- Permission to publish or distribute these documents has not been established. Treat the corpus as private project material unless the owner confirms otherwise.
- The TOR extraction contains legacy Thai glyph/encoding artifacts. The ER diagram extraction does not preserve visual reading order reliably.

## Dify ingestion files

The local `output/pdf/` directory is generated/private and excluded from Git. The files used for the current Dify knowledge bases are:

- `output/pdf/Attach_TOR_1.pdf` — cleaned/OCR-ready TOR, renamed to the original user-facing filename so questions and citations match `Attach_TOR_1.pdf`.
- `output/pdf/System Design Specification.pdf` — cleaned/OCR-ready SDS, renamed to the user-facing filename used in Dify and citations.
- `knowledge_base/nature_footprint/sources/er-dbdiagram.txt` — structured ER/dbdiagram source used directly as `ER_dbdiagram.txt`; it does not require OCR or PDF noise removal.

The byte-preserved originals remain under the private `sources/` directory. Do not replace provenance sources with cleaned outputs or commit either private directory without explicit publication permission.

## Recommended first use

Use this corpus for a controlled proof of concept:

1. Retrieve a requirement from the TOR.
2. Retrieve its implementation/design explanation from the System Design Specification.
3. Retrieve the relevant tables and relationships from `er-dbdiagram.txt`.
4. Verify that all results are scoped to the Nature Footprint project.
5. Record document, page/section, and chunk provenance for every answer.
