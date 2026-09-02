# AW5 RAG Lean Adaptive v1.4 Candidate

> **Historical experiment, not the current workflow or next task.** Status and
> proposed checks below are preserved as dated records. Follow [CURRENT.md](CURRENT.md)
> for the owner-confirmed AW5-RAG 1.2 snapshot and current target direction. The
> candidate YAML and rebuild scripts described here remain separate local artifacts;
> they are not included in this documentation/current-snapshot commit.

## Purpose

This candidate moves the deterministic source-boundary normalization into the
existing `Route Queries` node. It is built directly from v1, the last candidate
that returned message-level citations.

The graph remains 16 nodes and 18 edges. `Merge Context`, all graph edges, both LLM
nodes, the conditional repair path, and the final response path are unchanged from
v1. Only `Route Queries` receives the current question and normalizes the source
flags before downstream retrieval and Merge.

All three retrieval queries remain populated because the current graph executes
all three retrieval nodes. The normalized `use_tor`, `use_sds`, and `use_er` flags
control which evidence enters `Merge Context`.

## Why v1.4 follows v1.3

The live v1.3 `ER-01` run returned all six required identifiers and Merge contained
six `ER_dbdiagram.txt` chunks with intact citation metadata, but Dify again emitted
zero `retriever_resources`. Exact comparison showed that v1.3 differed from v1 only
inside Merge Context: it accepted `sys.query` and applied the filter there.

v1.4 therefore restores Merge Context and the graph edges exactly to v1 and applies
the correction at the existing route-normalization boundary instead.

## Local validation

- all code-node Python compiled;
- all selectors resolve;
- ER-only and explicit cross-source route fixtures passed;
- graph edges exactly equal v1;
- Merge Context data exactly equals v1.

## Artifact

- DSL: `aw5-rag-lean-adaptive-v1.4-candidate-2026-08-29.yml`
- SHA-256: `9d48c590a13eb0c0371845c4880c2451ee1708fa27d95ab81ef73d97c91ab7fc`
