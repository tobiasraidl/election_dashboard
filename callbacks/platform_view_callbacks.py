from dash.dependencies import Input, Output
from dash import callback, dcc, html
import pandas as pd
import dash
from datetime import datetime
import plotly.graph_objects as go

from utils.platform_view_graph import PlatformGraph, TimespanGraph

def register_platform_view_callbacks():
    
    # @callback(
    #     Output('top-shared-images-bar-chart', 'elements'),
    #     [Input('df-store', 'data')]
    # )
    # def generate_nodes(df):
    #     if df is not None:
    #         df = pd.DataFrame.from_dict(df)
    #         G = TimespanGraph(df)
    #         return G.gen_cytoscape_elements(start=datetime(2021, 9, 5, 10, 30, 30), end=datetime(2021, 9, 5, 20, 30, 30))
    #         # G = PlatformGraph(df)
    #         # return G.gen_cytoscape_elements()
    #     return {}
    
    # @callback(Output('platform-graph-node-info', 'children'),
    #           Input('platform-graph', 'tapNodeData'))
    # def show_node_info(node_data):
    #     if node_data is not None:
    #         children = [
    #             html.H4(f"Platform: {node_data['platform']}", className="card-title"),
    #             html.H6(f"Num. of Posts: {node_data['posts']}", className="card-subtitle"),
    #             html.P(f"Image Hash: {node_data['hash']}"),
    #             html.P(f"Node ID: {node_data['id']}"),
    #         ]
    #         return children
    #     else:
    #         return [html.P('Click on a node for details.')]
    
    @callback(
        Output('top-shared-images-bar-chart', 'figure'),
        [Input('df-store', 'data')]
    )
    def generate_barchart(df_dict):
        # x ... 10 most shared images; y ... num of shares; stacked y and color ... platform
        if df_dict is not None:
            df = pd.DataFrame(df_dict)
            hash_counts = df['hash'].value_counts()
            top_hashes = hash_counts.iloc[0:20]
            most_shared_images = df[df['hash'].isin(list(top_hashes.index))]
            counts = most_shared_images.groupby(['hash', 'platform'])['platform'].count()

            df_temp = counts.unstack(fill_value=0)

            fig = go.Figure()

            platform_colors = {
                'fb': '#4267B2',
                'ig': '#E4405F',
                'tw': '#1DA1F2'
            }

            for platform in df_temp.columns:
                fig.add_trace(go.Bar(
                    x=df_temp.index,
                    y=df_temp[platform],
                    name=platform,
                    marker_color=platform_colors[platform]
                ))

            fig.update_layout(
                barmode='stack',
                title="Stacked Bar Chart of Platform Counts by Hash",
                xaxis_title="Hash",
                yaxis_title="Count",
                xaxis={'categoryorder': 'total descending'},
            )
            return fig
        return {}
    