import dash
import dash_cytoscape as cyto
from dash import html, dcc, callback
from dash.dependencies import Input, Output, State
import networkx as nx
from utils.accounts_network_graph_creation import create_accounts_graph, create_cluster_graph
from utils.accounts_network_graph_elements import generate_cluster_graph_elements, generate_connection_graph_elements, generate_cluster_inspection_graph_elements
from utils.image_loader import generate_image_grid
import pandas as pd
import dash_bootstrap_components as dbc
import yaml
import plotly.graph_objs as go

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

df = pd.read_csv('data/posts_with_party.csv')
dash.register_page(__name__, path='/')

MIN_CLUSTER_SIZE = 10
MAX_CLUSTER_SIZE = 30
CLUSTER_SIZE_SLIDER_STEPS = 5
INITIAL_MIN_CLUSTER_SIZE = 20

G_accounts = create_accounts_graph(df)
G_clusters = create_cluster_graph(G_accounts, MIN_CLUSTER_SIZE)
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
    style={'width': '100%', 'height': '700px', "borderStyle": "groove"},
    elements=generate_cluster_graph_elements(config, G_clusters, INITIAL_MIN_CLUSTER_SIZE),
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'content': 'data(size)',  # Display the label (number) inside the node
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#0074D9',
                'color': '#ffffff',  # Text color
                'font-size': '10px',
                'width': '35px',
                'height': '35px',
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': '#888',
                'width': 2,
            }
        }
    ]
)


slider_element = html.Div([
    html.Label("Min. Cluster Size:", style={'margin-right': '10px'}),
    html.Div([
        dcc.Slider(
            MIN_CLUSTER_SIZE, MAX_CLUSTER_SIZE, CLUSTER_SIZE_SLIDER_STEPS,
            value=INITIAL_MIN_CLUSTER_SIZE,
            id="min-cluster-size-slider"
        )
    ], style={'width': '100%', 'flex-grow': '1'})  # Added flex-grow
], style={'display': 'flex', 'align-items': 'center', 'width': '100%'})


select_label_element = dbc.Label("Network Layout:", html_for="graph-layout-select")

select_element = dbc.Select(
    id="graph-layout-select",
    value="cose",
    options=[
        {"label": name.capitalize(), "value": name} 
        for name in LAYOUT_NAMES
    ]
)

### CONNECTION GRAPH MODAL

connection_graph_element = cyto.Cytoscape(
        id='connection-graph',
        layout={"name": "breadthfirst", 'roots': ["cluster-left"], 'direction': 'LR', 'animate': False},
        style={'width': '100%', 'height': '100%', "borderStyle": "groove"},
        elements = []
)

connection_graph_node_info_element = dbc.Card(
    dbc.CardBody(
        id="connection-graph-node-info",
        children=[]
    ),
    style={'height': '100%'}
)

connection_graph_modal_element = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Cluster Connection View")),
        dbc.ModalBody([
            html.Div(
                [
                    dbc.Col(
                        [connection_graph_element], className='m-3'
                    ),
                    dbc.Col([
                        dbc.Row(html.P('This view displays all minimum paths that connect the two clusters.'), className='m-3'),
                        dbc.Row(connection_graph_node_info_element)
                    ], className='m-3'),
                ],
                style={
                    'display': 'flex',
                    'gap': '10px',      # Adds spacing between the sections
                    'height': '700px'  # Ensures the modal is large
                }
            )
            
        ])
    ],
    id="connection-graph-modal",
    size="xl",
    is_open=False
)

### CLUSTER INSPECTION GRAPH MODAL

cluster_inspection_graph_element = cyto.Cytoscape(
        id='cluster-inspection-graph',
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '100%', "borderStyle": "groove"},
        elements = [],
)

cluster_inspection_graph_node_info_element = dbc.Card(
    dbc.CardBody(
        id="cluster-inspection-graph-node-info",
        children=[]
    ),
    style={'height': '100%'}
)

cluster_inspection_slider_element = html.Div([
    html.Label("Min. same images shared:", style={'margin-right': '10px'}),
    html.Div([
        dcc.Slider(1, 5, 1, value=2, id="cluster-inspection-slider")
    ], style={'width': '100%', 'flex-grow': '1'})  # Added flex-grow
], style={'display': 'flex', 'align-items': 'center', 'width': '100%'})

