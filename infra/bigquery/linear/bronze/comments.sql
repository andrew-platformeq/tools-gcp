-- Bronze view: one row per comments record per page file, with run lineage.
-- Reads from linear_bronze.comments_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.comments` AS
SELECT
  p.meta.run_id,
  p.meta.mode,
  p.meta.page,
  p.meta.since,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', p.meta.extracted_at) AS extracted_at,

  REGEXP_EXTRACT(_FILE_NAME, r'bronze/([^/]+/[^/]+)/') AS run_prefix,
  _FILE_NAME AS source_uri,

  JSON_VALUE(n, '$.id') AS id,
  JSON_VALUE(n, '$.body') AS body,
  JSON_QUERY(n, '$.bodyData') AS body_data_json,
  JSON_VALUE(n, '$.issueId') AS issue_id,
  JSON_VALUE(n, '$.projectId') AS project_id,
  JSON_VALUE(n, '$.parentId') AS parent_id,
  JSON_VALUE(n, '$.resolvingCommentId') AS resolving_comment_id,
  JSON_VALUE(n, '$.url') AS url,
  SAFE_CAST(JSON_VALUE(n, '$.isArtificialAgentSessionRoot') AS BOOL) AS is_artificial_agent_session_root,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.editedAt')) AS edited_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.resolvedAt')) AS resolved_at,
  JSON_VALUE(n, '$.user.id') AS user_id,

  n AS raw_json
FROM `linear_bronze.comments_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
