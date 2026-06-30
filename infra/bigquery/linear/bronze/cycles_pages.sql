-- Bronze external table: one row per GCS page file for cycles.
-- Source: gs://peq-tools-linear-data/bronze/{backfill|daily}/{run_id}/cycles/page_*.json
-- Each file is one compact JSON line: { "meta": {...}, "nodes": [ ... ] }.
-- BigQuery JSON external tables require one complete JSON object per line (not pretty-printed).
-- Query flattened rows via linear_bronze.cycles (view).
--
-- BigQuery allows only one wildcard per URI, in the last path segment — so URIs are
-- discovered from GCS at apply time (one URI per run folder). Do not apply this file
-- directly; use: make apply-bq-linear-bronze ENTITY=cycles
CREATE OR REPLACE EXTERNAL TABLE `linear_bronze.cycles_pages` (
  meta STRUCT<
    run_id STRING,
    entity STRING,
    mode STRING,
    page INT64,
    since STRING,
    extracted_at STRING,
    record_count INT64
  >,
  nodes ARRAY<JSON>
)
OPTIONS (
  format = 'JSON',
  uris = [__GCS_URIS__]
);
