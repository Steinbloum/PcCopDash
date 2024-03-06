
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import dash
import plotly.express as px
import pandas as pd
import sqlite3


dash.register_page(__name__, path="/pointmap")



df = pd.DataFrame()
filters = []


layout = dbc.Container([
    dbc.Row([    
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="stored-filters"),
        dbc.Col(
            html.Div(id="tmside-pane-content"),
            width=3),
        dbc.Col(
            html.Div([
                dcc.Graph(id='scatter-plot', style={'height': '100vh'})
                ]), 
            width=9),    
                ]),])

@callback(
    [Output('scatter-plot', 'figure'),
    Output('stored-filters', 'data'), 
    Output('tmside-pane-content', 'children')],
    Input('url', 'pathname'),
    State('selected-hardware', 'data'))
def update_figure(pathname, data):
    print(data)
    df = read_table(data['id'])
    cols_to_filter = [x for x in df.columns if x not in ["X", "Y", "pin_number", "pogolocation", "slotpin"]]

    def generate_filters(cols):


        ls = [
        html.Div([#filter options (dynamic)
            dcc.Dropdown(
                id=f"{filter}-filter",
                options=sorted([{'label': i, 'value': i} for i in df[filter].unique()], key=lambda x: x['value']),
                multi=True,
                placeholder=f"Filter by {filter.replace('_', ' ').capitalize()}",
                searchable=True,
                style={'height': '30px', 'width': '100%', 'marginBottom': '10px'}),
                ], style={'padding': '0px', 
                         'margin':'15px',
                          'backgroundColor': '#D3D3D3', 
                          'borderRadius': '5px',})
                for filter in cols
        ]

        card_content = ls
        card_title = dbc.CardHeader(
            html.H2("Filters", className="text-center", style={'fontWeight': 'bold'}),
            className="text-center", style={"padding":"2px"}
        )
        button_group = dbc.CardFooter(
    dbc.Row(
        dbc.Col(
            html.Div([
                html.P("Mode", className="text-center", style={'fontWeight': 'bold', 'margin-bottom':'2px'}),
                dbc.RadioItems(
                    id="radios",
                    className="btn-group",
                    inputStyle={"marginRight": "5px"},  # Optional, to add space between radio items
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "AND", "value": "and"},
                        {"label": "OR", "value": "or"},
                    ],
                    value="and",  # Ensure this matches one of the option values
                ),
                html.Div(id="output"),
            ], className="d-flex flex-column align-items-center"),  # Center content vertically
            width={"size": 3, "offset": 0},  # Adjust size and offset as needed for your layout
        ),
        justify="center",  # Center the column horizontally
    ),
    className="radio-group",
)


        # return html.Div([
        #     html.H2("Filters")]+
        #     ls)
        return dbc.Card(
            [card_title, dbc.CardBody(card_content), button_group],
            color="light",
            inverse=False,
            style={'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)', 'margin-top' : '30px', "padding":'5px'})

    fig = px.scatter(df, x='X', y='Y', hover_data=df[["name", "signal_type", "components", "pogozone"]],
                    color_discrete_sequence=['rgba(0,0,0,0)'], custom_data=df.columns.difference(['X', 'Y', 'absx', 'absy', 'relx', 'rely', 'pin_number']))


    fig.add_scatter(x=df['X'], y=df['Y'], mode='markers',
                                marker=dict(size=8, color='black', line=dict(width=1, color='black')), hoverinfo="skip")


    fig.update_layout(xaxis_title=None, yaxis_title=None,
                    xaxis_showgrid=False, yaxis_showgrid=False,
                    xaxis_zeroline=False, yaxis_zeroline=False,
                    xaxis_tickformat='', yaxis_tickformat='',
                    plot_bgcolor='#D3D3D3', paper_bgcolor='#D3D3D3',
                    showlegend=False,
                    xaxis=dict(
                        scaleanchor="y",
                        scaleratio=1,
                        showticklabels=False
                        ),
                    yaxis=dict(
                        showticklabels=False
                        ),
                        uirevision='constant')



    return fig, {}, generate_filters(cols_to_filter)
    


def read_table(name):
    conn = sqlite3.connect('hw.db')
    tbl = pd.read_sql(f"SELECT * FROM tbl_map_{name}", conn)
    conn.close()
    return tbl