-- Distinct files vs total imports (rolling usage summary).
CREATE OR REPLACE VIEW `eml_viewer_gold.gold_unique_files_vs_imports` AS
SELECT
  DATE(ts) AS event_date,
  COUNT(*) AS total_imports,
  COUNT(DISTINCT JSON_VALUE(properties, '$.content_fingerprint')) AS unique_files
FROM `eml_viewer_bronze.events`
WHERE event = 'import_succeeded'
GROUP BY event_date;
