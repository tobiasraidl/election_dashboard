from dash.dependencies import Input, Output
from dash import callback
import pandas as pd
import dash

from utils.platform_view_graph_creation import PlatformGraph

def register_platform_view_callbacks():
    
    @callback(
        Output('platform-graph', 'elements'),
        [Input('df-store', 'data')]
    )
    def update_output(df):
        if df is not None:
            df = pd.DataFrame.from_dict(df)
            platform_graph = PlatformGraph(df)
            return platform_graph.gen_cytoscape_elements()
        return {}