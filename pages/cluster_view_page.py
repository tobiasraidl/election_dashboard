import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import networkx as nx
from graph_creation import load_data, create_people_graph, create_cluster_graph
from graph_elements import generate_cluster_graph_elements, generate_connection_graph_elements
import pandas as pd
import dash_bootstrap_components as dbc
import yaml
import plotly.graph_objs as go

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

dash.register_page(__name__, path='/cluster-view')

df = load_data('data/multiplatform_hashed_visuals.csv', config)
MIN_CLUSTER_SIZE = 25
MAX_CLUSTER_SIZE = 50
CLUSTER_SIZE_SLIDER_STEPS = 5
INITIAL_MIN_CLUSTER_SIZE = 30

G_people = create_people_graph(df)
G_clusters = create_cluster_graph(G_people, MIN_CLUSTER_SIZE)
LAYOUT_NAMES = [
    'grid',
    'random',
    'circle',
    'concentric',
    'breadthfirst',
    'cose',
]

cluster_graph_element = cyto.Cytoscape(
    id='cluster-graph',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '700px', "border-style": "groove"},
    elements=generate_cluster_graph_elements(config, G_clusters, INITIAL_MIN_CLUSTER_SIZE),
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

connection_graph_element = cyto.Cytoscape(
        id='connection-graph',
        layout={"name": "breadthfirst", 'roots': ["cluster-left"], 'direction': 'LR', 'animate': True},
        style={'width': '100%', 'height': '700px', "border-style": "groove"},
        elements = []
)

connection_graph_node_info_element = dbc.Card(
    dbc.CardBody(
        id="connection-graph-node-info",
        children=[]
    )
)

layout = dbc.Container(
    [
        dcc.Location(id="location", refresh=True),
        dbc.Row(
            [
                html.H4("Cluster View"),
                dbc.Col(
                    [
                        cluster_graph_element, 
                    ], 
                    width="8", 
                    className="mb-3",
                ),
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
            className="mb-4"
        ),
        dbc.Row([
            html.H4(id="connection-view-title", children="Click an edge, to display connection view"),
            dbc.Col([
                connection_graph_element,
            ], width="8", className="mb-3"),
            dbc.Col(connection_graph_node_info_element, width="4", className="mb-3"),
        ])
    ],
    fluid=True,
    style={"padding": "20px"}
)


@callback(
    Output("cluster-graph", "elements"),
    Input("min-cluster-size-slider", "value")
)
def update_elements(min_size):
    return generate_cluster_graph_elements(config, G_clusters, min_size)

@callback(
    Output("cluster-graph", "layout"),
    Input("graph-layout-select", "value")
)
def update_layout(layout):
    return {
        "name": layout,
        "animate": True
    }

@callback(
    Output("node-info", "children"),
    Input("cluster-graph", "tapNodeData")
)
def display_node_info(node_data):
    if node_data is None:
        return "Click on a node to see its information."
    
    sorted_ratios = dict(sorted(node_data["party_ratios"].items(), key=lambda item: item[1], reverse=True))
    x_data = list(sorted_ratios.keys())
    y_data = list(sorted_ratios.values())
    colors_sorted = [config["party_color_map"][key] for key in sorted_ratios.keys()]
    fig = go.Figure(data=[go.Bar(x=x_data, y=y_data, marker_color=colors_sorted)])
    fig.update_layout(
        title='Party Membership Ratios',
        xaxis_title='Parties',
        yaxis_title='Ratio',
        dragmode=False,
    )
    
    card =  [
                html.H4(f"Cluster ID: {node_data['id']}", className="card-title"),
                html.H6(f"Size: {node_data['size']} people", className="card-subtitle"),
                dcc.Graph(id='party-ratio-plot', figure=fig),
            ]
    return card

@callback(
    [
        Output('location', 'href'),
        Output('connection-graph', 'elements'),
        Output('connection-view-title', 'children')
    ], 
    Input('cluster-graph', 'tapEdgeData')
)
def display_connection_graph(edgeData):
    if edgeData is None:
        return "#", [], "Click an edge to display cluster connection view"
    
    cluster1_details = {
        "id": edgeData["source"], 
        "nodes": G_clusters.nodes[int(edgeData["source"])]["nodes"],
        "size": G_clusters.nodes[int(edgeData["source"])]["size"],
        "party_ratios": G_clusters.nodes[int(edgeData["source"])]["party_ratios"],
    }
    cluster2_details = {
        "id": edgeData["target"], 
        "nodes": G_clusters.nodes[int(edgeData["target"])]["nodes"],
        "size": G_clusters.nodes[int(edgeData["target"])]["size"],
        "party_ratios": G_clusters.nodes[int(edgeData["target"])]["party_ratios"],
    }
    return "#connection-view-title", generate_connection_graph_elements(
        config,
        G_people, 
        cluster1_details,
        cluster2_details
    ), "Cluster Connection View"
    
@callback(
    Output("connection-graph-node-info", "children"),
    Input("connection-graph", "tapNodeData")
)
def display_node_info(node_data):
    if node_data is None:
        return "Click a node to see its details."
    if node_data['id'].startswith("cluster"):
        sorted_ratios = dict(sorted(node_data["party_ratios"].items(), key=lambda item: item[1], reverse=True))
        x_data = list(sorted_ratios.keys())
        y_data = list(sorted_ratios.values())
        colors_sorted = [config["party_color_map"][key] for key in sorted_ratios.keys()]
        fig = go.Figure(data=[go.Bar(x=x_data, y=y_data, marker_color=colors_sorted)])
        fig.update_layout(
            title='Party Membership Ratios',
            xaxis_title='Parties',
            yaxis_title='Ratio',
            dragmode=False,
        )
        return  [
            html.H4(f"Cluster ID: {node_data['cluster-graph-id']}", className="card-title"),
            html.H6(f"Size: {node_data['size']} people", className="card-subtitle"),
            dcc.Graph(id='party-ratio-plot', figure=fig),
        ]
        
    else:
        return [
            html.H4(f"Name: {node_data['name']}", className="card-title"),
            html.P(f"Party: {node_data['party']}", className="card-subtitle"),
            html.P(f"User ID: {node_data['id']}", className="card-subtitle"),
        ]