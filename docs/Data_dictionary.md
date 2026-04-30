# Data Dictionary — Customer 360

Complete column definitions for all 19 tables across Bronze, Silver, and Gold layers.

---

## Bronze layer — `customer360`

### `bronze_users`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| user_id | STRING | No | Natural key — 8-char UUID prefix | `A1B2C3D4` |
| name | STRING | Yes | Full name (Faker en_IN) | `Priya Sharma` |
| age | INT | Yes | Age at signup — range 18–65 | `32` |
| gender | STRING | Yes | Male / Female / Other | `Female` |
| signup_date | STRING | Yes | ISO date YYYY-MM-DD | `2023-06-15` |
| city | STRING | Yes | One of 10 Indian cities | `Mumbai` |
| country | STRING | Yes | Always India | `India` |
| email | STRING | Yes | Synthetic email | `priya.sharma@email.com` |
| segment | STRING | Yes | Premium / Standard / Basic / Trial | `Premium` |
| is_active | INT | Yes | 1 = active, 0 = inactive | `1` |
| pipeline_run_id | STRING | Yes | Run that created this row | `BOOTSTRAP_20240101_000000` |

### `bronze_transactions`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| transaction_id | STRING | No | PK — TXN + 8-char UUID | `TXNA1B2C3D4` |
| user_id | STRING | No | FK → bronze_users.user_id | `A1B2C3D4` |
| amount | DOUBLE | Yes | Gross amount INR — skewed 50–50,000 | `2499.50` |
| transaction_timestamp | STRING | Yes | YYYY-MM-DD HH:MM:SS UTC | `2024-03-15 14:22:10` |
| product_id | STRING | Yes | PRD + 4-digit code | `PRD4821` |
| category | STRING | Yes | Product category | `Electronics` |
| payment_method | STRING | Yes | Payment type used | `UPI` |
| city | STRING | Yes | Transaction city | `Bangalore` |
| country | STRING | Yes | Always India | `India` |
| status | STRING | Yes | success (85%) / failed (10%) / refunded (5%) | `success` |
| discount_pct | INT | Yes | 0 / 5 / 10 / 15 / 20 | `10` |
| platform | STRING | Yes | iOS / Android / Web | `Android` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

### `bronze_app_usage`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| session_id | STRING | No | PK — SES + 8-char UUID | `SESA1B2C3D4` |
| user_id | STRING | No | FK → bronze_users.user_id | `A1B2C3D4` |
| session_start | STRING | Yes | Session start YYYY-MM-DD HH:MM:SS | `2024-03-15 09:00:00` |
| session_end | STRING | Yes | Session end YYYY-MM-DD HH:MM:SS | `2024-03-15 09:24:00` |
| session_duration_mins | DOUBLE | Yes | Duration in minutes — range 1.0–90.0 | `24.0` |
| pages_visited | INT | Yes | Pages/screens visited — range 1–25 | `8` |
| actions_taken | INT | Yes | Clicks, searches, add-to-carts — range 0–15 | `5` |
| device_type | STRING | Yes | Mobile / Desktop / Tablet | `Mobile` |
| platform | STRING | Yes | iOS / Android / Web | `iOS` |
| is_bounce | INT | Yes | 1 = session under 60 seconds, 0 = normal | `0` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

### `bronze_support_tickets`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| ticket_id | STRING | No | PK — TKT + 8-char UUID | `TKTA1B2C3D4` |
| user_id | STRING | No | FK → bronze_users.user_id | `A1B2C3D4` |
| issue_type | STRING | Yes | Type of issue raised | `Payment Failure` |
| priority | STRING | Yes | Low / Medium / High / Critical | `High` |
| created_at | STRING | Yes | Ticket creation YYYY-MM-DD HH:MM:SS | `2024-03-15 10:00:00` |
| resolved_at | STRING | Yes | Resolution timestamp — NULL if open | `2024-03-16 08:30:00` |
| resolution_hours | DOUBLE | Yes | Hours to resolve — NULL if open | `22.5` |
| status | STRING | Yes | open / closed | `closed` |
| satisfaction_score | INT | Yes | Rating 1–5 after resolution — NULL if open | `4` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

