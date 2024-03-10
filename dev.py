import pandas as pd
from env import *
import plotly.graph_objs as go
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
from random import choice
from helpers.DbManager import DbManager
import pandas as pd
import json





#Create Data
dbm = DbManager(PATH_TO_DB)
wso = 1
print(dbm.getAllTablesList())
df = dbm.getWholeTable(f"tbl_map_{wso}")
comps = ["COMPONENT" + str(x) for x in range(70)]
comps = [x if x !="COMPONENT0" else "DIRECT ROUTE" for x  in comps]
pogozone = ["A", "B", "C", "D", "E", "F"]
df["comps"] = [choice(comps) for n in range(len(df))]
df["pogozone"] = [choice(pogozone) for n in range(len(df))]
df = df.rename(columns={"Pad Name": 'Name'})
print(df)
idx = dbm.getWholeTable(f"tbl_index")
pcData = idx.loc[idx.wso == wso].to_dict("records")[0]





# Initialize the Dash app
app = dash.Dash(__name__)
app.title = f'{wso} TipMap'

FILTERS = df.columns.difference(['X', 'Y', 'absx', 'absy', 'relx', 'rely', 'pin_number']).tolist()
app.stored_data = []
app.layout = html.Div([
    html.Div(id='stored-data', style={'display': 'none'}),
    html.Div(id='stored-filters', style={'display': 'none'}),
    html.Div([dcc.Graph(id='scatter-plot', style={'height': '100vh'})], style={'flex': '4'}),
    html.Div(
        [
        dcc.RadioItems( #Pad/Tipview switch
            id='invert-x-axis',
            options=[
                {'label': 'Pad View', 'value': 'normal'},
                {'label': 'Tip View', 'value': 'invert'}],
            value='normal',
            labelStyle={'display': 'block'},
            style={'padding': '5px', 'marginBottom': '10px', 'backgroundColor': '#999696', 'borderRadius': '5px'}),

        dcc.RadioItems( #filter mode
            id='filter-mode',
            options=[
                {'label': 'Add', 'value': 'add'},
                {'label': 'Intersect', 'value': 'intersect'}
            ],
            value='add',
            labelStyle={'display': 'block'},
            style={'padding': '5px', 'marginBottom': '10px', 'backgroundColor': '#999696', 'borderRadius': '5px'}
            ),
        ] + 
        [
        html.Div([#filter options (dynamic)
            dcc.Dropdown(
                id=f"{filter}-filter",
                options=sorted([{'label': i, 'value': i} for i in df[filter].unique()], key=lambda x: x['value']),
                multi=True,
                placeholder=f"Filter by {filter}",
                searchable=True,
                style={'height': '30px', 'width': '100%', 'marginBottom': '10px'}),
                ], style={'padding': '20px', 
                          'marginBottom': '10px', 
                          'backgroundColor': '#999696', 
                          'borderRadius': '5px'})
                for filter in FILTERS
        ] + 
        [
        html.Button(
            f"Clear Selection", 
            id=f"clear-selection",
            n_clicks=0, 
            style={'margin': '5px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 
                   'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'}
                   ) ,
        html.Button(
            f"Add Filtered", 
            id=f"add-filtered",
            n_clicks=0, 
            style={'margin': '5px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 
                   'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'}
                   ) ,
        ] +
        [
        html.Div(id='selected-point-data', 
                 style={'margin': '20px', 
                        'padding': '5px 10px', 
                        'backgroundColor': 
                        '#999696',
                        # 'border': '2px solid #007BFF', 
                        'borderRadius': '5px',
                        'boxShadow': 'inset 0 0 20px rgba(0,0,0,0.8)'})],
    style={'flex': '1', 'overflowY': 'scroll', 'maxHeight': '100vh', 'backgroundColor': '#999696', 'padding': '20px'},
        ),],
style={'display': 'flex', 'flexDirection': 'row'})


