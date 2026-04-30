# ============================================================
# FILE    : pages/customer_detail.py
# PURPOSE : Page 2 — Customer 360 detail view
#           Search bar → customer profile card →
#           metric grid → RFM gauges → engagement radar →
#           activity timeline (transactions + sessions + tickets)
# ROUTE   : /customer
# DEEPLINK: /customer?id=CUST_XXXXXXXX
# ============================================================

import dash
from dash import html, dcc, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd

from data.queries import (
    search_customers,
    get_customer_profile,
    get_customer_transactions,
    get_customer_tickets,
    get_customer_sessions,
)
from components.kpi_cards import metric_card
from components.charts import rfm_gauge, engagement_radar

dash.register_page(__name__, path="/customer",
                   title="Customer lookup — Customer 360")

# ── Tier / priority badge colours ─────────────────────────────
TIER_BADGE     = {"Champions":"success","Loyal":"primary",
                  "Potential":"warning","At Risk":"danger","Dormant":"secondary"}
PRIORITY_BADGE = {"Critical":"danger","High":"warning",
                  "Medium":"info","Low":"secondary"}
STATUS_BADGE   = {"success":"success","failed":"danger","refunded":"warning",
                  "closed":"success","open":"warning"}

# ── Layout ────────────────────────────────────────────────────
layout = html.Div([

    # URL component — reads ?id= query param
    dcc.Location(id="customer-url"),

    # Header
    html.H5("Customer lookup", className="fw-semibold mb-3"),

    # Search bar
    dbc.Row([
        dbc.Col(
            dbc.Input(
                id          = "customer-search-input",
                placeholder = "Search by name, email or user ID...",
                type        = "text",
                debounce    = True,
            ),
            md=8,
        ),
        dbc.Col(
            dbc.Button("Search", id="customer-search-btn",
                       color="primary", className="w-100"),
            md=2,
        ),
    ], className="mb-3"),

    # Search results dropdown (hidden until search)
    html.Div(id="search-results-list", className="mb-3"),

    # Customer detail section (hidden until customer selected)
    html.Div(id="customer-detail-section"),
])


# ── Callbacks ─────────────────────────────────────────────────

@callback(
    Output("search-results-list", "children"),
    Input("customer-search-btn",  "n_clicks"),
    Input("customer-search-input","n_submit"),
    State("customer-search-input","value"),
    prevent_initial_call=True,
)
def run_search(_clicks, _submit, query):
    """Search customers and display clickable results."""
    if not query or len(query.strip()) < 2:
        return dbc.Alert("Enter at least 2 characters to search.",
                         color="warning", className="py-2")

    results = search_customers(query.strip())

    if results.empty:
        return dbc.Alert(f"No customers found for '{query}'.",
                         color="secondary", className="py-2")

    items = []
    for _, r in results.iterrows():
        items.append(
            dbc.ListGroupItem(
                dbc.Row([
                    dbc.Col([
                        html.Span(r["name"], className="fw-semibold me-2"),
                        dbc.Badge(r["tier"],
                                  color=TIER_BADGE.get(r["tier"],"secondary"),
                                  className="me-1"),
                        html.Small(f"{r['city']} · {r['segment']}",
                                   className="text-muted"),
                    ], md=7),
                    dbc.Col(
                        html.Span(f"₹{int(r['lifetime_value']):,}",
                                  className="fw-semibold text-success"),
                        md=2, className="text-end",
                    ),
                    dbc.Col(
                        dbc.Badge("⚠ Churned", color="danger")
                        if r["churn_flag"] else
                        dbc.Badge("Active", color="success"),
                        md=3, className="text-end",
                    ),
                ]),
                action = True,
                href   = f"/customer?id={r['customer_key']}",
                className = "py-2",
            )
        )

    return dbc.ListGroup(items, flush=True, className="border rounded")


