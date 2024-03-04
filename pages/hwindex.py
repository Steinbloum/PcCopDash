import dash
from dash import html, dcc, dash_table, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3



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

    dbc.Row([

        dbc.Col([
    html.Div([
        html.H4("Select your hardware", className="p-2 text-center"),  # Header with padding and centered text
        html.Div([
            dash_table.DataTable(
                id='hw-index',
                columns=[{"name": i.replace("_", " ").capitalize(), "id": i, "type": "numeric" if idx[i].dtype in ['int64', 'float64'] else "text"} for i in idx.columns],
                data=table,
                filter_action="native",
                filter_options={"placeholder_text": "Filter"},
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
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(220, 220, 220)',
                    },
                    # Style for selected cell
                    {
                        'if': {'state': 'selected'},  # Applies to both cell and row selection
                        'backgroundColor': 'rgba(0, 116, 217, 0.3)',  # Light blue
                        'border': '1px solid blue'
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(210, 210, 210)',
                    'color': 'black',
                    'fontWeight': 'bold'
                }

            ),
        ], style={'padding': '20px', 'border': '1px solid #dee2e6', 'borderRadius': '5px', "margin":"10px"}), 
        html.Div([
            dbc.Button("Export CSV", id="export-csv", className="mt-2", color="primary", style={"margin":"10px"}),
        ], className="d-grid gap-2 col-3 mx-auto mt-3"),  # Adjusted for button centering
    ], style={  "color":"secondary",
                'boxShadow': '0 0 8px rgba(0, 14, 111, 0.8)',
                "margin":"20px",
                "border-radius":"5px"}),
], width=12),
    ]),
], fluid=True)


@callback(
    Output('side-pane-content', 'children'),
    [Input('hw-index', 'active_cell')],
    [State('hw-index', 'data')],
)
def display_cell_value(active_cell, rows):


    if not active_cell:
        return dbc.Card(
            "Select Hardware",
            color="light",
            inverse=False,
            body=True,
            style={
                'boxShadow': '0 0 8px rgba(0, 14, 111, 0.8)',  # Glow effect
            }
        )

    row = active_cell['row']
    selected_row_data = rows[row]

    card_content = generate_card_content(selected_row_data)

    # Center the card title
    card_title = dbc.CardHeader(
        f"Hardware {selected_row_data.get('id', 'N/A')}",
        className="text-center"
    )

    # Center the "View Map" button in the card footer
    card_footer = dbc.CardFooter(
    dbc.Row(
        dbc.Col(
            dbc.Button("View Map", id="view-map-button", color="primary", className="mx-auto", style={"display": "block"}),
            className="text-center",  # Ensures the column content is centered
            width=12,
        ),
        justify="center",  # This centers the Row, should the Col not take full width
        className="mt-2",  # Adds top margin for spacing
    )
)

    return dbc.Card(
        [card_title, dbc.CardBody(card_content), card_footer],
        color="light",
        inverse=False,
        style={
            'boxShadow': '0 0 8px rgba(0, 14, 111, 0.8)',  # Glow effect
        }
    )



def generate_card_content(data):
    # Define the attributes to include
    attributes_to_include = ['family', 'rack', 'tech', 'dut_count']
    
    # Filter and prepare the content
    card_content = []
    for key in attributes_to_include:
        # Check if key exists in data to avoid KeyError
        if key in data:
            # Format the attribute name
            formatted_key = key.replace('_', ' ').capitalize()
            value = data[key]
            
            # Add the formatted attribute name and value to the card content
            card_content.append(
                dbc.Row(
                    dbc.Col(html.Div([html.B(f"{formatted_key}: "), f"{value}"]),
                            width={"size": 6, "offset": 3}),
                    className="text-center"
                )
            )
    
    return card_content

from dash.exceptions import PreventUpdate

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