inputlist = [
    Input('scatter-plot', 'clickData'),
    Input('invert-x-axis', 'value'),
    Input('filter-mode', 'value'),
    Input('stored-data', 'children')
]
for filter in FILTERS:
    inputlist.append(Input(f'{filter}-filter', 'value'))

@app.callback(
    [Output('scatter-plot', 'figure'),
    Output('stored-filters', 'children')],
    inputlist
)



def update_figure(clickData, invert_x_axis, filter_mode, stored_data_json, *args):

    # this initial scatter is transparent and is used for simple hover data display
    fig = px.scatter(df, x='absx', y='absy', hover_data=df[["Name", "Signal Type", "comps", "pogozone"]],
                    color_discrete_sequence=['rgba(0,0,0,0)'], custom_data=df.columns.difference(['X', 'Y', 'absx', 'absy', 'relx', 'rely', 'pin_number']))


    fig.add_scatter(x=df['absx'], y=df['absy'], mode='markers',
                                marker=dict(size=8, color='black', line=dict(width=1, color='black')), hoverinfo="skip")
    #add filters
    if filter_mode == "add":

        for filter, arg in zip(FILTERS,args):
            if arg:
                filtered_df = df[df[filter].isin(arg)]
                fig.add_scatter(x=filtered_df['absx'], y=filtered_df['absy'], mode='markers',
                                marker=dict(size=8, color='red', line=dict(width=1, color='Red')), hoverinfo="skip")
                filterData = filtered_df.to_dict('records')
                
    elif filter_mode == "intersect":
            filter_values = list(args)
            mask = pd.Series([True] * len(df))
            for filter, arg in zip(FILTERS, filter_values):
                if arg:
                    mask = mask & df[filter].isin(arg)
            filtered_df = df.loc[mask]
            fig.add_scatter(x=filtered_df['absx'], y=filtered_df['absy'], mode='markers',
                                marker=dict(size=8, color='red', line=dict(width=1, color='Red')), hoverinfo="skip")
            print(filtered_df)
            filterData = filtered_df.to_dict("records")
    
    if clickData:
        stored_data = json.loads(stored_data_json) if stored_data_json else []
        if len(stored_data)==0:
            print("Empty datalist")
        else:
            # stored_data.append(clicked_data)
            print(pd.DataFrame(stored_data))
            
            _df = pd.DataFrame(stored_data)        
            # Highlight the clicked point by adding it as a separate trace with different styling
            fig.add_scatter(x=_df['absx'], y=_df['absy'], mode='markers',
                                    marker=dict(size=10, color='rgba(0,0,0,0)', line=dict(width=3, color='Green')), hoverinfo="skip")
        
    if invert_x_axis == 'invert':
        fig.update_layout(xaxis=dict(autorange='reversed'))
        


    # Adjustments for axis, layout, and removing legends
    fig.update_layout(xaxis_title=None, yaxis_title=None,
                    xaxis_showgrid=False, yaxis_showgrid=False,
                    xaxis_zeroline=False, yaxis_zeroline=False,
                    xaxis_tickformat='', yaxis_tickformat='',
                    plot_bgcolor='#999696', paper_bgcolor='#999696',
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
    try:
        stored_data = json.dumps(filterData)
    except UnboundLocalError:
        stored_data = json.dumps([])
    return fig, stored_data


@app.callback(
    Output('stored-data', 'children'),
    Input('scatter-plot', 'clickData'),
    State('stored-data', 'children')
)
def accumulate_selections(clickData, stored_data_json):
    if clickData:
        # Deserialize the stored data or initialize it if not present
        stored_data = json.loads(stored_data_json) if stored_data_json else []

        # Extract clicked point data (consider including unique identifier or index)
        clicked_point_index = clickData['points'][0]['pointIndex']
        clicked_data = df.iloc[clicked_point_index].to_dict()

        # Append the new selection
        stored_data.append(clicked_data)

        # Serialize and return the updated selections
        return json.dumps(stored_data)
    return stored_data_json  # Return existing data if no clickData


# Callback to clear selection, assuming you have a button with id="clear-selection"
@app.callback(
    Output('stored-data', 'children', allow_duplicate=True),
    Input('clear-selection', 'n_clicks'),
    prevent_initial_call=True
)
def clear_selection(n_clicks):
    print("clear clicked")
    return None


# Callback to display selected point data
@app.callback(
    Output('selected-point-data', 'children'),
    [Input('stored-data', 'children')])

def display_selected_data(stored_data_json):

    data = json.loads(stored_data_json) if stored_data_json else []

    details_list = []
    if len(data)>1:
        details_list.append(
                html.P(
                    children=[html.Strong("Selection options")],
                    style={
                        'text-align': 'center',  # Centers the text
                        'font-weight': 'bold',   # Makes the text bold
                        # 'text-decoration': 'underline',  # Underlines the text
                        'color': 'black',  # Sets the text color to blue
                        'fontSize':'1.2em'
                    }
                ))
        df = pd.DataFrame.from_records(data)
        common = {}
        for col in df.columns:
            if len (df[col].unique())==1:
                common[col]=df[col].iloc[0]
        point_details = f"{len(data)} tips selected"
        details_list.append(html.P(point_details))
        if len(common)>1:
            details_list.append(html.P(html.Strong(f"Common attributes : ")))
            for k, v in common.items():
                details_list.append(html.P([html.Strong(f"{k}: "), f"{v}"]))

        return html.Div(details_list+[
        html.Button(
            f"Export data", 
            id=f"export-data",
            n_clicks=0, 
            style={'margin': '5px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 
                   'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'}
                   ),
        html.Button(
            f"TipInspector Program", 
            id=f"create-program",
            n_clicks=0, 
            style={'margin': '5px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 
                   'padding': '10px', 'borderRadius': '5px', 'cursor': 'pointer'}
                   )           
        ])
            
    elif len(data) == 1:
        details_list.append(
                html.P(
                    children=[html.Strong("Tip Data")],
                    style={
                        'text-align': 'center',  # Centers the text
                        'font-weight': 'bold',   # Makes the text bold
                        # 'text-decoration': 'underline',  # Underlines the text
                        'color': 'blue',  # Sets the text color to blue
                    }
                ))
        point_info = data[0]

        for detail_index, detail_value in point_info.items():
            if detail_index not in ['X', 'Y', "absx", "absy", "relx", "rely","pin_number"]:
                formatted_index = detail_index.replace('_', ' ').capitalize()
                details_list.append(
                    html.P([html.Strong(f"{formatted_index}: "), f"{detail_value}"],
                           )
                )
                # print("detail list",details_list)
        return html.Div(details_list)
    details_list.append(
                html.P(
                    children=[html.Strong("Probecard Data")],
                    style={
                        'text-align': 'center',  # Centers the text
                        'font-weight': 'bold',   # Makes the text bold
                        # 'text-decoration': 'underline',  # Underlines the text
                        'color': 'black',  # Sets the text color to blue
                        'fontSize':'1.5em'
                    }
                ))
    for k, v in pcData.items():#add data
        formatted_index = k.replace('_', ' ').capitalize()
        details_list.append(
                html.P([html.Strong(f"{formatted_index}: "), f"{v}"],
                       style={"margin":"5px"})
                )
                # print("detail list",details_list)
    return html.Div(details_list)

@app.callback(
    Output('stored-data', 'children', allow_duplicate=True),
    Input('add-filtered', 'n_clicks'),
    [State('stored-filters', 'children'),
     State('stored-data', 'children')],
    prevent_initial_call=True)

def add_filtered(n_clicks, stored_filters_json, stored_data_json):
    print("add filtered clicked")
    filters = json.loads(stored_filters_json) if stored_filters_json else []
    selec = json.loads(stored_data_json) if stored_data_json else []
    if len(filters) > 0:
        selec += filters
        selec = json.dumps(selec)
    return selec




app.run_server(debug=True)
