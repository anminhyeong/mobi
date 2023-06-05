import os
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from server import app
from pages import mainpage, groupAnalysis, indivAnalysis, selectgr
import pandas as pd

#################
#               #
#    M O B I    #
#               #
#################

TOPBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width" : "100%",
    "height": "10rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
    "font-family" : "Georgia"
}

CONTENT_STYLE = {
    "marginTop" : "10rem",
    "padding" : "1rem 1rem"
}

topbar = html.Div(
    [
        dcc.Link(
            "MOBI",
            href="/",
            className="h3",
            style={"textDecoration": "none", "color": "black"},
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavItem(
                    dbc.NavLink("Select Group", href="/selectgr", active="exact")
                ),
                dbc.NavItem(
                    dbc.NavLink("Group Analysis", href="/groupAnalysis", active="exact")
                ),
                dbc.NavItem(
                    dbc.NavLink("Individual Analysis", href="/indivAnalysis", active="exact")
                ),
            ],
        ),
    ],
    style = TOPBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page_content(pathname):
    if pathname == "/":
        return mainpage.layout
    elif pathname == "/selectgr":
        return selectgr.layout
    elif pathname == "/groupAnalysis":
        return groupAnalysis.layout
    elif pathname == "/indivAnalysis":
        return indivAnalysis.layout
    
    return dbc.Container(
            [
                html.H1("404: Not found", className="display-3"),
            ])
    

app.layout = html.Div(
    [
        dcc.Store(id="places", storage_type="session"),
        dcc.Store(id="place-areas", storage_type="session"),
        dcc.Location(id="url", refresh=False),
        topbar,
        content
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True)