import dash
from dash import html, dcc, callback
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os

from callbacks.network_v2_callbacks import register_network_v2_callbacks
from utils.accounts_graph import AccountsGraph

dash.register_page(__name__, path='/network_v2')

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
df = pd.read_csv('data/posts_with_party.csv')

accounts_graph = AccountsGraph(df, config)

### ELEMENTS
accounts_graph_element = cyto.Cytoscape(
    id='accounts-graph',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '700px', "borderStyle": "groove"},
    elements=accounts_graph.gen_cytoscape_elements(),
)

layout = dbc.Container(
    [
        dbc.Col([
            accounts_graph_element
        ],width=8),
        dbc.Col([
            
        ],width=4)
    ],
    fluid=True,
    style={"padding": "20px"}
)
