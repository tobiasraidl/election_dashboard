import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import networkx as nx
from graph_creation import load_data, create_people_graph, create_cluster_graph
from graph_elements import generate_elements
import pandas as pd
import dash_bootstrap_components as dbc
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = load_data('data/multiplatform_hashed_visuals.csv', config)
MIN_CLUSTER_SIZE = 20
MAX_CLUSTER_SIZE = 150
CLUSTER_SIZE_SLIDER_STEPS = 5
INITIAL_MIN_CLUSTER_SIZE = 20
G_people = create_people_graph(df)
G_clusters = create_cluster_graph(G_people, MIN_CLUSTER_SIZE)

# initial_elements = generate_elements(G)
LAYOUT_NAMES = [
    'grid',
    'random',
    'circle',
    'concentric',
    'breadthfirst',
    'cose',
]



graph_element = cyto.Cytoscape(
    id='cluster-graph',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '600px', "border-style": "groove"},
    elements=generate_elements(G_clusters, INITIAL_MIN_CLUSTER_SIZE),
    stylesheet=[
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
    MIN_CLUSTER_SIZE, MAX_CLUSTER_SIZE, CLUSTER_SIZE_SLIDER_STEPS,
    value=INITIAL_MIN_CLUSTER_SIZE,
    id="min-cluster-size-slider",
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


# @callback(
#     Output("cluster-graph", "elements"),
#     Input("min-cluster-size-slider", "value")
# )
# def update_elements(min_size):
#     return generate_elements(G_clusters, min_size)

# @callback(
#     Output("cluster-graph", "layout"),
#     Input("graph-layout-select", "value")
# )
# def update_layout(layout):
#     if layout == "cose":
#         return {
#             'name': 'cose',
#             'nodeRepulsion': 4000,  # Adjusts repulsion force between nodes
#             'idealEdgeLength': 100,  # Sets the ideal length for edges
#             'edgeElasticity': 100,    # Determines how much edges resist stretching
#             'nestingFactor': 5,       # Defines how much nesting is considered in the layout
#             'gravity': 10, 
#         }
#     else:
#         return {
#             "name": layout,
#             "animate": True
#         }
    
# @callback(
#     Output("node-info", "children"),
#     Input("cluster-graph", "tapNodeData")
# )
# def display_node_info(node_data):
#     if node_data is None:
#         return "Click on a node to see its information."
    
#     # Return the information from the clicked node
#     card =  [
#                 html.H4(f"Name: {node_data['name']}", className="card-title"),
#                 html.H6(f"Partei: {node_data['party']}", className="card-subtitle"),
#                 html.P(f"User ID: {node_data['id']}", className="card-text"),
#             ]
#     return card

if __name__ == '__main__':
    app.run_server(debug=True)