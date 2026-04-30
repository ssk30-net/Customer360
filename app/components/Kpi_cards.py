# ============================================================
# FILE    : components/kpi_cards.py
# PURPOSE : Reusable KPI card component
# ============================================================

from dash import html
import dash_bootstrap_components as dbc


def kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    subtitle_color: str = "text-muted",
    border_color: str = "#dee2e6",
) -> dbc.Card:
    """
    Returns a single KPI card.
    subtitle_color: Bootstrap text class or hex color.
    """
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="text-muted mb-1",
                   style={"fontSize": "12px", "fontWeight": "500",
                          "textTransform": "uppercase", "letterSpacing": ".05em"}),
            html.H4(value, className="mb-1 fw-semibold"),
            html.Small(subtitle, className=subtitle_color,
                       style={"fontSize": "11px"}),
        ]),
        className="shadow-sm h-100",
        style={"borderLeft": f"3px solid {border_color}"},
    )


def kpi_row(kpis: list) -> dbc.Row:
    """
    Wraps a list of kpi_card() calls into a responsive Bootstrap row.
    kpis: list of dicts with keys: title, value, subtitle,
          subtitle_color (optional), border_color (optional)
    """
    cols = []
    for k in kpis:
        cols.append(
            dbc.Col(
                kpi_card(
                    title          = k["title"],
                    value          = k["value"],
                    subtitle       = k.get("subtitle", ""),
                    subtitle_color = k.get("subtitle_color", "text-muted"),
                    border_color   = k.get("border_color", "#dee2e6"),
                ),
                xs=12, sm=6, md=3,
                className="mb-3",
            )
        )
    return dbc.Row(cols, className="mb-2")


def metric_card(
    title: str,
    value: str,
    sub: str = "",
    color: str = "#1D9E75",
) -> dbc.Card:
    """
    Smaller metric card for customer detail page.
    """
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="text-muted mb-1",
                   style={"fontSize": "11px"}),
            html.H5(value, className="mb-0 fw-semibold",
                    style={"color": color}),
            html.Small(sub, className="text-muted",
                       style={"fontSize": "10px"}),
        ], className="py-2 px-3"),
        className="shadow-sm h-100",
    )