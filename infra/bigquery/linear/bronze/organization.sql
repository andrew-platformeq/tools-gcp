-- Bronze view: one row per organization record per page file, with run lineage.
-- Reads from linear_bronze.organization_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.organization` AS
SELECT
  p.meta.run_id,
  p.meta.mode,
  p.meta.page,
  p.meta.since,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', p.meta.extracted_at) AS extracted_at,

  REGEXP_EXTRACT(_FILE_NAME, r'bronze/([^/]+/[^/]+)/') AS run_prefix,
  _FILE_NAME AS source_uri,

  JSON_VALUE(n, '$.id') AS id,
  JSON_VALUE(n, '$.name') AS name,
  JSON_VALUE(n, '$.urlKey') AS url_key,
  SAFE_CAST(JSON_VALUE(n, '$.userCount') AS INT64) AS user_count,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,

  n AS raw_json
FROM `linear_bronze.organization_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
