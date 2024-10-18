import dash
from dash import dcc, html
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

from callbacks.platform_view_callbacks import register_platform_view_callbacks

dash.register_page(__name__, path='/platform-view')
    
app = dash.get_app()

top_shared_images_bar_chart_element = dcc.Graph(
    id='top-shared-images-bar-chart',
        figure={}
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
                    top_shared_images_bar_chart_element,
                ],
                # width="6", 
                className="mb-3"
            ),
        ])
    ],
    fluid=True,
    style={"padding": "20px"}
)

register_platform_view_callbacks()