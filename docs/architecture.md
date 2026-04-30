# Architecture — Customer 360

## Overview

Customer 360 is a production-style unified customer analytics platform
built on Databricks Free Edition. It implements the Medallion Architecture
(Bronze → Silver → Gold), a Snowflake schema in Silver, a star schema in Gold,
a scheduled incremental data pipeline, a SQL dashboard, and a Dash web app
deployed via Databricks Apps.

---

## Pipeline flow

```
Databricks Job (every 6 hours)
        ↓
05_pipeline_orchestrator.py
        ↓ dbutils.notebook.run()
        ├── 01_bronze_initial_load.py   ← runs only if Bronze is empty
        ├── 02_incremental_generator.py ← appends new rows to Bronze
        ├── 03_silver_transform.py      ← rebuilds Silver from Bronze
        └── 04_gold_metrics.py          ← rebuilds Gold from Silver
```

---

## Layer design

### Bronze — `customer360`

Raw data. Append-only. Never modified after insert.
Every row stamped with `pipeline_run_id` for full lineage tracing.

| Table | Grain | Rows at bootstrap |
|-------|-------|------------------|
| `bronze_users` | One row per user signup | 500 |
| `bronze_transactions` | One row per transaction | 3,000 |
| `bronze_app_usage` | One row per app session | 2,500 |
| `bronze_support_tickets` | One row per support ticket | 800 |

Each pipeline run appends 5–20 users, 80–200 transactions,
50–120 sessions, and 15–40 tickets. Dataset grows automatically.

---

### Silver — `customer360_silver` (Snowflake schema)

Cleaned, type-cast, deduplicated, and joined data.
Implements a Snowflake schema with two levels of normalization:

- `dim_product → dim_category` — avoids repeating category hierarchy in every product row
- `dim_location → dim_city` — avoids repeating state and region in every location row

**7 dimension tables:**

| Table | Rows | Source |
|-------|------|--------|
| `dim_date` | 1,461 | Generated — full date spine 2023–2026 |
| `dim_city` | 10 | Hardcoded master — 10 Indian cities |
| `dim_location` | 30 | Derived — 3 pincodes per city |
| `dim_category` | 7 | Hardcoded master — 7 product categories |
| `dim_product` | ~varies | Distinct product_ids from Bronze |
| `dim_payment_method` | 5 | Hardcoded master |
| `dim_customer` | ~varies | Deduped from bronze_users |

**3 fact tables:**

| Table | Grain | Key joins |
|-------|-------|-----------|
| `fact_transactions` | One row per transaction | customer, product, date, location, payment |
| `fact_sessions` | One row per app session | customer, date, location |
| `fact_support` | One row per support ticket | customer, date |

---

### Gold — `customer360_gold` (Star schema)

Business metrics aggregated to one row per customer.
Star schema optimised for Power BI — 4 dimensions, 1 fact.

**4 dimension tables:**

| Table | Rows | Purpose |
|-------|------|---------|
| `gold_dim_customer` | ~varies | Identity + geography (city, state, tier) |
| `gold_dim_date` | 1,461 | Date spine — reused from Silver |
| `gold_dim_segment` | 4 | Segment master with marketing channel |
| `gold_dim_tier` | 5 | Tier master with retention strategy |

**1 fact table:**

`gold_fact_customer_metrics` — 38 columns, one row per customer.

Metrics computed:

| Metric group | Columns |
|-------------|---------|
| Transaction | `total_spend`, `txn_count`, `avg_order_value`, `failure_rate` |
| Recency | `recency_days` — recomputed against `current_date()` every run |
| RFM | `r_score`, `f_score`, `m_score`, `rfm_score` (3–15) |
| Engagement | `session_count`, `avg_session_mins`, `engagement_score` (0–100) |
| Support | `ticket_count`, `open_tickets`, `support_health_score` (0–100) |
| Churn | `churn_flag`, `churn_reason` |
| Tier | `customer_tier` — Champions / Loyal / Potential / At Risk / Dormant |

