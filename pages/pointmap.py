
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback, ALL, dash_table
from dash.exceptions import PreventUpdate
import dash
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
import itertools


from icecream import ic

ic.configureOutput(includeContext=True)

dash.register_page(__name__, path="/pointmap")



df = pd.DataFrame()
filters = []


layout = dbc.Container([
    dbc.Row([    
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="stored-filters"),
        dcc.Store(id="clicked-data"),
        dcc.Store(id="filtered-data"),
        dcc.Store(id="selected-data"),
        dcc.Store(id="map"),
        dbc.Col(
            html.Div([
                dbc.Card(id="filter-card", style={'margin-top': '30px', "padding": '5px', 'backgroundColor': '#D3D3D3', 'border-width': '0px'}),
                dbc.Card(id="buttons-card", style={'margin-top': '10px', "padding": '5px', 'backgroundColor': '#D3D3D3', 'border-width': '0px'}),
                dbc.Card(id="selection-card", style={'margin-top': '10px', "padding": '5px', 'backgroundColor': '#D3D3D3', 'border-width': '0px'}),
            ]),
            width=3
        ),
        dbc.Col(
            html.Div([
                dcc.Tabs(id="tabs", children=[
                    dcc.Tab(label='Scatter Plot', children=[
                        dcc.Graph(id='scatter-plot', style={'height': '100vh'})
                    ]),
                    dcc.Tab(label='Selected Data', id='selection-table'),
                ]),
            ]),
            width=9
        ),    
    ]),
])


@callback(
        [Output('map', 'data'),
        Output('stored-filters', 'data'),
        Output('filter-card', 'children'),
        Output('buttons-card', 'children')],
        Input('url', 'pathname'),
        State('selected-hardware', 'data'),
        
)
def load_map(url, pc):
    """
    NEEDS TO BE LOADED FIRST
    Loads map as records and creates the filter dict, for storing selected data and filters dropdowns creation

    Args:
        url (str): /pointmap
        pc (dict): selected pc data

    Returns:
        records, {filter :None}: data 
    """
    ic(url)
    if url == '/pointmap':
        if pc is not None:
            df = read_table(pc)
            ic(df)
            filters = [x for x in df.columns if x not in ["X", "Y", "pin_number", "pogolocation", "slotpin"]]
            filter_card = generate_filter_card({filter:None for filter in filters}, df)
            return [df.to_dict('records'), {filter:None for filter in filters}, filter_card, generate_buttons()]
    



def generate_filter_card(filters, data):
        df = data
        ls = [
        html.Div([
            dcc.Dropdown(
                id={'type': 'dynamic-filter', 'index': filter},
                options=sorted([{'label': i, 'value': i} for i in df[filter].unique()], key=lambda x: x['value']),
                multi=True,
                placeholder=f"Filter by {filter.replace('_', ' ').capitalize()}",
                searchable=True,
                style={'height': '30px', 'width': '100%', 'marginBottom': '10px'}),
                ], style={'padding': '0px', 
                         'margin':'0px',
                          'backgroundColor': '#D3D3D3', 
                          'borderRadius': '5px',})
                for filter in filters.keys()]+[dbc.Row(
                dbc.Col(
                    html.Div([
                        html.P("Mode", className="text-center", style={'fontWeight': 'bold', 'margin-bottom':'2px'}),
                            dbc.RadioItems(
                                id="radios-filtermode",
                                className="btn-group",
                                inputStyle={"marginRight": "5px"},  
                                inputClassName="btn-check",
                                labelClassName="btn btn-outline-primary",
                                labelCheckedClassName="active",
                                options=[
                                    {"label": "AND", "value": "and"},
                                    {"label": "OR", "value": "or"},],
                                value="or"),
                                ], className="d-flex flex-column align-items-center"), 
                    width={"size": 3, "offset": 0}),
                justify="center",
            className="radio-group")]+[
                    dbc.Row(
        dbc.Col(
            dbc.Button("From Datalog", id="from-datalog", className="mt-3", disabled=True),
            width=12,
            className="d-flex justify-content-center"
        )
    )]+[
        dbc.Row(
        dbc.Col(
            dbc.Button("Add to selection", id="add-filtered-to-selection", className="mt-3"),
            width=12,
            className="d-flex justify-content-center"
        )
    )]

        card_content = ls
        card_title = dbc.CardHeader(
            html.H2("Filters", className="text-center", style={'fontWeight': 'bold'}),
            className="text-center", style={"padding":"2px"}
        )

        return dbc.Card(
            [card_title, dbc.CardBody(card_content)],
            color="light",
            inverse=False,
            style={'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)'})


