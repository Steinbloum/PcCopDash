# home.py

# Import necessary libraries
from dash import html, callback, Input, Output, State
import dash

# Optional: If you're using Dash Bootstrap Components
import dash_bootstrap_components as dbc

# Register your page
dash.register_page(__name__)

# Define the page content
layout = html.Div(
    dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.H1("Hardware Assistant", className="text-center"),
                    width=12
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.P("Your new debug best friend !", className="text-center"),
                    width=12
                )
            )
        ],
        fluid=True,
        className="py-3",  # Add some padding around the container
    ),
    style={"height": "100vh", "display": "flex", "alignItems": "center"}  # This centers the content vertically
)

# @callback(
#     Output('side-pane-content', 'children'),
#     Input('url', 'pathname')
# )
# def update_side_panel_content(pathname):
#     if pathname == "/home":
#         return html.P("Home Page Content")
#     elif pathname == "/hwindex": 
#         return None
#     else:
#         return html.Div()

