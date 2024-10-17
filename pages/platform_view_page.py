import dash
from dash import dcc, html
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from callbacks.platform_view_callbacks import register_platform_view_callbacks

dash.register_page(__name__, path='/platform-view')

# with open("config.yaml", "r") as file:
#     config = yaml.safe_load(file)
    
app = dash.get_app()

platform_graph_element = cyto.Cytoscape(
    id='platform-graph',
    layout={'name': 'cose'},
    style={'width': '100%', 'height': '700px', "border-style": "groove"},
    elements={},
)

layout = html.Div(
    [
        dbc.Row([
            html.H4("Platform View"),
            dbc.Col(
                [
                    platform_graph_element,
                ], 
                width="8", className="mb-3"
            )
        ])
    ]
)

register_platform_view_callbacks()