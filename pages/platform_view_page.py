import dash
from dash import dcc, html
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from callbacks.platform_view_callbacks import register_platform_view_callbacks

dash.register_page(__name__, path='/platform-view')
    
app = dash.get_app()

platform_graph_element = cyto.Cytoscape(
    id='platform-graph',
    layout={'name': 'cose', 'animate': False},
    style={'width': '100%', 'height': '700px', "border-style": "groove"},
    elements={},
)

platform_graph_node_info_element = dbc.Card(
    dbc.CardBody(
        id="platform-graph-node-info",
        children=[]
    )
)

layout = dbc.Container(
    [
        dbc.Row([
            html.H4("Platform View"),
            dbc.Col(
                [
                    platform_graph_element,
                ],
                width="8", className="mb-3"
            ),
            dbc.Col(
                [
                    platform_graph_node_info_element
                ],
                width="4",
                className="mb-3"
            )
        ])
    ],
    fluid=True,
    style={"padding": "20px"}
)

register_platform_view_callbacks()