**Power BI relationships (draw in Model view):**

```
gold_fact_customer_metrics.customer_key   → gold_dim_customer.customer_key  (many-to-one)
gold_fact_customer_metrics.segment_key    → gold_dim_segment.segment_key    (many-to-one)
gold_fact_customer_metrics.tier_key       → gold_dim_tier.tier_key          (many-to-one)
gold_fact_customer_metrics.first_txn_date → gold_dim_date.date_key          (many-to-one)
```

---

## Databricks App

A two-page Dash (Plotly) app deployed via Databricks Apps.
Connects to Gold schema via `databricks-sql-connector` using
built-in Apps OAuth — no credentials required.

| Page | Route | Content |
|------|-------|---------|
| Dashboard | `/` | KPI cards, revenue by tier, segment donut, revenue trend, churn risk table |
| Customer detail | `/customer` | Search bar, profile card, metric grid, RFM gauges, engagement radar, activity timeline |

**App file structure:**
```
app/
├── app.py                  Dash entry point + navbar + page router
├── app.yaml                Databricks Apps deployment config
├── requirements.txt        Python dependencies
├── data/queries.py         All SQL queries (single source of truth)
├── components/kpi_cards.py Reusable KPI card components
├── components/charts.py    Reusable Plotly chart functions
├── pages/dashboard.py      Page 1 — executive dashboard
└── pages/customer_detail.py Page 2 — customer 360 detail view
```

---

## SQL dashboard

5 queries in Databricks SQL warehouse against `customer360_gold`:

| File | Visual | What it shows |
|------|--------|--------------|
| `01_top_customers_by_ltv.sql` | Horizontal bar | Top 20 customers by lifetime value |
| `02_churn_risk_analysis.sql` | Table | Churned customers + recommended action |
| `03_revenue_by_segment_and_tier.sql` | Grouped bar + pie | Revenue breakdown with churn rate |
| `04_revenue_trend_by_quarter.sql` | Line chart | Quarterly revenue + transaction volume |
| `05_engagement_by_city_and_platform.sql` | Stacked bar | Engagement by city tier and platform |

---

## Tech stack

| Layer | Tool | Free tier |
|-------|------|-----------|
| Compute | Databricks Free Edition (serverless) | ✓ |
| Storage | Delta Lake (Unity Catalog) | ✓ |
| Transform | Python serverless notebooks | ✓ |
| Orchestration | Databricks Jobs (max 5 tasks) | ✓ |
| SQL + viz | Databricks SQL warehouse | ✓ |
| App | Databricks Apps — Dash (Plotly) | ✓ |
| Version control | GitHub | ✓ |

---

## Databricks Free Edition limits

| Feature | Limit | Impact on project |
|---------|-------|------------------|
| Compute | Serverless only | All notebooks use serverless — no issue |
| SQL warehouse | One, 2X-Small | Sufficient for dashboard and app queries |
| Scheduled jobs | Max 5 concurrent tasks | Pipeline uses 1 task — well within limit |
| Notebooks | Unlimited | No impact |
| Delta Lake storage | Included | No impact |

---

## Why this design

**Snowflake in Silver, star in Gold** — Silver normalizes to reduce redundancy
and maintain referential integrity. Gold denormalizes into a star schema because
Power BI and Databricks SQL perform best with flat, pre-joined dimensions.

**Synthetic incremental data** — in production, data arrives from source systems
continuously. The scheduled generator simulates this so the dataset grows
realistically over time, recency metrics stay meaningful, and churn flags
update automatically on every run without any manual intervention.

**`pipeline_run_id` on every row** — every row across all 19 tables carries
the ID of the run that created it. This enables instant data quality auditing:
if a bad run produces anomalous data, you can identify and delete exactly
those rows without touching anything else.