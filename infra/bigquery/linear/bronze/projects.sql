-- Bronze view: one row per projects record per page file, with run lineage.
-- Reads from linear_bronze.projects_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.projects` AS
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
  JSON_VALUE(n, '$.slugId') AS slug_id,
  JSON_VALUE(n, '$.icon') AS icon,
  JSON_VALUE(n, '$.color') AS color,
  JSON_VALUE(n, '$.state') AS state,
  JSON_VALUE(n, '$.health') AS health,
  SAFE_CAST(JSON_VALUE(n, '$.priority') AS INT64) AS priority,
  SAFE_CAST(JSON_VALUE(n, '$.sortOrder') AS FLOAT64) AS sort_order,
  SAFE_CAST(JSON_VALUE(n, '$.progress') AS FLOAT64) AS progress,
  SAFE.PARSE_DATE('%Y-%m-%d', JSON_VALUE(n, '$.startDate')) AS start_date,
  SAFE.PARSE_DATE('%Y-%m-%d', JSON_VALUE(n, '$.targetDate')) AS target_date,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.startedAt')) AS started_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.completedAt')) AS completed_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.canceledAt')) AS canceled_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  SAFE_CAST(JSON_VALUE(n, '$.trashed') AS BOOL) AS trashed,
  JSON_VALUE(n, '$.lead.id') AS lead_id,
  JSON_VALUE(n, '$.creator.id') AS creator_id,

  n AS raw_json
FROM `linear_bronze.projects_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
