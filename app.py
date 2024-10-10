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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

df = load_data('data/multiplatform_hashed_visuals.csv', config)
MIN_CLUSTER_SIZE = 20
MAX_CLUSTER_SIZE = 50
CLUSTER_SIZE_SLIDER_STEPS = 5
INITIAL_MIN_CLUSTER_SIZE = 20
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

graph_element = cyto.Cytoscape(
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

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([graph_element, html.Div(id="connection-graph-wrapper")], width="8", className="mb-3"),
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
            # style={"height": "400px"},
            className="mb-4"
        )
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

@app.callback(
    Output('connection-graph-wrapper', 'children'),
    Input('cluster-graph', 'tapEdgeData')
)
def display_connection_graph(edgeData):
    if edgeData is None:
        return html.P("Click an edge to view a new graph.")
    
    return cyto.Cytoscape(
        id='connection-graph',
        layout={"name": "cose"},
        style={'width': '100%', 'height': '700px', "border-style": "groove"},
        elements = generate_connection_graph_elements(
            G_people, 
            edgeData["source"], 
            G_clusters.nodes[int(edgeData["source"])]["nodes"], 
            edgeData["target"], 
            G_clusters.nodes[int(edgeData["target"])]["nodes"]
        )
    )

if __name__ == '__main__':
    app.run_server(debug=True)