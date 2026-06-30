# BigQuery SQL artifacts

SQL for medallion layers lives here — **not** embedded in Python. Python ingest jobs
load Bronze and execute these files via `bigquery.Client.query()`.

## Layout (per source)

```
infra/bigquery/
  <source>/                 e.g. linear, epic
    bronze/                 External tables + views over GCS JSON (Linear)
    silver/
      ddl/                  CREATE TABLE statements (applied once)
      merge/                MERGE scripts (run after each ingest)
    gold/                   CREATE VIEW statements (tool-facing contract)
```

## Naming

| Dataset (Terraform) | Contents |
|---------------------|----------|
| `<source>_bronze` | Optional staging tables for raw JSON loads |
| `<source>_silver` | Typed master tables (MERGE on `id`) |
| `<source>_gold` | Views consumed by jobs and analysts |

Example for Linear: `linear_silver.issues`, `linear_gold.gold_sweep_issues`.

## Applying SQL

Datasets are created by Terraform. Table and view DDL is applied manually or via a
script until we automate it:

```bash
# Linear bronze (GCS → BigQuery external tables + views)
make apply-bq-linear-bronze-all            # all entities
make apply-bq-linear-bronze ENTITY=issues  # one entity

# Future silver/gold
bq query --use_legacy_sql=false < infra/bigquery/linear/silver/ddl/issues.sql
bq query --use_legacy_sql=false < infra/bigquery/linear/gold/gold_sweep_issues.sql
```

## Cross-source views

Joins across sources (e.g. Linear + Epic) belong in a separate mart dataset
(`analytics_gold`), not inside a single source's Gold folder. See
[docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md).

## Adding a new source

1. Create `infra/bigquery/<source>/silver/ddl/`, `merge/`, and `gold/`.
2. Add matching datasets in `infra/terraform/<source>_data.tf`.
3. Document PII and access in `docs/<SOURCE>_DATA.md` when the pipeline ships.
