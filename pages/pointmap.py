
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import dash
import json


dash.register_page(__name__)




layout = dbc.Container([
dbc.Row([    
    dcc.Location("url", refresh=False), 
    dcc.Store(id="stored-filters"),
    
    
      
        # Side pane column
        dbc.Col(
            html.Div([
                html.H4(id="side-pane-content", className="p-2 text-center"),
                    ]),
            width=3),

        dbc.Col(
            html.Div([
                dcc.Graph(id='scatter-plot', style={'height': '90vh'})]), width=9),    
        dbc.Button("View Map", id="view-map-button", style={"display": "None"}),#to adjust callback
        ])])

@callback(
    [Output('scatter-plot', 'figure'),
    Output('stored-filters', 'data')],
    Input('url', 'pathname'),
    State('selected-hardware', 'data'))
def update_figure(pathname, data):
    #plotly stuff i'll handle
    print(pathname,data)
    return {}, {}
    

