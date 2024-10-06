import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import networkx as nx
from graph_creation import load_data, create_graph, query_nodes_with_min_deg
from graph_elements import generate_elements
import pandas as pd
import dash_bootstrap_components as dbc

# Create the Dash app
app = dash.Dash(__name__)

df = load_data('data/multiplatform_hashed_visuals.csv')
MIN_THRESHOLD = 100
MAX_THRESHOLD = 150
SLIDER_STEPS = 5
G = create_graph(df, MIN_THRESHOLD)
primary_nodes = query_nodes_with_min_deg(G, 20)

# initial_elements = generate_elements(G)

INITIAL_MIN_DEGREE = 150
LAYOUT_NAMES = [
    'grid',
    'random',
    'circle',
    'concentric',
    'breadthfirst',
    'cose',
]

app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Slider(
                MIN_THRESHOLD, MAX_THRESHOLD, SLIDER_STEPS,
                value=INITIAL_MIN_DEGREE,
                id="min-degree-slider",
            ),
            width=6
        ),
        dbc.Col(
            dbc.Select(
                id="graph-layout-select",
                value="cose",
                options=[
                    {"label": name.capitalize(), "value": name} 
                    for name in LAYOUT_NAMES
                ]
            ),
            width=6
        )
    ]),
    dbc.Row(cyto.Cytoscape(
        id='cytoscape-graph',
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '600px', "border-style": "groove"},
        elements=generate_elements(G, INITIAL_MIN_DEGREE)
    )),
    dbc.Row(
        html.Div(id='node-info', style={'margin-top': '20px'})
    )
])

@callback(
    Output("cytoscape-graph", "elements"),
    Input("min-degree-slider", "value")
)
def update_elements(min_degree):
    return generate_elements(G, min_degree)

@callback(
    Output("cytoscape-graph", "layout"),
    Input("graph-layout-select", "value")
)
def update_layout(layout):
    return {
        "name": layout,
        "animate": True
    }
    
@callback(
    Output("node-info", "children"),
    Input("cytoscape-graph", "tapNodeData")
)
def display_node_info(node_data):
    if node_data is None:
        return "Click on a node to see its information."
    
    # Return the information from the clicked node
    return f"""
        Node ID: {node_data['id']} \n
        Name: {node_data['name']}
        """

if __name__ == '__main__':
    app.run_server(debug=True)