@callback(
    [Output('scatter-plot', 'figure'),
     Output('scatter-plot', 'clickData'),
     Output('filtered-data', 'data'),
     Output('add-filtered-to-selection', 'n_clicks')],
    [Input({'type': 'dynamic-filter', 'index': ALL}, 'value'), 
     Input('radios-filtermode', 'value'),
     Input('radios-view', 'value'),
     Input('radios-dutdisplay', 'value'),
     Input('clicked-data', 'data'),],
    [State('map', 'data'), 
     State('stored-filters', 'data'),
     State('url', 'pathname')
     ], prevent_initall_call=True)
def update_figure(selected_filters,filtermode,viewmode, dut_display, clicked_data, map, filters, pathname):
    if '/pointmap' not in pathname:
        raise PreventUpdate
    ic(filtermode)
    ic(viewmode)     
    ic(dut_display)
    ic(selected_filters)
    filtered = []
    df = pd.DataFrame.from_dict(map)



    #add base invisible for hobver data only
    fig = px.scatter(df, x='X', y='Y', hover_data=df[["name", "signal_type", "components", "pogozone"]],
                    color_discrete_sequence=['rgba(0,0,0,0)'], custom_data=df.columns.difference(['X', 'Y', 'absx', 'absy', 'relx', 'rely', 'pin_number']))

    #add black tips
    fig.add_scatter(x=df['X'], y=df['Y'], mode='markers',
                                marker=dict(size=8, color='black', line=dict(width=1, color='black')), hoverinfo="skip")

    def add_centers(scatter, data):#add site number
        data = data.rename(columns={"X":"absx", "Y":"absy", "dut":"site"})
        dfs = [data.loc[data.site==x] for x in range(data.site.max()+1)]
        d=[]
        for df in dfs:
            site = df.site.unique().tolist()[0]
            xmed = round((df.absx.min()+df.absx.max())/2,4)
            ymed = round((df.absy.min()+df.absy.max())/2,4)
            d.append({"site":site, "x":xmed, "y":ymed}) 
        df = pd.DataFrame.from_records(d)
        scatter.add_trace(go.Scatter(x=df['x'], y=df['y'], mode='markers+text',name="Sites",
                                    hoverinfo="none", text=df.site,
                                    textposition='middle center',
                                    marker=dict(size=30, color='white', line=dict(width=2)),
                                    textfont=dict(color='black', size=15)))
        
    def add_filters(scatter, data, filters, filtermode):
        
        df=data
        filters = {k:v for k, v in zip(filters.keys(), selected_filters)}
        if filtermode == 'or':
            for col, arg in filters.items():
                if arg:

                    filtered_df = df[df[col].isin(arg)]
                    scatter.add_scatter(x=filtered_df['X'], y=filtered_df['Y'], mode='markers',
                                            marker=dict(size=8, color='red', line=dict(width=1, color='Red')), hoverinfo="skip")
                    filtered.append(filtered_df.index.tolist())
        elif filtermode == "and":
            mask = pd.Series([True] * len(df[filters.keys()]))
            for col, arg in filters.items():
                if arg:
                    mask = mask & df[col].isin(arg)
            filtered_df = df.loc[mask]
            fig.add_scatter(x=filtered_df['X'], y=filtered_df['Y'], mode='markers',
                                marker=dict(size=8, color='red', line=dict(width=1, color='Red')), hoverinfo="skip")
            if len(filtered_df)>0:
                filtered.append(filtered_df.index.tolist())

    def add_selection(data, clicked_data):
        if clicked_data:
            
            _df = data.iloc[clicked_data]
            ic(_df)
            fig.add_scatter(x=_df['X'], y=_df['Y'], mode='markers',
                                        marker=dict(size=10, color='rgba(0,0,0,0)', line=dict(width=3, color='Green')), hoverinfo="skip")


    if dut_display == "on":
        add_centers(fig, df)
    add_filters(fig, df, filters, filtermode)
    add_selection(df, clicked_data)

    fig.update_layout(xaxis_title=None, yaxis_title=None,
                xaxis_showgrid=False, yaxis_showgrid=False,
                xaxis_zeroline=False, yaxis_zeroline=False,
                xaxis_tickformat='', yaxis_tickformat='',
                plot_bgcolor='#D3D3D3', paper_bgcolor='#D3D3D3',
                showlegend=False,
                xaxis=dict(
                    autorange='reversed' if viewmode=="tip" else True,
                    scaleanchor="y",
                    scaleratio=1,
                    showticklabels=False
                    ),
                yaxis=dict(
                    showticklabels=False
                    ),
                    uirevision=viewmode)


    return [fig, None, list(itertools.chain.from_iterable(filtered)), None]


