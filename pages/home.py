# home.py


from dash import html, dcc
import dash
import dash_bootstrap_components as dbc


dash.register_page(__name__)


layout = html.Div(
    dbc.Container(
        dbc.Col(
        [
            dbc.Row(
                [dcc.Location(id="url", refresh=False),
                dbc.Col(
                html.H1("Probecard Copilot", className="text-center"),
                    width=12
                )
            ]),
            dbc.Row(
                dbc.Col(
                    html.P("Your new Probecard debug best friend !", className="text-center"),
                    width=12
                )
            )
        ]),
        fluid=True,
        className="py-3",  # Add some padding around the container
    ),
    style={"height": "100vh", "display": "flex", "alignItems": "center"}  # This centers the content vertically
)


