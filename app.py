from dash import Dash, html, dcc, page_container, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("PointMap", href="/hwindex")),
        dbc.NavItem(dbc.NavLink("PointInspector", href="#")),
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="Links",
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
        ),
    ],
    brand="HardwareAssistant",
    brand_href="/home",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    dcc.Download(id="download-dataframe-csv"),
    navbar,
    dbc.Container(
        dbc.Row([
            dbc.Col(html.Div(id='side-pane_content'), width=2, style={"height": "100vh", "margin-top":"20px"}),  # Ensure this ID matches
            dbc.Col(page_container, width=10),
        ]),
        fluid=True,
    ),
])


if __name__ == "__main__":
    app.run_server(debug=True)

