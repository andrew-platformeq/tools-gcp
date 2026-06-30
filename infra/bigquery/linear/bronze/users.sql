-- Bronze view: one row per users record per page file, with run lineage.
-- Reads from linear_bronze.users_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.users` AS
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
  JSON_VALUE(n, '$.displayName') AS display_name,
  JSON_VALUE(n, '$.email') AS email,
  JSON_VALUE(n, '$.avatarUrl') AS avatar_url,
  JSON_VALUE(n, '$.title') AS title,
  JSON_VALUE(n, '$.timezone') AS timezone,
  SAFE_CAST(JSON_VALUE(n, '$.active') AS BOOL) AS active,
  SAFE_CAST(JSON_VALUE(n, '$.admin') AS BOOL) AS admin,
  SAFE_CAST(JSON_VALUE(n, '$.owner') AS BOOL) AS owner,
  SAFE_CAST(JSON_VALUE(n, '$.guest') AS BOOL) AS guest,
  SAFE_CAST(JSON_VALUE(n, '$.app') AS BOOL) AS app,
  SAFE_CAST(JSON_VALUE(n, '$.isMe') AS BOOL) AS is_me,
  SAFE_CAST(JSON_VALUE(n, '$.isAssignable') AS BOOL) AS is_assignable,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.lastSeen')) AS last_seen,

  n AS raw_json
FROM `linear_bronze.users_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
