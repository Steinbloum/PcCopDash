from dash import Dash, html, dcc, page_container, Input, Output, State
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("PointMap", href="/hwindex")),
        dbc.NavItem(dbc.NavLink("PointInspector", href="#")),
        dbc.Col(  # Use dbc.Col to align the form with other navbar items
            dbc.Form(
                dbc.InputGroup(
                    [
                        # dbc.InputGroupText("Search"),  # Optional: Add a prefix text or icon
                        dbc.Input(id='navbar-search', placeholder="Search Tech File", type="search"),
                        dbc.Button("Go", id='navbar-search-button', n_clicks=0),  # Add a search button
                    ],
                    className="me-2",  # Margin end to align items inside the input group
                ),
                className="d-flex",  # Display form as flex to align search input and button
            ),
            width="auto"  # Set the column width to auto to only take necessary space
        ),
    ],
    brand="HardwareAssistant",
    brand_href="/home",
    color="primary",
    dark=True,
)




app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Download(id="download-dataframe-csv"),
    navbar,
    dbc.Container(
        dbc.Row([
            dbc.Col(html.Div(id='side-pane-content'), width=2, style={"height": "100vh", "margin-top":"20px"}),
            dbc.Col(page_container, width=10),
        ]),
        fluid=True,
    ),
])





if __name__ == "__main__":
    app.run_server(debug=True)

