import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import networkx as nx
from graph_creation import load_data, create_graph, query_nodes_with_min_deg
from graph_elements import generate_elements
import pandas as pd
import dash_bootstrap_components as dbc
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = load_data('data/multiplatform_hashed_visuals.csv', config)
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

graph_element = cyto.Cytoscape(
    id='cytoscape-graph',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '600px', "border-style": "groove"},
    elements=generate_elements(G, INITIAL_MIN_DEGREE),
    stylesheet=[
        {
            "selector": "node",
            "style": {
                'width': 'mapData(degree, 100, 250, 50, 100)',  # Map degree (min 1, max 3) to size (20 to 60px)
                'height': 'mapData(degree, 100, 250, 50, 100)',  # Map height similarly
                'border-color': 'black',
                'border-style': 'solid',
                'border-opacity': 1
            }
        },
        {
            "selector": "edge",
            "style": {
                "width": 5,
                "line-color": "#f0f0f0"
            }
        }
    ]
)


slider_element = dcc.Slider(
    MIN_THRESHOLD, MAX_THRESHOLD, SLIDER_STEPS,
    value=INITIAL_MIN_DEGREE,
    id="min-degree-slider",
)

select_label_element = dbc.Label("Layout:", html_for="graph-layout-select")

select_element = dbc.Select(
    id="graph-layout-select",
    value="cose",
    options=[
        {"label": name.capitalize(), "value": name} 
        for name in LAYOUT_NAMES
    ]
)

node_info_element = dbc.Card(
    dbc.CardBody(
        id="node-info",
        children=[]
    )
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([graph_element], width="8", className="mb-3"),
                dbc.Col(
                    [
                        dbc.Row([slider_element], align="center", className="mb-3"),
                        dbc.Row([dbc.Col([select_label_element]), dbc.Col([select_element])], align="center", className="mb-3"),
                        dbc.Row([node_info_element], className="mb-3")
                    ],
                    width="4",
                    className="mb-3"
                ),
            ], 
            style={"height": "400px"},
            className="mb-4"
        )
    ],
    fluid=True,
    style={"padding": "20px"}
)


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
    if layout == "cose":
        return {
            'name': 'cose',
            'nodeRepulsion': 4000,  # Adjusts repulsion force between nodes
            'idealEdgeLength': 100,  # Sets the ideal length for edges
            'edgeElasticity': 100,    # Determines how much edges resist stretching
            'nestingFactor': 5,       # Defines how much nesting is considered in the layout
            'gravity': 10, 
        }
    else:
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
    card =  [
                html.H4(f"Name: {node_data['name']}", className="card-title"),
                html.H6(f"Partei: {node_data['party']}", className="card-subtitle"),
                html.P(f"User ID: {node_data['id']}", className="card-text"),
            ]
    return card

if __name__ == '__main__':
    app.run_server(debug=True)