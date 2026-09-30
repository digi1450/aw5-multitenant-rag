-- Run once in the Dify database as its administrator. Grant SELECT on this
-- projection only to a dedicated AW5 sync reader; never grant base-table access.
CREATE OR REPLACE VIEW aw5_published_retrieval_v1 AS
SELECT a.id AS app_id,
       w.id AS workflow_id,
       COALESCE((
           SELECT jsonb_agg(DISTINCT dataset_id.value)
           FROM jsonb_array_elements(w.graph::jsonb -> 'nodes') AS node
           CROSS JOIN LATERAL jsonb_array_elements_text(
               node -> 'data' -> 'dataset_ids'
           ) AS dataset_id(value)
           WHERE node -> 'data' ->> 'type' = 'knowledge-retrieval'
       ), '[]'::jsonb) AS dataset_ids
FROM apps AS a
JOIN workflows AS w ON w.id = a.workflow_id AND w.app_id = a.id;

-- Provision a LOGIN role with a private password, then grant only:
-- GRANT USAGE ON SCHEMA public TO aw5_sync_reader;
-- GRANT SELECT ON aw5_published_retrieval_v1 TO aw5_sync_reader;