---

## Silver layer — `customer360_silver`

### `dim_date`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| date_key | STRING | No | PK — ISO date string | `2024-03-15` |
| full_date | DATE | Yes | Full date as DATE type | `2024-03-15` |
| day_of_month | INT | Yes | 1–31 | `15` |
| day_of_week | INT | Yes | 1=Monday, 7=Sunday | `5` |
| day_name | STRING | Yes | Full day name | `Friday` |
| week_number | INT | Yes | ISO week number 1–53 | `11` |
| month | INT | Yes | 1–12 | `3` |
| month_name | STRING | Yes | Full month name | `March` |
| quarter | INT | Yes | 1–4 | `1` |
| quarter_label | STRING | Yes | Q1 / Q2 / Q3 / Q4 | `Q1` |
| year | INT | Yes | Calendar year | `2024` |
| fiscal_quarter_label | STRING | Yes | Year-Quarter combined | `2024-Q1` |
| is_weekend | INT | Yes | 1 = Saturday or Sunday | `0` |
| is_holiday | INT | Yes | 1 = Indian public holiday | `0` |
| is_non_working_day | INT | Yes | 1 = weekend or holiday | `0` |

### `dim_city`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| city_key | STRING | No | PK — CITY_ + 3-char prefix | `CITY_MUM` |
| city_name | STRING | Yes | Full city name | `Mumbai` |
| state | STRING | Yes | Indian state | `Maharashtra` |
| region | STRING | Yes | North / South / East / West | `West` |
| city_tier | STRING | Yes | Tier 1 / Tier 2 | `Tier 1` |

### `dim_location`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| location_key | STRING | No | PK — LOC_ + city prefix + sequence | `LOC_MUM_01` |
| city_key | STRING | Yes | FK → dim_city.city_key | `CITY_MUM` |
| city_name | STRING | Yes | Denormalised city name | `Mumbai` |
| pincode | STRING | Yes | Synthetic 6-digit pincode | `400051` |
| zone | STRING | Yes | Zone within city | `North Zone` |

### `dim_category`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| category_key | STRING | No | PK — CAT_ + 4-char prefix | `CAT_ELEC` |
| category_name | STRING | Yes | Product category | `Electronics` |
| department | STRING | Yes | Business department | `Technology` |
| super_category | STRING | Yes | Broad grouping | `Hard Goods` |

### `dim_product`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| product_key | STRING | No | PK — same as Bronze product_id | `PRD4821` |
| category_key | STRING | Yes | FK → dim_category.category_key | `CAT_ELEC` |
| category_name | STRING | Yes | Denormalised category | `Electronics` |
| brand | STRING | Yes | Brand name | `Samsung` |
| price_tier | STRING | Yes | Budget / Mid-range / Premium / Luxury | `Mid-range` |
| base_price | DOUBLE | Yes | Synthetic base price INR | `12999.00` |

### `dim_payment_method`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| payment_key | STRING | No | PK — PAY_ + method slug | `PAY_CREDIT_C` |
| method_name | STRING | Yes | Payment method name | `Credit Card` |
| provider | STRING | Yes | Payment provider | `Visa/Mastercard` |
| payment_type | STRING | Yes | Card / Digital | `Card` |
| is_digital | INT | Yes | 1 = digital, 0 = card | `0` |
| is_emi_eligible | INT | Yes | 1 = EMI available | `1` |

### `dim_customer`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| customer_key | STRING | No | PK — surrogate key CUST_ + user_id | `CUST_A1B2C3D4` |
| user_id | STRING | Yes | NK — natural key from Bronze | `A1B2C3D4` |
| name | STRING | Yes | Full name | `Priya Sharma` |
| age | INT | Yes | Age at signup | `32` |
| gender | STRING | Yes | Male / Female / Other | `Female` |
| signup_date | DATE | Yes | Account creation date | `2023-06-15` |
| customer_age_days | INT | Yes | Days since signup — refreshed each run | `285` |
| city | STRING | Yes | City at signup | `Mumbai` |
| country | STRING | Yes | Always India | `India` |
| email | STRING | Yes | Email address | `priya.sharma@email.com` |
| segment | STRING | Yes | Premium / Standard / Basic / Trial | `Premium` |
| is_active | INT | Yes | 1 = active, 0 = inactive | `1` |
| pipeline_run_id | STRING | Yes | Run that last updated this row | `20240315_142210` |

