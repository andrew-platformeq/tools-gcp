-- Bronze view: one row per cycles record per page file, with run lineage.
-- Reads from linear_bronze.cycles_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.cycles` AS
SELECT
  p.meta.run_id,
  p.meta.mode,
  p.meta.page,
  p.meta.since,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', p.meta.extracted_at) AS extracted_at,

  REGEXP_EXTRACT(_FILE_NAME, r'bronze/([^/]+/[^/]+)/') AS run_prefix,
  _FILE_NAME AS source_uri,

  JSON_VALUE(n, '$.id') AS id,
  SAFE_CAST(JSON_VALUE(n, '$.number') AS INT64) AS number,
  JSON_VALUE(n, '$.name') AS name,
  JSON_VALUE(n, '$.description') AS description,
  SAFE_CAST(JSON_VALUE(n, '$.isActive') AS BOOL) AS is_active,
  SAFE_CAST(JSON_VALUE(n, '$.isFuture') AS BOOL) AS is_future,
  SAFE_CAST(JSON_VALUE(n, '$.isPast') AS BOOL) AS is_past,
  SAFE_CAST(JSON_VALUE(n, '$.isNext') AS BOOL) AS is_next,
  SAFE_CAST(JSON_VALUE(n, '$.isPrevious') AS BOOL) AS is_previous,
  SAFE_CAST(JSON_VALUE(n, '$.progress') AS FLOAT64) AS progress,
  SAFE_CAST(JSON_VALUE(n, '$.currentProgress') AS FLOAT64) AS current_progress,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.startsAt')) AS starts_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.endsAt')) AS ends_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.completedAt')) AS completed_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  JSON_VALUE(n, '$.team.id') AS team_id,

  n AS raw_json
FROM `linear_bronze.cycles_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
