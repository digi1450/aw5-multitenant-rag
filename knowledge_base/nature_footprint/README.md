# Nature Footprint Knowledge Base

This directory is an ingestion-ready, source-backed corpus for the AW5 Multi-Tenant RAG senior project. It is intentionally independent of any chunking library, embedding model, vector database, or RAG framework.

## Current direction — 2026-09-02

The target is [self-hosted Dify with local knowledge storage and cloud models](../../docs/architecture/current-direction-2026-09-02.md).
Use one retrieval node across the authorized project corpus. The artifact roles
below describe this case study; they are not source-router rules or descriptions
to embed in system prompts. Adding documents must not require per-file nodes or
prompt changes. Knowledge-base organization and ingestion/chunking methods remain
undecided, and this update has not migrated or re-indexed any files.

Local storage does not mean document text never leaves the computer: cloud
embedding receives chunk text during ingestion; reranking, if selected, receives
candidates; the answer LLM receives selected evidence. Providers and new transfers
of private material require approval.

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

The local `output/pdf/` directory is generated/private and excluded from Git. The recorded Dify Cloud ingestion files are listed below; this is not a verified inventory of a new self-hosted deployment:

- `output/pdf/Attach_TOR_1.pdf` — cleaned/OCR-ready TOR, renamed to the original user-facing filename so questions and citations match `Attach_TOR_1.pdf`.
- `output/pdf/System Design Specification.pdf` — cleaned/OCR-ready SDS, renamed to the user-facing filename used in Dify and citations.
- `knowledge_base/nature_footprint/sources/er-dbdiagram.txt` — structured ER/dbdiagram source used directly as `ER_dbdiagram.txt`; it does not require OCR or PDF noise removal.

The byte-preserved originals remain under the private `sources/` directory. Do not replace provenance sources with cleaned outputs or commit either private directory without explicit publication permission.

The original TOR is `sources/nature-footprint-tor.pdf`; its user-facing document
name is `Attach_TOR_1.pdf`. These refer to the same TOR artifact, not different
source categories. Preserve the original file and its manifest checksum.

## Corpus use cases, not a routing or execution plan

The existing corpus supports evidence tracing across requirements, design, and
schema. The following describe possible evidence relationships, not required
retrieval branches or permission to begin testing:

1. Retrieve a requirement from the TOR.
2. Retrieve its implementation/design explanation from the System Design Specification.
3. Retrieve the relevant tables and relationships from `er-dbdiagram.txt`.
4. Verify that all results are scoped to the Nature Footprint project.
5. Record document, page/section, and chunk provenance for every answer.
