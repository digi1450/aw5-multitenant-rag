# AW5 RAG Lean Adaptive v1.3 Candidate

> **Historical experiment, not the current workflow or next task.** Status and
> proposed checks below are preserved as dated records. Follow [CURRENT.md](CURRENT.md)
> for the owner-confirmed AW5-RAG 1.2 snapshot and current target direction. The
> candidate YAML and rebuild scripts described here remain separate local artifacts;
> they are not included in this documentation/current-snapshot commit.

## Purpose

This candidate tests a narrower correction after v1.1 and v1.2 both returned
complete `ER-01` answers but no message-level citations.

It removes the standalone `LEAN ROUTE GUARD` node and folds the same deterministic
source-boundary policy into `Merge Context`. The retrieval fan-out and source
selectors remain rooted at `Route Queries`, matching the v1 graph that returned
citations. The candidate has 16 nodes and 18 edges, one fewer node and two fewer
edges than v1.2.

## Hypothesis under test

The v1.2 diagnostic proved that `Merge Context` contained six `ER_dbdiagram.txt`
rows with the expected Dify citation metadata, while `message_end` contained no
`retriever_resources`. This candidate tests whether removing the standalone Guard
from the Merge dependency graph restores Dify citation propagation.

This is a hypothesis, not a verified root cause. Do not promote the candidate
until a live `ER-01` run returns an ER-only citation boundary.

## Local validation

- all code-node Python compiled;
- all selectors resolve;
- retrieval fan-out remains `Route Queries -> Retrieve TOR/SDS/ER`;
- integrated ER-only Merge fixture returned only ER evidence;
- explicit TOR + SDS + ER fixture retained all three sources.

## Artifact

- DSL: `aw5-rag-lean-adaptive-v1.3-candidate-2026-08-29.yml`
- SHA-256: `ce99cb85625d98341c97f37f09fe92f15f092b6229aa048e50d3b80d26cfd53d`
