# ============================================================
# FILE    : components/charts.py
# PURPOSE : Reusable Plotly chart functions
# ============================================================

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Colour palette ────────────────────────────────────────────
TIER_COLORS = {
    "Champions": "#1D9E75",
    "Loyal":     "#378ADD",
    "Potential": "#EF9F27",
    "At Risk":   "#D85A30",
    "Dormant":   "#888780",
}

SEGMENT_COLORS = {
    "Premium":  "#1D9E75",
    "Standard": "#378ADD",
    "Basic":    "#EF9F27",
    "Trial":    "#888780",
}

CHART_LAYOUT = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="Inter, sans-serif", size=12),
    margin        = dict(l=10, r=10, t=30, b=10),
    showlegend    = True,
)


def revenue_by_tier_chart(df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart — revenue by customer tier.
    df columns: tier_name, total_revenue, customer_count, churn_rate_pct
    """
    df = df.sort_values("priority_rank", ascending=False)
    colors = [TIER_COLORS.get(t, "#888780") for t in df["tier_name"]]

    fig = go.Figure(go.Bar(
        x           = df["total_revenue"],
        y           = df["tier_name"],
        orientation = "h",
        marker_color= colors,
        text        = df["total_revenue"].apply(lambda v: f"₹{v:,.0f}"),
        textposition= "outside",
        customdata  = df[["customer_count", "churn_rate_pct"]],
        hovertemplate = (
            "<b>%{y}</b><br>"
            "Revenue: ₹%{x:,.0f}<br>"
            "Customers: %{customdata[0]}<br>"
            "Churn rate: %{customdata[1]}%"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title     = "Revenue by customer tier",
        xaxis     = dict(title="Net revenue (INR)", showgrid=False),
        yaxis     = dict(title=""),
        height    = 280,
        showlegend= False,
    )
    return fig


def segment_donut_chart(df: pd.DataFrame) -> go.Figure:
    """
    Donut chart — customer count by segment.
    df columns: segment_name, customer_count, total_revenue
    """
    colors = [SEGMENT_COLORS.get(s, "#888780") for s in df["segment_name"]]

    fig = go.Figure(go.Pie(
        labels       = df["segment_name"],
        values       = df["customer_count"],
        hole         = 0.55,
        marker_colors= colors,
        textinfo     = "label+percent",
        textfont_size= 11,
        hovertemplate= (
            "<b>%{label}</b><br>"
            "Customers: %{value}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title      = "Customer segment split",
        height     = 280,
        showlegend = False,
    )
    return fig


def revenue_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart — net revenue per quarter.
    df columns: fiscal_quarter_label, net_revenue, txn_count, unique_customers
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x          = df["fiscal_quarter_label"],
        y          = df["net_revenue"],
        mode       = "lines+markers",
        name       = "Net revenue",
        line       = dict(color="#1D9E75", width=2),
        marker     = dict(size=6),
        hovertemplate = (
            "<b>%{x}</b><br>"
            "Revenue: ₹%{y:,.0f}"
            "<extra></extra>"
        ),
    ))

    fig.add_trace(go.Bar(
        x          = df["fiscal_quarter_label"],
        y          = df["txn_count"],
        name       = "Transactions",
        marker_color = "rgba(55,138,221,0.25)",
        yaxis      = "y2",
        hovertemplate = (
            "Transactions: %{y:,}"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title   = "Revenue trend by quarter",
        height  = 280,
        yaxis   = dict(title="Net revenue (INR)", showgrid=True,
                       gridcolor="rgba(0,0,0,.06)"),
        yaxis2  = dict(title="Transactions", overlaying="y",
                       side="right", showgrid=False),
        legend  = dict(orientation="h", yanchor="bottom",
                       y=1.02, xanchor="right", x=1),
        xaxis   = dict(showgrid=False),
    )
    return fig


def rfm_gauge(r: int, f: int, m: int) -> go.Figure:
    """
    Three mini gauges showing R, F, M scores for a single customer.
    Each score is 1-5.
    """
    fig = go.Figure()

    positions = [
        (0.15, "Recency",   r, "#1D9E75"),
        (0.50, "Frequency", f, "#378ADD"),
        (0.85, "Monetary",  m, "#EF9F27"),
    ]

    for x, label, score, color in positions:
        fig.add_trace(go.Indicator(
            mode   = "gauge+number",
            value  = score,
            title  = dict(text=label, font=dict(size=11)),
            gauge  = dict(
                axis      = dict(range=[0, 5], tickvals=[1,2,3,4,5]),
                bar       = dict(color=color),
                bgcolor   = "rgba(0,0,0,.05)",
                threshold = dict(
                    line  = dict(color="red", width=2),
                    value = 2,
                ),
            ),
            domain = dict(x=[x-0.14, x+0.14], y=[0, 1]),
        ))

    fig.update_layout(
        **CHART_LAYOUT,
        height     = 180,
        showlegend = False,
        title      = "RFM scores (1=low  5=high)",
    )
    return fig


def engagement_radar(row: pd.Series) -> go.Figure:
    """
    Radar chart showing 5 engagement dimensions for one customer.
    Normalised 0-100 for display.
    """
    categories = [
        "Sessions",
        "Avg duration",
        "Pages visited",
        "Actions taken",
        "Non-bounce",
    ]

    # Normalise each metric to 0-100 for radar display
    values = [
        min(row.get("session_count", 0) / 50 * 100, 100),
        min(row.get("avg_session_mins", 0) / 90 * 100, 100),
        min(row.get("total_pages", 0) / 500 * 100, 100),
        min(row.get("total_actions", 0) / 300 * 100, 100),
        max(0, 100 - row.get("bounce_rate", 0)),
    ]
    values += [values[0]]   # close the polygon
    cats   = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r           = values,
        theta       = cats,
        fill        = "toself",
        fillcolor   = "rgba(29,158,117,0.15)",
        line_color  = "#1D9E75",
        name        = "Engagement",
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        polar  = dict(
            radialaxis = dict(visible=True, range=[0, 100],
                              showticklabels=False),
        ),
        height     = 260,
        showlegend = False,
        title      = "Engagement profile",
    )
    return fig