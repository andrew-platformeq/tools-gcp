-- Pipeline run-history audit table.
-- External table over the append-only NDJSON the ingest job writes to
-- gs://<bucket>/audit/run_history/<run_id>.json (one record per run). No load step needed;
-- each run's file is picked up automatically. Answers "did the pipeline run, when, and
-- correctly?" — distinct from bronze, which only records "what the source said".
--
-- Apply once (datasets are created by Terraform):
--   bq query --use_legacy_sql=false < infra/bigquery/linear/audit/run_history.sql
CREATE OR REPLACE EXTERNAL TABLE `linear_bronze.run_history` (
  run_id STRING,
  mode STRING,
  dry_run BOOL,
  status STRING,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  run_prefix STRING,
  code_version STRING,        -- image build (TOOLS_IMAGE_VERSION); null on local runs
  total_records INT64,
  entity_failures INT64,
  entities ARRAY<STRUCT<
    entity STRING,
    status STRING,
    records INT64,
    since STRING,             -- watermark inputs/outputs kept as raw strings (may be EPOCH/null)
    new_watermark STRING,
    error STRING
  >>
)
OPTIONS (
  format = 'NEWLINE_DELIMITED_JSON',
  uris = ['gs://peq-tools-linear-data/audit/run_history/*.json']
);
