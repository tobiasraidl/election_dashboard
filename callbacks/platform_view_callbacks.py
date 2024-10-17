from dash.dependencies import Input, Output
from dash import callback, dcc, html
import pandas as pd
import dash

from utils.platform_view_graph import PlatformGraph

def register_platform_view_callbacks():
    
    @callback(
        Output('platform-graph', 'elements'),
        [Input('df-store', 'data')]
    )
    def generate_nodes(df):
        if df is not None:
            df = pd.DataFrame.from_dict(df)
            platform_graph = PlatformGraph(df)
            return platform_graph.gen_cytoscape_elements()
        return {}
    
    @callback(Output('platform-graph-node-info', 'children'),
              Input('platform-graph', 'tapNodeData'))
    def show_node_info(node_data):
        if node_data is not None:
            children = [
                html.H4(f"Platform: {node_data['platform']}", className="card-title"),
                html.H6(f"Num. of Posts: {node_data['posts']}", className="card-subtitle"),
                html.P(f"Image Hash: {node_data['hash']}"),
                html.P(f"Node ID: {node_data['id']}"),
            ]
            return children
        else:
            return [html.P('Click on a node for details.')]