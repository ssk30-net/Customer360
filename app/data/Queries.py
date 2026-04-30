# ============================================================
# FILE    : data/queries.py
# PURPOSE : All SQL queries against Gold schema
#           Single source of truth for every data fetch in app
# CONNECTION: Databricks Apps built-in auth — no credentials
#             needed. Uses DATABRICKS_HOST env var injected
#             automatically by the Apps runtime.
# ============================================================

import os
import pandas as pd
from databricks import sql
from functools import lru_cache

# ── Connection factory ────────────────────────────────────────
# Databricks Apps injects DATABRICKS_HOST automatically.
# DATABRICKS_HTTP_PATH must be set in app.yaml env section —
# copy it from SQL Warehouse → Connection details → HTTP Path.

def get_connection():
    """
    Returns a Databricks SQL connection using Apps built-in auth.
    No token or password needed — handled by the Apps runtime.
    """
    return sql.connect(
        server_hostname = os.environ["DATABRICKS_HOST"],
        http_path       = os.environ["DATABRICKS_HTTP_PATH"],
        auth_type       = "databricks-oauth",   # Apps native auth
    )


def run_query(sql_str: str) -> pd.DataFrame:
    """Execute a SQL string and return a pandas DataFrame."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_str)
            cols = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=cols)


# ── KPI queries (Page 1) ──────────────────────────────────────

def get_kpi_summary() -> pd.DataFrame:
    """
    Single-row summary for the 4 KPI cards on the dashboard.
    Returns: total_customers, total_revenue, churned_customers,
             churn_rate, avg_engagement, avg_support_health
    """
    return run_query("""
        SELECT
            COUNT(*)                                        AS total_customers,
            ROUND(SUM(total_spend), 0)                      AS total_revenue,
            SUM(churn_flag)                                 AS churned_customers,
            ROUND(SUM(churn_flag) * 100.0 / COUNT(*), 1)   AS churn_rate,
            ROUND(AVG(engagement_score), 1)                 AS avg_engagement,
            ROUND(AVG(support_health_score), 1)             AS avg_support_health,
            COUNT(CASE WHEN txn_count = 0 THEN 1 END)       AS never_transacted
        FROM customer360_gold.gold_fact_customer_metrics
    """)


def get_revenue_by_tier() -> pd.DataFrame:
    """
    Revenue, customer count and churn rate per tier.
    Used for bar chart on dashboard.
    """
    return run_query("""
        SELECT
            t.tier_name,
            t.priority_rank,
            COUNT(f.customer_key)               AS customer_count,
            ROUND(SUM(f.total_spend), 0)        AS total_revenue,
            ROUND(AVG(f.rfm_score), 1)          AS avg_rfm,
            SUM(f.churn_flag)                   AS churned,
            ROUND(SUM(f.churn_flag) * 100.0
                  / COUNT(*), 1)                AS churn_rate_pct
        FROM customer360_gold.gold_fact_customer_metrics f
        JOIN customer360_gold.gold_dim_tier t
          ON f.tier_key = t.tier_key
        GROUP BY t.tier_name, t.priority_rank
        ORDER BY t.priority_rank
    """)


def get_segment_distribution() -> pd.DataFrame:
    """
    Customer count and revenue per segment.
    Used for donut chart on dashboard.
    """
    return run_query("""
        SELECT
            s.segment_name,
            COUNT(f.customer_key)           AS customer_count,
            ROUND(SUM(f.total_spend), 0)    AS total_revenue
        FROM customer360_gold.gold_fact_customer_metrics f
        JOIN customer360_gold.gold_dim_segment s
          ON f.segment_key = s.segment_key
        GROUP BY s.segment_name
        ORDER BY total_revenue DESC
    """)


def get_churn_risk_table(limit: int = 25) -> pd.DataFrame:
    """
    Top churned customers with spend history — for churn table.
    Ordered by LTV descending so highest-value at-risk customers
    appear first — most actionable for retention team.
    """
    return run_query(f"""
        SELECT
            c.name,
            c.city,
            c.city_tier,
            s.segment_name                          AS segment,
            t.tier_name                             AS tier,
            ROUND(f.total_spend, 0)                 AS lifetime_value,
            f.txn_count,
            f.recency_days,
            f.churn_reason,
            ROUND(f.engagement_score, 1)            AS engagement_score,
            f.ticket_count,
            t.retention_strategy,
            f.customer_key
        FROM customer360_gold.gold_fact_customer_metrics  f
        JOIN customer360_gold.gold_dim_customer           c ON f.customer_key = c.customer_key
        JOIN customer360_gold.gold_dim_segment            s ON f.segment_key  = s.segment_key
        JOIN customer360_gold.gold_dim_tier               t ON f.tier_key     = t.tier_key
        WHERE f.churn_flag = 1
          AND f.txn_count  > 0
        ORDER BY f.total_spend DESC
        LIMIT {limit}
    """)


def get_revenue_trend() -> pd.DataFrame:
    """
    Quarterly revenue trend — for line chart on dashboard.
    Reads from Silver fact_transactions for transaction-level detail.
    """
    return run_query("""
        SELECT
            d.fiscal_quarter_label,
            d.year,
            d.quarter,
            COUNT(ft.transaction_key)       AS txn_count,
            ROUND(SUM(ft.net_amount), 0)    AS net_revenue,
            COUNT(DISTINCT ft.customer_key) AS unique_customers
        FROM customer360_silver.fact_transactions ft
        JOIN customer360_gold.gold_dim_date d
          ON ft.date_key = d.date_key
        GROUP BY d.fiscal_quarter_label, d.year, d.quarter
        ORDER BY d.year, d.quarter
    """)


# ── Customer detail queries (Page 2) ─────────────────────────

def search_customers(query: str, limit: int = 10) -> pd.DataFrame:
    """
    Search customers by name, email, or user_id.
    Returns a list of matches for the search results dropdown.
    """
    q = query.replace("'", "''")    # basic SQL injection guard
    return run_query(f"""
        SELECT
            f.customer_key,
            c.user_id,
            c.name,
            c.email,
            c.city,
            c.segment,
            t.tier_name             AS tier,
            ROUND(f.total_spend, 0) AS lifetime_value,
            f.churn_flag,
            f.churn_reason
        FROM customer360_gold.gold_fact_customer_metrics  f
        JOIN customer360_gold.gold_dim_customer           c ON f.customer_key = c.customer_key
        JOIN customer360_gold.gold_dim_tier               t ON f.tier_key     = t.tier_key
        WHERE LOWER(c.name)    LIKE LOWER('%{q}%')
           OR LOWER(c.email)   LIKE LOWER('%{q}%')
           OR LOWER(c.user_id) LIKE LOWER('%{q}%')
        ORDER BY f.total_spend DESC
        LIMIT {limit}
    """)


def get_customer_profile(customer_key: str) -> pd.DataFrame:
    """
    Full metrics row for one customer — all 38 columns.
    Used to populate the customer detail page.
    """
    ck = customer_key.replace("'", "''")
    return run_query(f"""
        SELECT
            f.*,
            c.name, c.user_id, c.age, c.gender,
            c.city, c.state, c.city_tier, c.email,
            c.signup_date, c.customer_age_days,
            s.segment_name, s.target_channel,
            t.tier_name, t.retention_strategy
        FROM customer360_gold.gold_fact_customer_metrics  f
        JOIN customer360_gold.gold_dim_customer           c ON f.customer_key = c.customer_key
        JOIN customer360_gold.gold_dim_segment            s ON f.segment_key  = s.segment_key
        JOIN customer360_gold.gold_dim_tier               t ON f.tier_key     = t.tier_key
        WHERE f.customer_key = '{ck}'
    """)


def get_customer_transactions(customer_key: str, limit: int = 10) -> pd.DataFrame:
    """
    Recent transactions for one customer — for activity timeline.
    """
    ck = customer_key.replace("'", "''")
    return run_query(f"""
        SELECT
            ft.date_key,
            ROUND(ft.gross_amount, 0)   AS amount,
            ft.net_amount,
            ft.status,
            ft.category,
            ft.platform,
            p.method_name               AS payment_method,
            ft.discount_pct
        FROM customer360_silver.fact_transactions   ft
        JOIN customer360_silver.dim_payment_method  p
          ON ft.payment_key = p.payment_key
        WHERE ft.customer_key = '{ck}'
        ORDER BY ft.date_key DESC
        LIMIT {limit}
    """)


def get_customer_tickets(customer_key: str, limit: int = 10) -> pd.DataFrame:
    """
    Recent support tickets for one customer — for activity timeline.
    """
    ck = customer_key.replace("'", "''")
    return run_query(f"""
        SELECT
            date_key,
            issue_type,
            priority,
            status,
            resolution_hours,
            satisfaction_score
        FROM customer360_silver.fact_support
        WHERE customer_key = '{ck}'
        ORDER BY date_key DESC
        LIMIT {limit}
    """)


def get_customer_sessions(customer_key: str, limit: int = 10) -> pd.DataFrame:
    """
    Recent app sessions for one customer — for activity timeline.
    """
    ck = customer_key.replace("'", "''")
    return run_query(f"""
        SELECT
            date_key,
            ROUND(session_duration_mins, 1) AS duration_mins,
            pages_visited,
            actions_taken,
            device_type,
            platform,
            is_bounce
        FROM customer360_silver.fact_sessions
        WHERE customer_key = '{ck}'
        ORDER BY date_key DESC
        LIMIT {limit}
    """)