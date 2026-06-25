-- Users re-opening the same file (content fingerprint) multiple times.
CREATE OR REPLACE VIEW `eml_viewer_gold.gold_repeat_file_opens` AS
SELECT
  user_email,
  JSON_VALUE(properties, '$.content_fingerprint') AS content_fingerprint,
  COUNT(*) AS open_count,
  MIN(ts) AS first_opened_at,
  MAX(ts) AS last_opened_at
FROM `eml_viewer_bronze.events`
WHERE event = 'import_succeeded'
  AND JSON_VALUE(properties, '$.content_fingerprint') IS NOT NULL
GROUP BY user_email, content_fingerprint
HAVING open_count >= 2;
