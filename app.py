import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc



app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)



navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("PointMap", href="/hwindex")),
        dbc.NavItem(dbc.NavLink("PointInspector", href="/pointmap")),
        dbc.Col(
            dbc.Form(
                dbc.InputGroup(
                    [
                        # dbc.InputGroupText("Search"),  # prefix
                        dbc.Input(id='navbar-search', placeholder="Search Tech File", type="search"),
                        dbc.Button("Go", id='navbar-search-button', n_clicks=0),
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
    dcc.Store(id="selected-hardware"),
    dcc.Location(id="url", refresh=False),
    dcc.Download(id="download-dataframe-csv"),
    dbc.Col(navbar),
    dbc.Container(
        dbc.Col(dash.page_container, width=10),  # Correct usage of page_container within dbc.Container
        fluid=True,
    ),
],style={'backgroundColor': '#D3D3D3'})


if __name__ == "__main__":
    # os.startfile("http://127.0.0.1:8050/home")
    app.run_server(debug=True)