@callback(
    Output("customer-detail-section", "children"),
    Input("customer-url", "search"),   # ?id=CUST_XXXXXXXX
    prevent_initial_call=False,
)
def load_customer_detail(search: str):
    """Load full customer profile when ?id= param is present."""
    if not search or "id=" not in search:
        return html.Div()

    # Parse ?id= from URL
    customer_key = search.split("id=")[-1].split("&")[0]
    if not customer_key:
        return html.Div()

    # ── Fetch data ────────────────────────────────────────────
    profile_df  = get_customer_profile(customer_key)
    if profile_df.empty:
        return dbc.Alert("Customer not found.", color="danger")

    p           = profile_df.iloc[0]
    txn_df      = get_customer_transactions(customer_key)
    ticket_df   = get_customer_tickets(customer_key)
    session_df  = get_customer_sessions(customer_key)

    # ── Profile card ──────────────────────────────────────────
    initials = "".join(w[0].upper() for w in str(p["name"]).split()[:2])

    profile_card = dbc.Card(
        dbc.CardBody(
            dbc.Row([
                dbc.Col(
                    html.Div(
                        initials,
                        className="rounded-circle bg-primary text-white "
                                  "d-flex align-items-center justify-content-center fw-bold",
                        style={"width":"48px","height":"48px","fontSize":"16px"},
                    ),
                    width="auto",
                ),
                dbc.Col([
                    html.H6(p["name"], className="fw-semibold mb-0"),
                    html.Small(
                        [
                            f"ID: {p['user_id']}  ·  ",
                            f"{p['city']}, {p.get('state','')}  ·  ",
                            dbc.Badge(p["segment_name"], color="light",
                                      text_color="dark", className="me-1"),
                            dbc.Badge(p["tier_name"],
                                      color=TIER_BADGE.get(p["tier_name"],"secondary")),
                        ],
                        className="text-muted",
                    ),
                ]),
                dbc.Col([
                    html.Div([
                        html.Small("Churn reason", className="text-muted d-block"),
                        html.Span(
                            p["churn_reason"] if p["churn_flag"] else "✓ Active customer",
                            className="fw-semibold " + (
                                "text-danger" if p["churn_flag"] else "text-success"
                            ),
                            style={"fontSize":"13px"},
                        ),
                    ])
                ], className="text-end"),
            ], align="center"),
        ),
        className="shadow-sm mb-3",
    )

    # ── Metric grid ───────────────────────────────────────────
    metrics = dbc.Row([
        dbc.Col(metric_card("Lifetime value",
                            f"₹{int(p['total_spend']):,}",
                            f"r={p['r_score']} f={p['f_score']} m={p['m_score']} → rfm {p['rfm_score']}",
                            "#1D9E75"), md=4, className="mb-3"),
        dbc.Col(metric_card("Last transaction",
                            f"{int(p['recency_days'])} days ago",
                            f"First purchase: {p.get('first_txn_date','—')}",
                            "#378ADD"), md=4, className="mb-3"),
        dbc.Col(metric_card("Engagement score",
                            f"{p['engagement_score']} / 100",
                            f"{int(p['session_count'])} sessions · {p['bounce_rate']}% bounce",
                            "#EF9F27"), md=4, className="mb-3"),
        dbc.Col(metric_card("Transactions",
                            f"{int(p['txn_count'])}",
                            f"{int(p['successful_txns'])} success · {int(p['failed_txns'])} failed",
                            "#1D9E75"), md=4, className="mb-3"),
        dbc.Col(metric_card("Support tickets",
                            f"{int(p['ticket_count'])}",
                            f"{int(p['open_tickets'])} open · {int(p['critical_tickets'])} critical",
                            "#D85A30"), md=4, className="mb-3"),
        dbc.Col(metric_card("Support health",
                            f"{p['support_health_score']} / 100",
                            f"Avg satisfaction: {p['avg_satisfaction']}",
                            "#888780"), md=4, className="mb-3"),
    ])

    # ── RFM gauges + engagement radar ─────────────────────────
    charts_row = dbc.Row([
        dbc.Col(
            dbc.Card(dbc.CardBody(
                dcc.Graph(
                    figure = rfm_gauge(
                        int(p["r_score"]),
                        int(p["f_score"]),
                        int(p["m_score"]),
                    ),
                    config = {"displayModeBar": False},
                )
            ), className="shadow-sm"),
            md=7, className="mb-3",
        ),
        dbc.Col(
            dbc.Card(dbc.CardBody(
                dcc.Graph(
                    figure = engagement_radar(p),
                    config = {"displayModeBar": False},
                )
            ), className="shadow-sm"),
            md=5, className="mb-3",
        ),
    ])

    # ── Activity timeline ─────────────────────────────────────
    timeline_items = []

    # Merge transactions
    for _, t in txn_df.iterrows():
        timeline_items.append({
            "date":  t["date_key"],
            "type":  "transaction",
            "icon":  "💳",
            "title": f"₹{int(t['amount']):,} · {t['category']} · {t['payment_method']}",
            "badge": t["status"],
            "color": STATUS_BADGE.get(t["status"], "secondary"),
        })

    # Merge tickets
    for _, t in ticket_df.iterrows():
        timeline_items.append({
            "date":  t["date_key"],
            "type":  "ticket",
            "icon":  "🎫",
            "title": f"{t['issue_type']} · {t['priority']} priority",
            "badge": t["status"],
            "color": STATUS_BADGE.get(t["status"], "secondary"),
        })

    # Merge sessions
    for _, s in session_df.iterrows():
        timeline_items.append({
            "date":  s["date_key"],
            "type":  "session",
            "icon":  "📱",
            "title": f"{s['duration_mins']} mins · {s['pages_visited']} pages · {s['device_type']}",
            "badge": "bounce" if s["is_bounce"] else "session",
            "color": "warning" if s["is_bounce"] else "light",
        })

    # Sort by date descending
    timeline_items.sort(key=lambda x: x["date"], reverse=True)

    tl_rows = []
    for item in timeline_items[:20]:
        tl_rows.append(
            dbc.Row([
                dbc.Col(
                    html.Small(item["date"], className="text-muted"),
                    width=2,
                ),
                dbc.Col(
                    html.Span(item["icon"] + " " + item["title"],
                              style={"fontSize": "12px"}),
                    width=8,
                ),
                dbc.Col(
                    dbc.Badge(item["badge"], color=item["color"],
                              text_color="dark" if item["color"]=="light" else None,
                              style={"fontSize":"10px"}),
                    width=2, className="text-end",
                ),
            ], className="py-1 border-bottom")
        )

    timeline = dbc.Card([
        dbc.CardHeader("Recent activity — last 20 events"),
        dbc.CardBody(tl_rows if tl_rows else
                     [html.Small("No activity found.", className="text-muted")]),
    ], className="shadow-sm mb-3")

    return html.Div([
        profile_card,
        metrics,
        charts_row,
        html.H6("Retention strategy", className="fw-semibold mt-2 mb-2"),
        dbc.Alert(
            [
                html.Strong(f"{p['tier_name']}: "),
                p["retention_strategy"],
            ],
            color = "info" if not p["churn_flag"] else "warning",
            className="py-2",
        ),
        timeline,
    ])