def generate_buttons():

    content=[html.H4("View", className="text-center", style={'fontWeight': 'bold'}),
             dbc.Row(
                dbc.Col(
                    html.Div([
                            dbc.RadioItems(
                                id="radios-view",
                                className="btn-group",
                                inputStyle={"marginRight": "5px"},  
                                inputClassName="btn-check",
                                labelClassName="btn btn-outline-primary",
                                labelCheckedClassName="active",
                                options=[
                                    {"label": "Pad", "value": "pad"},
                                    {"label": "Tip", "value": "tip"},],
                                value="pad"),
                                ], className="d-flex flex-column align-items-center"), 
                    width={"size": 3, "offset": 0}),
                justify="center",
            className="radio-group"),
    dbc.Row(
                dbc.Col(
                    html.Div([
                        html.P("Sites", className="text-center", style={'fontWeight': 'bold', 'margin-bottom':'2px'}),
                            dbc.RadioItems(
                                id="radios-dutdisplay",
                                className="btn-group",
                                inputStyle={"marginRight": "5px"},  
                                inputClassName="btn-check",
                                labelClassName="btn btn-outline-primary",
                                labelCheckedClassName="active",
                                options=[
                                    {"label": "ON", "value": "on"},
                                    {"label": "OFF", "value": "off"},],
                                value="on"),
                                ], className="d-flex flex-column align-items-center"), 
                    width={"size": 3, "offset": 0}),
                justify="center",
            className="radio-group"),]
    
     
    return dbc.Card(content, color="light",
            inverse=False,
            style={'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)'})

@callback(
        Output('selection-card', 'children'),
        Input('selected-data', 'data'), 
        State('map', 'data'),
        prevent_initial_call = True
)
def generate_selection_card(selected_data, data):

    card_title = dbc.CardHeader(
            html.H4("Selection", className="text-center", style={'fontWeight': 'bold'}),
            className="text-center", style={"padding":"2px"}
        )
    ic(selected_data)
    if not selected_data:
        card_content= [html.P("No selected Data")]
    else:
        df = pd.DataFrame.from_records(data)
        df = df.iloc[selected_data]
        ic(df)
        if len(df) == 1:
            ic('len is 1')
            card_content = []
            for col, value in df.iloc[0].items():
                if col not in ['X', 'Y']:
                    ic(col, value)
                    card_content.append(html.Div([
                        html.Span(f"{col.replace('_', ' ').capitalize()}:", style={"font-weight": "bold"}),  # Column name in bold
                        html.Span(f" {value}")  # Value next to it
                    ]))
        else:
            ic('len is moar!')
            ic(df)
            card_content = [html.Div([
                        html.Span(f"{len(df)} Tips selected", style={"font-weight": "bold"}),  # Column name in bold
                        # html.Span(f" {value}")  # Value next to it
                    ])]
    
    card_content = card_content+[
        dbc.Row(
        dbc.Col(
            dbc.Button("TipDetective", id="create-vi", className="mt-3", href="/tipdetective"),
            width=12,
            className="d-flex justify-content-center"
        )
    )]

    return dbc.Card(
            [card_title, dbc.CardBody(card_content)],
            color="light",
            inverse=False,
            style={'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)'})

@callback([Output('clicked-data', 'data'),
    Output("selected-data", 'data')],
    [Input('scatter-plot', 'clickData'),
     Input('add-filtered-to-selection', 'n_clicks')],
    [State('clicked-data', 'data'), State('filtered-data', 'data')]
)
def update_click_data(clickData,nclicks, stored_data,filtered_data):
    ic(nclicks)
    if stored_data:
        ls = stored_data
    else:
        ls=[]
    if clickData is None and filtered_data is None:
        ic('all is None')
        return [None, None]
    if clickData is not None:
        clickedindex = clickData['points'][0]['pointIndex']
        if clickedindex in ls:
            ls.remove(clickedindex)
        else:
            ls.append(clickedindex)
    if nclicks == 1:
        ls = ls+filtered_data

    if len(ls) == 0 :#only one selected point, unselected
        return [None, None]
    return [ls, ls]

@callback(
    Output('selection-table', 'children'),
    Input('selected-data', 'data'),
    State('map', 'data'),
)
def update_table(selected_data, data):
    if selected_data is None:
        # Return empty table if no data is selected
        return []

    else:
        df = pd.DataFrame.from_records(data)

        selected_data = df.iloc[selected_data].to_dict('records')
        return dash_table.DataTable(
                        id='table',
                        data=selected_data,
        )
    

    


def read_table(name):
    conn = sqlite3.connect('hw.db')
    tbl = pd.read_sql(f"SELECT * FROM tbl_map_{name['id']}", conn)
    conn.close()
    return tbl























