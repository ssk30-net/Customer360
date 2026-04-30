# ============================================================
# FILE    : pages/dashboard.py
# PURPOSE : Page 1 — Executive dashboard
#           KPI cards, tier chart, segment donut,
#           revenue trend, churn risk table
# ROUTE   : /  (home page)
# ============================================================

import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd

from data.queries import (
    get_kpi_summary,
    get_revenue_by_tier,
    get_segment_distribution,
    get_churn_risk_table,
    get_revenue_trend,
)
from components.kpi_cards import kpi_row
from components.charts import (
    revenue_by_tier_chart,
    segment_donut_chart,
    revenue_trend_chart,
)

dash.register_page(__name__, path="/", title="Dashboard — Customer 360")

# ── Tier badge colours ────────────────────────────────────────
TIER_BADGE = {
    "Champions": "success",
    "Loyal":     "primary",
    "Potential": "warning",
    "At Risk":   "danger",
    "Dormant":   "secondary",
}

# ── Layout ────────────────────────────────────────────────────
layout = html.Div([

    # Header row
    dbc.Row([
        dbc.Col([
            html.H5("Executive dashboard", className="fw-semibold mb-0"),
            html.Small("Live data from customer360_gold",
                       className="text-muted"),
        ], md=8),
        dbc.Col([
            dbc.Button(
                "Refresh",
                id   = "dashboard-refresh-btn",
                size = "sm",
                color= "outline-secondary",
                className="float-end",
            ),
        ], md=4),
    ], className="mb-3 align-items-center"),

    # KPI cards — populated by callback
    html.Div(id="kpi-cards-row"),

    # Charts row
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    dcc.Graph(id="tier-bar-chart",
                              config={"displayModeBar": False})
                )
            ], className="shadow-sm"),
            md=7, className="mb-3",
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    dcc.Graph(id="segment-donut-chart",
                              config={"displayModeBar": False})
                )
            ], className="shadow-sm"),
            md=5, className="mb-3",
        ),
    ]),

    # Revenue trend
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(
                    dcc.Graph(id="revenue-trend-chart",
                              config={"displayModeBar": False})
                )
            ], className="shadow-sm"),
            md=12, className="mb-3",
        ),
    ]),

    # Churn risk table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.Span([
                        "⚠ Churn risk — top customers to retain",
                        dbc.Badge("Action required", color="danger",
                                  className="ms-2"),
                    ])
                ),
                dbc.CardBody(
                    html.Div(id="churn-risk-table")
                ),
            ], className="shadow-sm"),
        ], md=12, className="mb-3"),
    ]),

    # Hidden store — triggers data load on page mount
    dcc.Store(id="dashboard-trigger", data=0),
])


# ── Callbacks ─────────────────────────────────────────────────

@callback(
    Output("kpi-cards-row",      "children"),
    Output("tier-bar-chart",     "figure"),
    Output("segment-donut-chart","figure"),
    Output("revenue-trend-chart","figure"),
    Output("churn-risk-table",   "children"),
    Input("dashboard-trigger",   "data"),
    Input("dashboard-refresh-btn","n_clicks"),
    prevent_initial_call=False,
)
def load_dashboard(_trigger, _n_clicks):
    """Load all dashboard data in one callback."""

    # ── KPI cards ─────────────────────────────────────────────
    kpi_df  = get_kpi_summary()
    row     = kpi_df.iloc[0]

    cards = kpi_row([
        {
            "title":          "Total customers",
            "value":          f"{int(row['total_customers']):,}",
            "subtitle":       f"{int(row['never_transacted'])} never transacted",
            "border_color":   "#1D9E75",
        },
        {
            "title":          "Total LTV",
            "value":          f"₹{int(row['total_revenue']):,}",
            "subtitle":       "successful transactions only",
            "border_color":   "#378ADD",
        },
        {
            "title":          "Churn rate",
            "value":          f"{row['churn_rate']}%",
            "subtitle":       f"{int(row['churned_customers'])} customers at risk",
            "subtitle_color": "text-danger",
            "border_color":   "#D85A30",
        },
        {
            "title":          "Avg engagement",
            "value":          f"{row['avg_engagement']} / 100",
            "subtitle":       f"Support health: {row['avg_support_health']}",
            "border_color":   "#EF9F27",
        },
    ])

    # ── Charts ────────────────────────────────────────────────
    tier_df    = get_revenue_by_tier()
    seg_df     = get_segment_distribution()
    trend_df   = get_revenue_trend()

    tier_fig   = revenue_by_tier_chart(tier_df)
    seg_fig    = segment_donut_chart(seg_df)
    trend_fig  = revenue_trend_chart(trend_df)

    # ── Churn risk table ──────────────────────────────────────
    churn_df   = get_churn_risk_table(limit=20)

    table_rows = []
    for _, r in churn_df.iterrows():
        table_rows.append(html.Tr([
            html.Td(
                dbc.Button(
                    r["name"],
                    href   = f"/customer?id={r['customer_key']}",
                    color  = "link",
                    size   = "sm",
                    className = "p-0 text-start",
                )
            ),
            html.Td(r["city"]),
            html.Td(dbc.Badge(r["tier"],
                              color=TIER_BADGE.get(r["tier"],"secondary"))),
            html.Td(f"₹{int(r['lifetime_value']):,}"),
            html.Td(f"{int(r['recency_days'])} days"),
            html.Td(r["churn_reason"] or "—",
                    style={"fontSize":"11px","color":"#dc3545"}),
            html.Td(
                dbc.Badge(r["retention_strategy"][:30]+"…"
                          if len(str(r["retention_strategy"])) > 30
                          else r["retention_strategy"],
                          color="light", text_color="dark",
                          style={"fontSize":"10px"}),
            ),
        ]))

    churn_table = dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Customer"), html.Th("City"),
                html.Th("Tier"),     html.Th("LTV"),
                html.Th("Inactive"), html.Th("Reason"),
                html.Th("Action"),
            ])),
            html.Tbody(table_rows),
        ],
        striped=True, hover=True, responsive=True,
        size="sm", className="mb-0",
    )

    return cards, tier_fig, seg_fig, trend_fig, churn_table