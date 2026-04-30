# Customer 360 — Databricks Free Edition

A production-style unified customer analytics platform built on Databricks,
implementing a Bronze → Silver → Gold lakehouse architecture with a
scheduled synthetic data pipeline.

## Project status

| Step | Notebook | Status |
|------|----------|--------|
| 1 | Repo skeleton | Done |
| 2 | 01_bronze_initial_load | Pending |
| 3 | 02_incremental_generator | Pending |
| 4 | 03_silver_transform | Pending |
| 5 | 04_gold_metrics | Pending |
| 6 | SQL dashboard | Pending |

## Architecture

```
Synthetic data generator  (scheduled via Databricks Jobs)
          ↓
    Bronze layer     raw Delta tables, append-only
          ↓
    Silver layer     cleaned, joined, deduplicated
          ↓
    Gold layer       LTV, RFM scores, churn flag
          ↓
    Databricks SQL dashboard
```

## Tech stack

| Layer         | Tool                                  |
|---------------|---------------------------------------|
| Compute       | Databricks Free Edition (serverless)  |
| Storage       | Delta Lake                            |
| Transform     | Python (serverless notebooks)         |
| Orchestration | Databricks Jobs                       |
| Visualisation | Databricks SQL warehouse              |
| Version ctrl  | GitHub                                |

## How to run

1. Import notebooks from `notebooks/` into your Databricks workspace
2. Run `01_bronze_initial_load` once manually
3. Create a Databricks Job: tasks 02 → 03 → 04 in sequence
4. Schedule the job every 6 hours
5. Build the SQL dashboard from queries in `sql/dashboard_queries/`
