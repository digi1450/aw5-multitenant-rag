# Nature Footprint Corpus Manifest

Status: draft source-identity authority for Phase 0 benchmark authoring. It does not change the corpus or Dify.

The frozen Knowledge Bases contain three indexed source records. The local ER-diagram PDF is retained as provenance but is not an expected retrieval source for this benchmark. Display filenames are never the sole identity.

| Source ID | Runtime document ID | Knowledge Base ID | Display filename | Canonical path | Type | Extent | Frozen KB |
|---|---|---|---|---|---|---|---|
| `nature-footprint-tor` | `7c5d8fc0-5a40-40db-b3f1-634827067506` | `ffa9afd2-c99b-4143-8f09-4ed6ed9d2b1d` | Attach_TOR_1.pdf | `knowledge_base/nature_footprint/sources/Attach_TOR_1.pdf` | requirements_tor_pdf | 17 pages | yes |
| `nature-footprint-system-design` | `d1359f85-f85a-4376-8a45-16c2720c905d` | `1f4b4f33-c29b-431a-ac21-416c6f3806fc` | System Design Specification.pdf | `knowledge_base/nature_footprint/sources/system-design-specification.pdf` | system_design_specification_pdf | 474 pages | yes |
| `nature-footprint-er-schema` | `dd86c6cf-3c68-4b2f-a2cc-1dc1696133a8` | `4c4ce1ad-cb9b-43f6-83b4-aa613899fb3c` | er-dbdiagram.txt | `knowledge_base/nature_footprint/sources/er-dbdiagram.txt` | dbdiagram_schema_text | 643 lines | yes |

## Version identity

- `nature-footprint-tor`: SHA-256 `84b3fd72b5b1d47dedf3c92c513d3443e1a5d339c231e0abcfe5615898213525`
- `nature-footprint-system-design`: SHA-256 `cefcbbfd1a82dc8d384a9b014a3266b1a4dad82f42b3dcf78b44c10b830b0de3`
- `nature-footprint-er-schema`: SHA-256 `887968339c32a84e77b80bdb586557a0169ea9c3579d87a98d7aa0d2ad5c03b8`

## Coverage and limitations

- `nature-footprint-tor` contains requirements, scope, deliverables and security/continuity conditions. Thai extraction has irregular spacing.
- `nature-footprint-system-design` contains prose, tables, figures, a data dictionary and appendices. Dense table extraction can lose cell alignment.
- `nature-footprint-er-schema` contains DBML declarations, constraints and explicit relationships. Names alone do not establish business meaning.

## Related local artifact outside the frozen Knowledge Bases

- `nature-footprint-er-diagram` (`knowledge_base/nature_footprint/sources/nature-footprint-er-diagram.pdf`) is a two-page visual provenance artifact with SHA-256 `5e19e5465ba683e71b46df7569d56b8351bfb9d03214ddd4486cc497bf292fcf`. It is not part of the benchmark source authority because it is not indexed in the three frozen Knowledge Bases; extracted text also cannot safely establish visual edges.

## Overlap

- The SDS repeats substantial TOR material in its requirements and appendix.
- The SDS data dictionary overlaps the DBML schema but sometimes presents different visible fields or names. Benchmark labels must keep source-specific declarations separate.
- The ER-diagram PDF and DBML schema overlap in subject matter, but only the DBML text is indexed in the frozen Knowledge Bases.