### `fact_transactions`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| transaction_key | STRING | No | PK — same as Bronze transaction_id | `TXNA1B2C3D4` |
| customer_key | STRING | Yes | FK → dim_customer.customer_key | `CUST_A1B2C3D4` |
| product_key | STRING | Yes | FK → dim_product.product_key | `PRD4821` |
| date_key | STRING | Yes | FK → dim_date.date_key | `2024-03-15` |
| location_key | STRING | Yes | FK → dim_location.location_key | `LOC_MUM_01` |
| payment_key | STRING | Yes | FK → dim_payment_method.payment_key | `PAY_UPI_____` |
| gross_amount | DOUBLE | Yes | Original amount INR | `2499.50` |
| net_amount | DOUBLE | Yes | After discount — gross × (1 - discount_pct/100) | `2249.55` |
| discount_pct | INT | Yes | Discount applied 0–20 | `10` |
| status | STRING | Yes | success / failed / refunded | `success` |
| platform | STRING | Yes | iOS / Android / Web | `Android` |
| category | STRING | Yes | Denormalised category | `Electronics` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

### `fact_sessions`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| session_key | STRING | No | PK — same as Bronze session_id | `SESA1B2C3D4` |
| customer_key | STRING | Yes | FK → dim_customer.customer_key | `CUST_A1B2C3D4` |
| date_key | STRING | Yes | FK → dim_date.date_key | `2024-03-15` |
| location_key | STRING | Yes | FK → dim_location.location_key | `LOC_MUM_01` |
| session_duration_mins | DOUBLE | Yes | Session length in minutes | `24.0` |
| pages_visited | INT | Yes | Pages visited in session | `8` |
| actions_taken | INT | Yes | Actions in session | `5` |
| device_type | STRING | Yes | Mobile / Desktop / Tablet | `Mobile` |
| platform | STRING | Yes | iOS / Android / Web | `iOS` |
| is_bounce | INT | Yes | 1 = under 60 seconds | `0` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

### `fact_support`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| ticket_key | STRING | No | PK — same as Bronze ticket_id | `TKTA1B2C3D4` |
| customer_key | STRING | Yes | FK → dim_customer.customer_key | `CUST_A1B2C3D4` |
| date_key | STRING | Yes | FK → dim_date.date_key | `2024-03-15` |
| issue_type | STRING | Yes | Type of issue | `Payment Failure` |
| priority | STRING | Yes | Low / Medium / High / Critical | `High` |
| status | STRING | Yes | open / closed | `closed` |
| is_resolved | INT | Yes | 1 = closed, 0 = open | `1` |
| resolution_hours | DOUBLE | Yes | Hours to resolve — NULL if open | `22.5` |
| satisfaction_score | INT | Yes | Rating 1–5 — NULL if open | `4` |
| pipeline_run_id | STRING | Yes | Run that created this row | `20240315_142210` |

---

## Gold layer — `customer360_gold`

### `gold_dim_customer`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| customer_key | STRING | No | PK — CUST_ + user_id | `CUST_A1B2C3D4` |
| user_id | STRING | Yes | Natural key | `A1B2C3D4` |
| name | STRING | Yes | Full name | `Priya Sharma` |
| age | INT | Yes | Age | `32` |
| gender | STRING | Yes | Male / Female / Other | `Female` |
| city | STRING | Yes | City | `Mumbai` |
| state | STRING | Yes | State — enriched from dim_city | `Maharashtra` |
| region | STRING | Yes | Region — enriched from dim_city | `West` |
| city_tier | STRING | Yes | Tier 1 / Tier 2 | `Tier 1` |
| country | STRING | Yes | Always India | `India` |
| email | STRING | Yes | Email | `priya.sharma@email.com` |
| signup_date | DATE | Yes | Signup date | `2023-06-15` |
| customer_age_days | INT | Yes | Days since signup | `285` |
| is_active | INT | Yes | 1 = active | `1` |

