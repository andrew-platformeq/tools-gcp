-- Bronze view: one row per attachments record per page file, with run lineage.
-- Reads from linear_bronze.attachments_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.attachments` AS
SELECT
  p.meta.run_id,
  p.meta.mode,
  p.meta.page,
  p.meta.since,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', p.meta.extracted_at) AS extracted_at,

  REGEXP_EXTRACT(_FILE_NAME, r'bronze/([^/]+/[^/]+)/') AS run_prefix,
  _FILE_NAME AS source_uri,

  JSON_VALUE(n, '$.id') AS id,
  JSON_VALUE(n, '$.title') AS title,
  JSON_VALUE(n, '$.subtitle') AS subtitle,
  JSON_VALUE(n, '$.url') AS url,
  JSON_QUERY(n, '$.metadata') AS metadata_json,
  JSON_QUERY(n, '$.source') AS source_json,
  JSON_VALUE(n, '$.sourceType') AS source_type,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  JSON_VALUE(n, '$.issue.id') AS issue_id,
  JSON_VALUE(n, '$.creator.id') AS creator_id,

  n AS raw_json
FROM `linear_bronze.attachments_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
