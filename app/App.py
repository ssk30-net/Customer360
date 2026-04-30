# ============================================================
# FILE    : app.py
# PURPOSE : Dash entry point — multi-page router
# DEPLOY  : Databricks Apps (native workspace deployment)
# ============================================================
#
# DATABRICKS APPS NOTES
# ─────────────────────────────────────────────────────────────
# - No credentials needed — Databricks Apps injects auth
#   automatically via DATABRICKS_HOST env variable
# - SQL warehouse connection uses databricks-sdk (included)
# - Deploy via: Databricks workspace → Compute → Apps → Create
# - app.yaml tells Databricks how to start this app
# ============================================================

import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,                         # enables pages/ directory routing
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
    ],
    suppress_callback_exceptions=True,      # needed for multi-page apps
    title="Customer 360",
)

# ── Layout ────────────────────────────────────────────────────
# Navbar is shared across all pages.
# dash.page_container renders the active page below it.

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Customer 360", className="fw-semibold"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink(
                "Dashboard",
                href="/",
                active="exact",
            )),
            dbc.NavItem(dbc.NavLink(
                "Customer lookup",
                href="/customer",
                active="exact",
            )),
        ], navbar=True, className="ms-3"),
    ], fluid=True),
    color="dark",
    dark=True,
    className="mb-4",
)

app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dbc.Container(
        dash.page_container,
        fluid=True,
        className="px-4",
    ),
])

# ── Entry point ───────────────────────────────────────────────
# Databricks Apps starts the server via gunicorn pointing at
# this file. The app object must be importable as `app.server`
# for gunicorn to find it.
server = app.server

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)