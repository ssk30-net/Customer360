# Architecture notes

## Why Bronze → Silver → Gold?

This is the Medallion Architecture — the standard pattern used in
enterprise lakehouses (Databricks, Microsoft Fabric, AWS Lake Formation).

- **Bronze** — raw data, append-only, never modified. Full audit trail.
- **Silver** — cleaned, type-cast, deduplicated, joined. Trusted data.
- **Gold** — aggregated business metrics. What dashboards read from.

## Why synthetic data on a schedule?

In production, data arrives continuously from source systems.
A scheduled generator simulates this — on every 6-hour run,
new rows are appended to Bronze tables, which then flow through
Silver and Gold automatically.

This means your dataset grows over time, your metrics change,
and your dashboard reflects a living system — not a static snapshot.

## Databricks Free Edition limits (relevant ones)

| Feature              | Free Edition limit         |
|----------------------|----------------------------|
| Compute              | Serverless only (no custom clusters) |
| SQL warehouse        | One, size 2X-Small         |
| Scheduled jobs       | Max 5 concurrent tasks     |
| Notebooks            | Unlimited                  |
| Delta Lake storage   | Included                   |

All four notebooks + the dashboard fit within these limits.
