from dash import html, dcc, callback, Input, Output, State, ALL, dash_table
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import os
from env import *
from icecream import ic
import pandas as pd


ic.configureOutput(includeContext=True)

dash.register_page(__name__)

layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="search-click-data"),
    html.Div(id="dummy-div", style={'display':'None'}),
    dbc.Row(
        dbc.Col(
            html.H1("Search Results", style={
                'fontWeight': 'bold',
                'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)',
                "padding": "5px",
                "borderRadius": "5px"
            }),
            width="auto",
            className="mx-auto"
        ),
        className="text-center"
    ),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id="file-results",
                columns=[{"name": "Files", "id": "file"}],
                style_table={"height": "70vh", "overflowY": "auto",
                             "color": "secondary",
                             'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)',
                             "margin": "15px",
                             "borderRadius": "5px", },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontSize': '20px'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '0px',
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'fontSize': '15px',
                    'backgroundColor': 'rgb(210, 210, 210)'
                },
            )],
            width=6
        ),
        dbc.Col(
            [dash_table.DataTable(
                id="dir-results",
                columns=[{"name": "Directories", "id": "directory"}],
                style_table={"height": "70vh", "overflowY": "auto",
                             "color": "secondary",
                             'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)',
                             "margin": "15px",
                             "borderRadius": "5px", },
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'fontSize': '20px'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '5px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'minWidth': '0px',
                    'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'fontSize': '15px',
                    'backgroundColor': 'rgb(210, 210, 210)'
                },
            )],
            width=6),

    ], id="search-results"),
    dbc.Row([dbc.Col(width=2),dbc.Col(
    dbc.Button(
        "Open Selection",
        id="open-sel-button",
        n_clicks=0,
        style={"width": "60%", "margin": "auto", "display": "block", "color":"light"},
        ),
        width=8,
        style={"padding": "0px"},
            ), dbc.Col(width=2)])
    ], fluid=True, className="py-3", style={"height": "100vh"})


@callback(
    [Output('file-results', 'data'), Output('dir-results', 'data'), Output('search-click-data', 'data')],
    [Input("search-results", 'data'), Input('file-results', 'active_cell'), Input('dir-results', 'active_cell')],
    [State('file-results', 'data'), State('dir-results', 'data')]
)
def show_results(data, file_active_cell, dir_active_cell, file_data, dir_data):
    if data is None:
        return (pd.DataFrame(columns=["file"]), pd.DataFrame(columns=["directory"]))
    
    # print(data)
    print(file_active_cell, dir_active_cell)

    file_items = data[0]
    dir_items = data[1]
    file_df = pd.DataFrame(file_items, columns=["file"])
    dir_df = pd.DataFrame(dir_items, columns=["directory"])
    
    if file_active_cell:
        path = PATH_TO_THD_DIR+data[0][file_active_cell["row"]].replace("\\", "/").strip()
        print(path)
        return file_df.to_dict('records'), dir_df.to_dict('records'), path
    if dir_active_cell:
        path = PATH_TO_THD_DIR+data[1][dir_active_cell["row"]].replace("\\", "/").strip()
        return file_df.to_dict('records'), dir_df.to_dict('records'), path
    

    return file_df.to_dict('records'), dir_df.to_dict('records'), {}

# @callback(Output('search-click-data', 'data'), [Input('file-results', 'derived_virtual_selected_rows'),
#                                                     Input('dir-results', 'derived_virtual_selected_rows')])
# def update_click_data(file_selected_rows, dir_selected_rows):
#     print(file_selected_rows, dir_selected_rows)
#     if file_selected_rows:
#         return {'id': 'file-results'}
#     elif dir_selected_rows:
#         return {'id': 'dir-results'}
#     else:
#         return None

@callback([Output('file-results', 'active_cell'), 
    Output('dir-results', 'active_cell')],
    Input('open-sel-button', 'n_clicks'),
    State('search-click-data', 'data')
)
def openFile(clic, data):
    if not clic:
        raise PreventUpdate
    print("button clicked")
    print(data)
    os.startfile(data)
    return None, None