cluster_inspection_graph_modal_element = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Cluster Inspection")),
        dbc.ModalBody([
            html.Div(
                [
                    dbc.Col(
                        [cluster_inspection_graph_element], 
                        className="m-3"
                    ),
                    dbc.Col([
                        dbc.Row(html.P('Each node is an account of this cluster. Two accounts are connected if they shared at least the specified number of same images. The edge opacity correlates to the number of same images shared.'), className='m-3'),
                        dbc.Row(cluster_inspection_slider_element, className='m-3'),
                        dbc.Row(cluster_inspection_graph_node_info_element, className='m-3 pb-3'),
                    ], className='m-3')
                ],
                style={
                    'display': 'flex',
                    'gap': '10px',      # Adds spacing between the sections
                    'height': '700px'  # Ensures the modal is large
                }
            )
            
        ])
    ],
    id="cluster-inspection-graph-modal",
    size="xl",
    is_open=False,
    scrollable=True,
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
                dbc.Col(dbc.Card(dbc.CardBody(
                    [
                        dbc.Row([slider_element], align="center", className="m-3"),
                        dbc.Row([dbc.Col([select_label_element]), dbc.Col([select_element])], align="center", className="m-3"),
                        dbc.Row([html.P(
                            'Each cluster shown represents a group of at least n accounts that are fully connected, ' +
                            'meaning every account in the cluster is directly linked to every other account within it. ' +
                            'Two clusters are connected if there exists a path between the clusters.' +
                            'The numbers inside the nodes and the size represent the number of accounts inside this cluster.' +
                            'This View only includes accounts with known party affiliation.',
                            className='p-3')
                        ])
                    ])),
                    width="4"
                ),
            ]
        ),
        dbc.Row([
            connection_graph_modal_element,
            cluster_inspection_graph_modal_element
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
        "animate": False
    }
    
@callback(
    Output('cluster-inspection-graph-modal', 'is_open'),
    Input('cluster-graph', 'tapNodeData'),
    State('cluster-inspection-graph-modal', 'is_open'),
    prevent_initial_call=True
)
def toggle_cluster_inspection_modal(node_data, is_open):
    if node_data:  # Only toggle if a node is clicked
        return not is_open
    return is_open

@callback(
    [Output('cluster-inspection-graph', 'elements'),
     Output("cluster-inspection-graph-node-info", "children", allow_duplicate=True),],
    Input('cluster-graph', 'tapNodeData'),
    Input("cluster-inspection-slider", "value"),
    prevent_initial_call=True
)
def update_cluster_inspection_graph(node_data, slider_value):
    if node_data:
        elements = generate_cluster_inspection_graph_elements(node_data['accounts'], df, config, min_same_shared_images=slider_value)
        return elements, 'Click a node to see its details or an edge to see the both accounts shared.'
    return [], 'Click a node to see its details or an edge to see the both accounts shared.'

# @callback(
#     [
#         Output('cluster-inspection-graph-modal', 'is_open'),
#         Output('cluster-inspection-graph', 'elements'),
#         Output("cluster-inspection-graph-node-info", "children")
#     ],
#     [
#         Input('cluster-graph', 'tapNodeData'),        # Node click on main graph to open modal
#         Input("cluster-inspection-slider", "value")   # Slider adjustment for graph filtering
#     ],
#     State('cluster-inspection-graph-modal', 'is_open'),
#     prevent_initial_call=True
# )
# def toggle_and_update_modal(node_data, slider_value, is_open):
#     # Check if a node is clicked in the main graph to toggle modal open
#     if node_data:
#         # Generate elements for inspection graph based on node_data and slider
#         elements = generate_cluster_inspection_graph_elements(
#             node_data['accounts'], df, config, min_same_shared_images=slider_value
#         )
#         # Set initial message for node info
#         node_info = 'Click a node to see its details or an edge to see the images both accounts shared.'
#         return not is_open, elements, node_info

#     # If slider is adjusted and modal is already open, update the inspection graph elements
#     elif is_open and slider_value is not None:
#         # Use existing node_data to regenerate elements with the updated slider value
#         elements = generate_cluster_inspection_graph_elements(
#             node_data['accounts'], df, config, min_same_shared_images=slider_value
#         )
#         return is_open, elements, dash.no_update  # Keep modal open, update elements only

#     # Default: No changes if no node click or slider input
#     return is_open, dash.no_update, dash.no_update

@callback(
    Output("cluster-inspection-graph-node-info", "children", allow_duplicate=True),
    Input("cluster-inspection-graph", "tapNodeData"),
    prevent_initial_call=True
)
def display_cluster_inspection_graph_node_info(node_data):
    if node_data is None:
            return "Click a node to see its details or an edge to see the both accounts shared."
    return [
            html.H4(f"Account Name: {node_data['name']}", className="card-title"),
            html.P(f"Party: {node_data['party']}", className="card-subtitle"),
            html.P(f"User ID: {node_data['id']}", className="card-subtitle"),
        ]
    
@callback(
    Output("cluster-inspection-graph-node-info", "children", allow_duplicate=True),
    Input("cluster-inspection-graph", "tapEdgeData"),
    prevent_initial_call=True
)
def display_cluster_inspection_graph_edge_info(edge_data):
    if edge_data is None:
        return "Click a node to see its details or an edge to see the both accounts shared."
    filtered_df = df[(df['user_id'] == edge_data['source']) | (df['user_id'] == edge_data['target'])]
    # Get the set of hashes for each user_id
    hashes_user_1 = set(filtered_df[filtered_df['user_id'] == edge_data['source']]['hash'])
    hashes_user_2 = set(filtered_df[filtered_df['user_id'] == edge_data['target']]['hash'])

    # Find the intersection of the two sets
    common_hashes = list(hashes_user_1.intersection(hashes_user_2))
    return generate_image_grid(common_hashes)

@callback(
    [
        Output('connection-graph', 'elements'),
        Output('connection-graph-modal', 'is_open'),
        Output('connection-graph-node-info', 'children', allow_duplicate=True)
    ], 
    Input('cluster-graph', 'tapEdgeData'),
    State('connection-graph-modal', 'is_open'),
    prevent_initial_call=True
)
def display_connection_graph(edgeData, is_open):
    if edgeData is None:
        return [], is_open, "Click a node to see its details."
    
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
    elements = generate_connection_graph_elements(
        config,
        G_accounts, 
        cluster1_details,
        cluster2_details
    )
    return elements, True, "Click a node to see its details."
    
@callback(
    Output("connection-graph-node-info", "children", allow_duplicate=True),
    Input("connection-graph", "tapNodeData"),
    prevent_initial_call=True
)
def display_connection_graph_node_info(node_data):
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
            html.H6(f"Size: {node_data['size']} accounts", className="card-subtitle"),
            dcc.Graph(id='party-ratio-plot', figure=fig),
        ]
        
    else:
        return [
            html.H4(f"Account Name: {node_data['name']}", className="card-title"),
            html.P(f"Party: {node_data['party']}", className="card-subtitle"),
            html.P(f"User ID: {node_data['id']}", className="card-subtitle"),
        ]