-- Bronze view: one row per issue_labels record per page file, with run lineage.
-- Reads from linear_bronze.issue_labels_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.issue_labels` AS
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
  JSON_VALUE(n, '$.description') AS description,
  JSON_VALUE(n, '$.color') AS color,
  SAFE_CAST(JSON_VALUE(n, '$.isGroup') AS BOOL) AS is_group,
  JSON_VALUE(n, '$.team.id') AS team_id,
  JSON_VALUE(n, '$.parent.id') AS parent_id,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.retiredAt')) AS retired_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.lastAppliedAt')) AS last_applied_at,

  n AS raw_json
FROM `linear_bronze.issue_labels_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
