# home.py

# Import necessary libraries
from dash import html
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
