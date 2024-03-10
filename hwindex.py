import dash
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from dash.exceptions import PreventUpdate



dash.register_page(__name__)

# Function to read table remains unchanged
def read_table(name):
    conn = sqlite3.connect('hw.db')
    tbl = pd.read_sql(f"SELECT * FROM tbl_{name}", conn)
    conn.close()
    return tbl

idx = read_table("idx")
table = idx.to_dict('records')



layout = dbc.Container([
    dcc.Store(id='temp-data'),
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        # Side pane column
        dbc.Col(html.Div([
            html.H4(id="side-pane-content", className="p-2 text-center"), 
        ]), width=3, style={"height": "100vh", "margin-top":"15vh"}),  
        
        # Main content column
        dbc.Col([
            html.Div([
                html.H2("Available Probecards", className="p-2 text-center", style={'fontWeight': 'bold'}),
                html.Div([
                    dash_table.DataTable(
                        id='hw-index',
                        columns=[{"name": i.replace("_", " ").capitalize(), "id": i, "type": "numeric" 
                                  if idx[i].dtype in ['int64', 'float64'] 
                                  else "text"} 
                                    for i in [x for x in idx.columns if not x.lower() in ["inspectorready", "inspections_count"]]],
                        data=table,
                        filter_action="native",
                        filter_options={"placeholder_text": ""},
                        sort_action="native",
                        sort_mode="single",
                        page_action="native",
                        page_current=0,
                        page_size=20,
                        style_as_list_view=True,
                        style_data={
                            'color': 'black',
                            'backgroundColor': 'white'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'even'},
                                'backgroundColor': 'rgb(207, 204, 204)',
                            },
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(194, 194, 194)',
                            },
                            {
                                'if': {'state': 'selected'},
                                'backgroundColor': 'rgba(0, 0, 0, 0)',
                                'border': '1px solid blue'
                            }
                        ],
                        style_header={
                            'backgroundColor': 'rgb(210, 210, 210)',
                            'color': 'black',
                            'fontWeight': 'bold'
                        },
                        style_filter={  # Add this property to your DataTable
                            'backgroundColor': 'rgb(230, 230, 230)',  # Example filter cell background color
                            'color': 'black',  # Text color for the filter cell
                            'fontWeight': 'bold',  # Make filter text bold
                        },
                    ),
                ], style={'padding': '15px', 'border': '1px solid #dee2e6', 'borderRadius': '5px', "margin":"10px"}), 
                html.Div([
                    dbc.Button("Export CSV", id="export-csv", className="mt-2", color="primary", style={"margin":"10px"}),
                ], className="d-grid gap-2 col-3 mx-auto mt-3")
            ],className="justify-content-center", style={"color":"secondary",
                        'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)',
                        "margin":"15px",
                        "borderRadius":"5px",
                        }),
                        
        ], width=9), 
    ]),
], fluid=True)



@callback(
    [Output('side-pane-content', 'children'),Output('selected-hardware', 'data')],
    [Input('hw-index', 'active_cell')],
    [State('hw-index', 'data')],
    )

def display_cell_value(active_cell, rows):
    if not active_cell:
        print("no active cell")
        return dbc.Card(
            "Select Hardware",
            color="light",
            inverse=False,
            body=True,
            style={
                'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)',  # Glow effect
            }
        ), "NO Active Cell"

    row = active_cell['row']
    selected_row_data = rows[row]
    dump = selected_row_data
    print(f"{dump} dump")

    card_content = generate_card_content(selected_row_data)
    card_title = dbc.CardHeader(
        html.H4(f"Probecard {selected_row_data.get('id', 'N/A')}", className="text-center", style={'fontWeight': 'bold'}),
        className="text-center"
    )
    card_footer = dbc.CardFooter(
    dbc.Row(
        dbc.Col(
            dbc.Button("View Map", id="view-map-button", href="/pointmap" ,color="primary", className="mx-auto", style={"display": "block"}, outline=False),
            className="text-center",  # Ensures the column content is centered
            width=12,
        ),
        justify="center",  # This centers the Row, should the Col not take full width
        className="mt-2",  # Adds top margin for spacing
        
    ))

    return dbc.Card(
        [card_title, dbc.CardBody(card_content), card_footer],
        color="light",
        inverse=False,
        style={'boxShadow': '0 0 15px rgba(0, 14, 111, 0.8)'}),selected_row_data

def generate_card_content(data):
    print(data)
    attributes_to_include = ['family', 'rack', 'tech', 'dut_count']
    card_content = []

    # Generate attribute rows
    for key in attributes_to_include:
        if key in data:
            formatted_key = key.replace('_', ' ').capitalize()
            value = data[key]

            card_content.append(
                dbc.Row(
                    dbc.Col(html.Div([
                        html.B(f"{formatted_key}: ", style={'fontSize': '0.65em'}),
                        html.Span(f"{value}", style={'fontSize': '0.65em'})
                    ]),
                    width="auto", className="mx-auto"),
                    className="justify-content-center",
                )
            )
    
    # Check conditions for badges and append accordingly
    if "inspectorReady" in data and data["inspectorReady"]:
        inspector_ready_badge = html.H6([dbc.Badge("Inspector Ready", color="success", className="me-1", pill=True)])
        card_content.append(dbc.Row(dbc.Col(inspector_ready_badge, width="auto"), className="justify-content-center"))
    else:
        inspector_not_ready_badge = html.H6([dbc.Badge("Inspector Ready", color="danger", className="me-1", pill=True)])
        card_content.append(dbc.Row(dbc.Col(inspector_not_ready_badge, width="auto"), className="justify-content-center"))

    if "inspections_count" in data and data["inspections_count"] > 0:
        inspections_count_badge = html.H6([dbc.Badge("Results", color="success", className="me-1", pill=True)])
        card_content.append(dbc.Row(dbc.Col(inspections_count_badge, width="auto"), className="justify-content-center"))
    else:
        inspections_count_badge_neg = html.H6([dbc.Badge("Results", color="danger", className="me-1", pill=True)])
        card_content.append(dbc.Row(dbc.Col(inspections_count_badge_neg, width="auto"), className="justify-content-center"))
    return card_content

@callback(
    Output("download-dataframe-csv", "data"),
    [Input("export-csv", "n_clicks")],
    [State("hw-index", "derived_virtual_data")]
)
def export_csv(n_clicks, filtered_data):
    if n_clicks is None or filtered_data is None:
        raise PreventUpdate

    # Convert the filtered data to a DataFrame
    filtered_df = pd.DataFrame(filtered_data)

    # Convert the DataFrame to a CSV and trigger the download
    return dcc.send_data_frame(filtered_df.to_csv, filename="filtered_hardware_data.csv", index=False)

