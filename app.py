import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from env import *
import time
import re
from icecream import ic

ic.configureOutput(includeContext=True)


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True, suppress_callback_exceptions=True)



navbar = dbc.NavbarSimple(
    children=[
        
        dbc.NavItem(dbc.NavLink("TipMap", href="/hwindex")),
        dbc.NavItem(dbc.NavLink("TipDetective", href="/tipdetective")),
        dbc.NavItem(dbc.NavLink("TDR Compiler", href="/tdrcomp")),
        dbc.Col(
            dbc.Form(
                dbc.InputGroup(
                    [
                        # dbc.InputGroupText("Search"),  # prefix
                        dbc.Input(id='navbar-search', placeholder="Search Tech File", type="search"),
                        dbc.Button("Go", id='navbar-search-button', n_clicks=0, href="/search-results"),
                    ],
                    className="me-2",  # Margin end to align items inside the input group
                ),
                className="d-flex",  # Display form as flex to align search input and button
            ),
            width="auto"  # Set the column width to auto to only take necessary space
        ),
        # dbc.Col(html.Img(src="assets/ST_logo_2020_white_no_tagline.png", height='auto')),
    ],
brand = dbc.Row(
    [
        dbc.Col(html.Img(src="assets/ST_logo_2020_white_no_tagline.png", height='50px')),
        dbc.Col(html.P("ProbeCard Copilot", className="my-auto")),
    ],
    align="center",
    className="align-items-center"),
    brand_href="/home",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    dcc.Store(id="selected-hardware"),
    dcc.Store(id="search-results"),
    dcc.Location(id="url", refresh=False),
    dcc.Download(id="download-dataframe-csv"),
    dbc.Row([navbar,dash.page_container]),
], style={'backgroundColor': '#D3D3D3'})


@app.callback(
    Output('search-results', 'data'),
    Input('navbar-search-button', 'n_clicks'),
    State('navbar-search', 'value'))
def search_file(n_clicks, term):
    pass
    # if term is None:
    #     return None, None
    # st = time.time()
    # ic(f"Searching for '{term}' in THD Directory")
    # search_term = term.lower()
    # files = []
    # dirs = []
    # with open(PATH_TO_TREE, "r") as f:
    #     for line in (l.lower() for l in f):
    #         if search_term in line:
    #             if ("." in line.split("\\")[-1])&(bool(re.search(r'.\D+',line.split('\\')[-1]))):
    #                 files.append(line.replace(PATH_TO_THD_DIR.lower(), ''))

    #             else:
    #                 dirs.append(line.replace(PATH_TO_THD_DIR.lower(), ''))
    # ic(f"Found {len(files)} files and {len(dirs)} directories in {round(time.time()-st), 2}")
    # ic(files, dirs)
    # return files, dirs


if __name__ == "__main__":
    # os.startfile("http://127.0.0.1:8050/home")
    # app.run_server(debug=True, host='0.0.0.0')
    app.run_server(debug=True)

