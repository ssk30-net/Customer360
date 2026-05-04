# Customer 360 — Databricks Free Edition

A production-style unified customer analytics platform built on Databricks,
implementing a Bronze → Silver → Gold lakehouse architecture with a scheduled
synthetic data pipeline, a Snowflake schema in Silver, a star schema in Gold,
and a Dash web app deployed via Databricks Apps.

---

## Project status

| Step | Deliverable | Status |
|------|-------------|--------|
| 1 | GitHub repo + project skeleton | ✅ Done |
| 2 | Notebook 01 — Bronze initial load | ✅ Done |
| 3 | Notebook 02 — Incremental generator | ✅ Done |
| 4 | Notebook 03 — Silver transform (Snowflake schema) | ✅ Done |
| 5 | Notebook 04 — Gold metrics (star schema) | ✅ Done |
| 6 | Notebook 05 — Pipeline orchestrator + 6hr schedule | ✅ Done |
| 7 | SQL dashboard queries (5 queries) | ✅ Done |
| 8 | Schema SQL — Bronze, Silver, Gold | ✅ Done |
| 9 | Databricks App — Dash (dashboard + customer detail) | ✅ Done |
| 10 | Data dictionary | ✅ Done |

---

## Architecture

```
Notebook 05 — pipeline orchestrator  (Databricks Job · every 6 hours)
        ↓ calls
Notebook 02 — incremental generator
        ↓ appends to
customer360 (Bronze)
  bronze_users · bronze_transactions · bronze_app_usage · bronze_support_tickets
        ↓
Notebook 03 — silver transform
        ↓ writes
customer360_silver (Snowflake schema)
  dim_date · dim_city · dim_location · dim_category
  dim_product · dim_payment_method · dim_customer
  fact_transactions · fact_sessions · fact_support
        ↓
Notebook 04 — gold metrics
        ↓ writes
customer360_gold (Star schema — Power BI ready)
  gold_dim_customer · gold_dim_date · gold_dim_segment
  gold_dim_tier · gold_fact_customer_metrics
        ↓
Databricks SQL dashboard        Databricks App (Dash)
```

---

## Tech stack

| Layer | Tool | Cost |
|-------|------|------|
| Compute | Databricks Free Edition (serverless) | Free |
| Storage | Delta Lake (Unity Catalog) | Free |
| Transform | Python notebooks (serverless) | Free |
| Orchestration | Databricks Jobs | Free |
| SQL + Viz | Databricks SQL warehouse | Free |
| App | Databricks Apps — Dash (Plotly) | Free |
| Version control | GitHub | Free |

---

## Repository structure

```
customer360/
├── README.md
├── .gitignore
├── requirements.txt
├── job_config.json
│
├── notebooks/
│   ├── 01_bronze_initial_load.py       Run once — bootstraps Bronze
│   ├── 02_incremental_generator.py     Appends rows — called by orchestrator
│   ├── 03_silver_transform.py          Builds Silver Snowflake schema
│   ├── 04_gold_metrics.py              Builds Gold star schema
│   └── 05_pipeline_orchestrator.py     Scheduled entry point
│
├── sql/
│   ├── dashboard_queries/
│   │   ├── 01_top_customers_by_ltv.sql
│   │   ├── 02_churn_risk_analysis.sql
│   │   ├── 03_revenue_by_segment_and_tier.sql
│   │   ├── 04_revenue_trend_by_quarter.sql
│   │   └── 05_engagement_by_city_and_platform.sql
│   └── schema/
│       ├── 01_bronze_schema.sql
│       ├── 02_silver_schema.sql
│       └── 03_gold_schema.sql
│
├── app/
│   ├── app.py
│   ├── app.yaml
│   ├── requirements.txt
│   ├── data/
│   │   └── queries.py
│   ├── components/
│   │   ├── kpi_cards.py
│   │   └── charts.py
│   └── pages/
│       ├── dashboard.py
│       └── customer_detail.py
│
├── data/
│   └── sample/
│       ├── users_sample.csv
│       ├── transactions_sample.csv
│       ├── app_usage_sample.csv
│       └── support_tickets_sample.csv
│
└── docs/
    ├── architecture.md
    └── data_dictionary.md
```

---

## Data model

**Bronze** — 4 raw tables, append-only, stamped with `pipeline_run_id`.

**Silver** — Snowflake schema. 7 dimension tables + 3 fact tables.
Normalized: `dim_product → dim_category`, `dim_location → dim_city`.

**Gold** — Star schema for Power BI. 4 dimension tables + 1 fact table.
One row per customer with 38 columns covering LTV, RFM, churn, engagement,
and support health.

---

## Data growth per pipeline run

| Runs | Transactions | Sessions | Tickets | Users |
|------|-------------|----------|---------|-------|
| 0 (bootstrap) | 3,000 | 2,500 | 800 | 500 |
| 10 | ~4,400 | ~3,350 | ~1,100 | ~625 |
| 30 | ~7,200 | ~5,100 | ~1,700 | ~875 |
| 100 | ~17,000 | ~12,500 | ~4,200 | ~1,750 |

---

## Key metrics in Gold layer

| Metric | Description |
|--------|-------------|
| `total_spend` | Lifetime value — successful transactions only |
| `recency_days` | Days since last transaction — refreshed every run |
| `rfm_score` | Combined R+F+M score 3–15 |
| `customer_tier` | Champions / Loyal / Potential / At Risk / Dormant |
| `engagement_score` | 0–100 composite (sessions, actions, pages, bounce) |
| `support_health_score` | 0–100 (penalises open/critical tickets) |
| `churn_flag` | 1 if inactive 60+ days, high failure rate, or low RFM |
| `churn_reason` | Text explanation of why customer was flagged |

---
## Dashboard screenshots

### Power BI
![Executive overview](docs/powerbi_dashboard.png)
![Revenue trend](docs/powerbi_dashboard_p2.png)
![Segments](docs/powerbi_dashboard_p3.png)

### Databricks App
Live at: https://customer360-app-7474651051509396.aws.databricksapps.com
## Interview summary

> "I built a Customer 360 system on Databricks Free Edition using a Medallion
> lakehouse architecture. Bronze holds raw synthetic data generated by a
> scheduled incremental pipeline. Silver implements a Snowflake schema with
> 7 dimensions and 3 facts, including two levels of normalization. Gold
> implements a star schema optimized for Power BI with LTV, RFM scoring,
> churn detection, engagement scoring, and support health metrics.
> The system also includes a Dash web app deployed via Databricks Apps
> with an executive dashboard and a customer drill-down detail page."
