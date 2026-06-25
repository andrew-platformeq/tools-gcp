-- Drag-and-drop vs file picker usage on successful imports.
CREATE OR REPLACE VIEW `eml_viewer_gold.gold_drop_vs_picker` AS
SELECT
  DATE(ts) AS event_date,
  JSON_VALUE(properties, '$.method') AS import_method,
  COUNT(*) AS import_count
FROM `eml_viewer_bronze.events`
WHERE event = 'import_succeeded'
GROUP BY event_date, import_method;