### `gold_dim_date`

Same columns as `customer360_silver.dim_date` — reused directly.

### `gold_dim_segment`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| segment_key | STRING | No | PK — SEG_PREMIUM etc | `SEG_PREMIUM` |
| segment_name | STRING | Yes | Segment name | `Premium` |
| description | STRING | Yes | Business description | `High-value paying customers` |
| target_channel | STRING | Yes | Marketing channel | `Account Manager` |

### `gold_dim_tier`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| tier_key | STRING | No | PK — TIER_CHAMPIONS etc | `TIER_CHAMPIONS` |
| tier_name | STRING | Yes | Tier name | `Champions` |
| rfm_range | STRING | Yes | RFM score range | `13–15` |
| retention_strategy | STRING | Yes | CRM action for this tier | `Reward and upsell — loyalty programme` |
| priority_rank | INT | Yes | 1 = highest priority | `1` |

### `gold_fact_customer_metrics`

| Column | Type | Nullable | Description | Example |
|--------|------|----------|-------------|---------|
| customer_key | STRING | No | PK + FK → gold_dim_customer | `CUST_A1B2C3D4` |
| segment_key | STRING | Yes | FK → gold_dim_segment | `SEG_PREMIUM` |
| tier_key | STRING | Yes | FK → gold_dim_tier | `TIER_LOYAL` |
| first_txn_date | STRING | Yes | FK → gold_dim_date — first purchase date | `2023-08-10` |
| total_spend | DOUBLE | Yes | LTV — successful net_amount only | `42000.00` |
| txn_count | LONG | Yes | All transactions including failed | `12` |
| avg_order_value | DOUBLE | Yes | Avg net_amount on successful txns | `3500.00` |
| successful_txns | LONG | Yes | Count status=success | `10` |
| failed_txns | LONG | Yes | Count status=failed | `2` |
| refunded_txns | LONG | Yes | Count status=refunded | `0` |
| failure_rate | DOUBLE | Yes | failed / total × 100 | `16.7` |
| last_txn_date | STRING | Yes | Most recent transaction date | `2024-01-10` |
| top_category | STRING | Yes | Most frequent purchase category | `Electronics` |
| recency_days | INT | Yes | Days since last transaction — 9999 if never | `72` |
| r_score | INT | Yes | Recency score 1–5 | `2` |
| f_score | INT | Yes | Frequency score 1–5 | `4` |
| m_score | INT | Yes | Monetary score 1–5 | `3` |
| rfm_score | INT | Yes | r + f + m total 3–15 | `9` |
| session_count | LONG | Yes | Total app sessions | `24` |
| avg_session_mins | DOUBLE | Yes | Average session duration | `18.5` |
| total_pages | LONG | Yes | Total pages visited | `142` |
| total_actions | LONG | Yes | Total actions taken | `87` |
| bounce_rate | DOUBLE | Yes | % sessions under 60 seconds | `12.5` |
| engagement_score | DOUBLE | Yes | Composite 0–100 (sessions 40% / actions 30% / pages 20% / non-bounce 10%) | `62.4` |
| last_session_date | STRING | Yes | Most recent session date | `2024-01-08` |
| ticket_count | LONG | Yes | Total support tickets | `6` |
| open_tickets | LONG | Yes | Unresolved tickets | `2` |
| critical_tickets | LONG | Yes | Priority=Critical tickets | `1` |
| avg_resolution_hrs | DOUBLE | Yes | Average hours to resolve | `18.2` |
| avg_satisfaction | DOUBLE | Yes | Average satisfaction score 1–5 | `3.8` |
| support_health_score | DOUBLE | Yes | 0–100 composite support health | `54.0` |
| last_ticket_date | STRING | Yes | Most recent ticket date | `2024-01-10` |
| churn_flag | INT | Yes | 1 = churned, 0 = active | `1` |
| churn_reason | STRING | Yes | Why flagged — NULL if not churned | `Inactive 60+ days` |
| pipeline_run_id | STRING | Yes | Run that last rebuilt this table | `20240315_142210` |