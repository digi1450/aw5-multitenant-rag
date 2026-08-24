# Current AW5-RAG Dify Draft Export

## Current snapshot

- File: `aw5-rag-source-routing-postfix-2026-08-25.yml`
- SHA-256: `081dfff6d367932ee609eb5a26a833da666fbb845dbdfb090271b9d42db9b61d`
- Exported from: Dify Cloud current saved version on 2026-08-25 at approximately 01:55 Asia/Bangkok
- Validated graph: 9 nodes / 10 edges
- Status: **current improved draft snapshot; not Published**

Use this file as the current workflow reference when reviewing, comparing, or continuing AW5-RAG work. Before claiming it still matches live Dify, verify whether the Dify draft has been edited after the export time above.

## Previous snapshots

- `aw5-rag-baseline-2026-08-25.yml` — original baseline before prompt/workflow tuning
- `aw5-rag-pre-source-routing-2026-08-25.yml` — rollback point immediately before source-specific routing changes

Do not treat either previous snapshot as the current workflow.

## Evidence and boundaries

- Before/after evaluation: `../../knowledge_base/nature_footprint/evaluation/evaluation-run-2026-08-25-representative-baseline.md`
- Representative retest: strict pass 5/5 on XDOC-02, TOR-02, SDS-01, ER-02, and EDGE-04
- Retrieval mode: Weighted Score 0.5 semantic / 0.5 keyword; TOR/SDS Top K 3; ER Top K 6; rerank disabled
- The Dify UI showed the improved workflow as Auto-Saved draft while the Published version remained older
- Full executable suite and ISO-01 are not complete; do not call the system production-ready or tenant-isolation complete
- The export and evidence files were not committed or pushed during the 2026-08-25 test run; check current git evidence before claiming repository completion
