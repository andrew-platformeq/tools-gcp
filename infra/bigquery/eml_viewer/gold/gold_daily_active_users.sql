-- Daily active users (distinct Chrome profile emails per calendar day).
CREATE OR REPLACE VIEW `eml_viewer_gold.gold_daily_active_users` AS
SELECT
  DATE(ts) AS event_date,
  COUNT(DISTINCT user_email) AS active_users,
  COUNT(DISTINCT install_id) AS active_installs
FROM `eml_viewer_bronze.events`
WHERE user_email IS NOT NULL
  AND user_email != 'unknown'
GROUP BY event_date;
