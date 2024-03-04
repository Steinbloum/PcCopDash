import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3









# Function to read table remains unchanged
def read_table(name):
    conn = sqlite3.connect('hw.db')
    tbl = pd.read_sql(f"SELECT * FROM tbl_{name}", conn)
    conn.close()
    return tbl

idx = read_table("idx")
table = idx.to_dict('records')


navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Dash App", href="#"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="#")),
                    dbc.NavItem(dbc.NavLink("Page 1", href="#")),
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("More pages", header=True),
                            dbc.DropdownMenuItem("Page 2", href="#"),
                            dbc.DropdownMenuItem("Page 3", href="#"),
                        ],
                        nav=True,
                        in_navbar=True,
                        label="More",
                    ),
                ],
                className="ms-auto",  # Aligns the navigation items to the right
            ),
        ],
        fluid=True,  # Container takes up the full width of the Navbar
    ),
    color="light",
    dark=False,
)


# Use the SPACELAB theme from Bootswatch
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

app.layout = dbc.Container([
    navbar,
    dcc.Download(id="download-dataframe-csv")
,
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Div(id='cell-click-output'),
                dbc.Button("Validate Selection", id="validate-button", style={"marginTop": 20, "display": "none"}),
                html.Div(id='validation-output', style={'marginTop': 20})
            ], style={'position': 'fixed', 'top': 0, 'left': 0, 'bottom': 0, 'width': '20%', 'padding': '20px', 'background-color': '#f8f9fa'}),
        ], width=3),
        dbc.Col([
            dash_table.DataTable(
    id='hw-index',
    columns=[
        {"name": i, "id": i, "type": "numeric" if idx[i].dtype in ['int64', 'float64'] else "text"}
        for i in idx.columns
    ],
    data=table,
    filter_action="native",  # Ensure native filtering is enabled
    sort_action="native",
    sort_mode="single",
    page_action="native",
    page_current=0,
    page_size=10,
)
,
            html.Div([
                dbc.Button("Export CSV", id="export-csv", className="mt-2", color="primary"),
            ], className="d-grid gap-2 col-2 mx-auto mt-3"),  # Center the button below the table
        ], width=9),
    ], className="g-0"),
], fluid=True)


@app.callback(
    Output('cell-click-output', 'children'),
    [Input('hw-index', 'active_cell')],
    [State('hw-index', 'data')]
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

    # Apply the glow effect directly via the style parameter
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

@app.callback(
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






if __name__ == "__main__":
    app.run_server()
