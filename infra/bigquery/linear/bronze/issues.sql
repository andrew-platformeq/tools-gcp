-- Bronze view: one row per issue per page file, with run lineage.
-- Reads from linear_bronze.issues_pages (GCS external table).
CREATE OR REPLACE VIEW `linear_bronze.issues` AS
SELECT
  p.meta.run_id,
  p.meta.mode,
  p.meta.page,
  p.meta.since,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', p.meta.extracted_at) AS extracted_at,

  REGEXP_EXTRACT(_FILE_NAME, r'bronze/([^/]+/[^/]+)/') AS run_prefix,
  _FILE_NAME AS source_uri,

  JSON_VALUE(n, '$.id') AS id,
  JSON_VALUE(n, '$.identifier') AS identifier,
  SAFE_CAST(JSON_VALUE(n, '$.number') AS INT64) AS number,
  JSON_VALUE(n, '$.title') AS title,
  JSON_VALUE(n, '$.description') AS description,
  JSON_VALUE(n, '$.url') AS url,
  JSON_VALUE(n, '$.branchName') AS branch_name,
  SAFE_CAST(JSON_VALUE(n, '$.priority') AS INT64) AS priority,
  SAFE_CAST(JSON_VALUE(n, '$.estimate') AS FLOAT64) AS estimate,
  SAFE_CAST(JSON_VALUE(n, '$.sortOrder') AS FLOAT64) AS sort_order,
  JSON_QUERY(n, '$.labelIds') AS label_ids_json,
  SAFE_CAST(JSON_VALUE(n, '$.trashed') AS BOOL) AS trashed,

  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.createdAt')) AS created_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.updatedAt')) AS updated_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.archivedAt')) AS archived_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.startedAt')) AS started_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.completedAt')) AS completed_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.canceledAt')) AS canceled_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.snoozedUntilAt')) AS snoozed_until_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.dueDate')) AS due_date,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.addedToProjectAt')) AS added_to_project_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.addedToCycleAt')) AS added_to_cycle_at,
  SAFE.PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%E*S%Ez', JSON_VALUE(n, '$.addedToTeamAt')) AS added_to_team_at,

  JSON_VALUE(n, '$.team.id') AS team_id,
  JSON_VALUE(n, '$.state.id') AS state_id,
  JSON_VALUE(n, '$.assignee.id') AS assignee_id,
  JSON_VALUE(n, '$.creator.id') AS creator_id,
  JSON_VALUE(n, '$.delegate.id') AS delegate_id,
  JSON_VALUE(n, '$.project.id') AS project_id,
  JSON_VALUE(n, '$.cycle.id') AS cycle_id,
  JSON_VALUE(n, '$.parent.id') AS parent_id,
  JSON_VALUE(n, '$.projectMilestone.id') AS project_milestone_id,

  n AS raw_json
FROM `linear_bronze.issues_pages` AS p
CROSS JOIN UNNEST(p.nodes) AS n;
