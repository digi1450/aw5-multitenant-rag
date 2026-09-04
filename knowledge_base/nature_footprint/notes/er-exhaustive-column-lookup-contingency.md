# ER Exhaustive Column Lookup Contingency

**Recorded:** 2026-09-04
**Status:** Deferred contingency; not a current requirement, approved implementation, or committed workflow direction.

## Current boundary

Keep the canonical `er-dbdiagram.txt` source and the current parent-child
retrieval approach for ordinary schema questions. A child can retrieve its full
table parent, so questions about a named table, its columns, and a distinctive
column can be answered from the original DBML without rewriting every field as
`TABLE.COLUMN`.

The known unresolved case is an exhaustive reverse lookup such as:

> Which tables contain a given column? Return every matching table.

Similarity retrieval returns only its selected Top K results. If a common column
occurs in more table parents than the final Top K, the answer model cannot recover
tables that were not included in its context. Reranking can reorder retrieved
candidates but cannot guarantee exhaustive coverage.

Document-level metadata does not solve this while the DBML remains one document,
because all table parents inherit the same document metadata. Splitting every
table into a separate metadata-bearing document would be a larger ingestion
change and would still retain a final Top K limit.

## Activation criteria

Reconsider this contingency only when at least one of these conditions is met:

1. An explicit product or course requirement demands complete column-to-table
   enumeration, exact counts, or another exhaustive schema query.
2. A representative evaluation includes this behavior and the current retrieval
   path reproducibly omits valid tables.
3. Real usage shows that incomplete reverse lookup materially affects users.

Until then, do not add a classifier, schema database, graph database, parser-only
ingestion path, or extra model call for this case.

## Preferred first fallback: generated column catalog

Generate a derived catalog from the canonical DBML. Each repeated column receives
one compact entry containing every table in which it occurs, for example:

```text
Column: CREATED_BY
Tables: ORG_COMPANY, ORG_LOCATION, ...
```

Store the catalog as derived evidence in the ER Knowledge Base while preserving
the original DBML as the source of truth. Generation must be deterministic and
must read table and column names from the source; it must not encode known test
answers or manually maintained table lists.

This option keeps the existing Knowledge Retrieval node and allows one retrieved
catalog parent to provide the complete list without raising Top K to the number
of schema tables.

## Stronger fallback: tenant-scoped structured schema lookup

If requirements expand to exact counts, broad schema inventory, dependency
queries, or guaranteed exhaustive results, parse the DBML into an AW5-owned
structured index such as:

```text
schema_columns
- aw5_tenant_id
- table_name
- column_name
- data_type
- definition
- source_document
- source_sha256
```

Expose narrow, read-only operations rather than unrestricted model-generated SQL:

```text
lookup_tables_by_column(column_name)
lookup_columns_by_table(table_name)
lookup_relationships(table_name)
```

The trusted backend must derive `aw5_tenant_id` from authenticated project
membership. User text, model output, and client-supplied identifiers must not
select another project tenant. Parameterized queries must return source
provenance with their results.

A future workflow may route exhaustive schema intent to this lookup and use the
existing Knowledge Retrieval path for semantic evidence. Such routing must be by
query capability, not by hard-gating TOR, SDS, or ER files. Mixed questions may
combine structured results with evidence from the one authorized-corpus
Knowledge Retrieval node.

## Deferred alternatives

- Raising Top K above the number of schema tables can work for this small corpus,
  but increases reranker input, answer context, latency, and cost and still needs
  completeness testing.
- One-table-per-document metadata can narrow named-table searches but is not an
  efficient exhaustive aggregation mechanism.
- Neo4j is unnecessary for the current column lookup case. Consider a graph store
  only if multi-hop relationship queries become an explicit requirement and a
  simpler relational representation proves insufficient.

## Required evidence before adoption

Any activated candidate must be compared with the unchanged parent-child control
using the same corpus, model providers, retrieval settings, and questions. Record:

- completeness and correctness of returned tables;
- citation and source-provenance accuracy;
- end-to-end and node latency, including p50 and p95 across repeated runs;
- reranker and answer-model tokens and estimated cost;
- provider errors, timeouts, and retry behavior;
- tenant isolation using a conflicting synthetic second-tenant fixture.

Only promote a more complex path when it satisfies the explicit requirement and
its measured benefit justifies the additional operational complexity.

## Work explicitly not authorized by this note

This note does not authorize changing the live Dify workflow, reindexing the ER
Knowledge Base, adding infrastructure or plugins, running an evaluation, editing
the canonical DBML, publishing an app, or promoting a new workflow snapshot.
