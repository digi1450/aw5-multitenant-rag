# Corpus Profile

## What the documents cover

The TOR defines the Nature Footprint application's background, objectives, functional scope, access levels, required deliverables, privacy obligations, security requirements, maintenance, and acceptance conditions.

The System Design Specification is a 474-page downstream artifact. Its main sections cover:

1. Project overview and user requirements
2. Input design and validation
3. UI, navigation, responsive behavior, and secure UI
4. Dashboards, reports, and verification outputs
5. Database architecture, ER diagram, and data dictionary
6. Security design, audit logging, vulnerability handling, and continuity
7. Nature Footprint calculations and data-quality analysis
8. Large appendices containing TOR material and calculation factors

The database schema contains 37 tables organized into five modules:

- `ORG`: organization, location, reporting period, and activity data
- `UM`: users, roles, permissions, systems, signatures, and organization membership
- `MD`: master data, indicators, activity types, factors, units, and histories
- `CALC`: assessments, indicators, results, and intermediate results
- `CM`: configuration, statistics/audit-like records, manuals, and files

## Why this is useful for the AW5 project

This is not merely a collection of unrelated PDFs. It is a traceable chain of requirements, system design, visual database design, and structured schema. It can support SDLC-specific questions such as whether a requirement is reflected in the design, which tables support a feature, and whether a database artifact is consistent with the design document.

## Ingestion cautions

- Do not treat every page of the 474-page specification identically. Factor appendices and narrative design sections need different chunking strategies.
- Preserve section titles, logical page numbers, physical PDF pages, table names, and source document IDs as metadata.
- Deduplicate repeated TOR material embedded in the System Design Specification.
- Normalize Thai text carefully and keep the original extraction for auditability.
- Prefer the dbdiagram text for schema semantics; use the diagram PDF for visual-layout experiments.
- A metadata filter must include both tenant and project scope when this corpus is ingested into the future multi-tenant system.

## Recommended metadata

```text
tenant_id
project_id
document_id
artifact_type
sdlc_stage
section_path
physical_page
logical_page
table_name
source_sha256
extraction_method
```

