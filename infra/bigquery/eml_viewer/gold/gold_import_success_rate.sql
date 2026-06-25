-- Import success rate from coarse import lifecycle events.
CREATE OR REPLACE VIEW `eml_viewer_gold.gold_import_success_rate` AS
SELECT
  DATE(ts) AS event_date,
  COUNTIF(event = 'import_succeeded') AS imports_succeeded,
  COUNTIF(event = 'import_failed') AS imports_failed,
  COUNTIF(event = 'import_rejected') AS imports_rejected,
  SAFE_DIVIDE(
    COUNTIF(event = 'import_succeeded'),
    COUNTIF(event IN ('import_succeeded', 'import_failed', 'import_rejected'))
  ) AS success_rate
FROM `eml_viewer_bronze.events`
WHERE event IN ('import_succeeded', 'import_failed', 'import_rejected')
GROUP BY event_date;
