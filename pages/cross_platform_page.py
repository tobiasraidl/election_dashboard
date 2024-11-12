import dash
from dash import dcc, html
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os

from callbacks.platform_view_callbacks import register_platform_view_callbacks

dash.register_page(__name__, path='/cross-platform')

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
df = pd.read_csv('data/outputs/cross_platform_posts.csv')
image_details = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Image Details")),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.Div(id='image-details-text', className='top-left', style={'height': '100%', 'overflow': 'auto'}),
                        html.Div(
                            html.Img(
                                id='image',
                                src='assets/placeholder.jpg', 
                                style={
                                    'max-height': '200px', 
                                    'width': '100%', 
                                    'object-fit': 'contain'
                                }
                            ), 
                            className="top-right",
                            style={'height': '100%', 'overflow': 'hidden'}
                        ),
                        dcc.Graph(id='image-timeline', className='bottom-left'),
                        dcc.Graph(figure={}, id='image-party-ratios', className='bottom-right'),
                    ],
                    style={
                        'display': 'grid',
                        'grid-template-columns': '1fr 1fr',
                        'grid-template-rows': '1fr 2fr',
                        'gap': '10px',      # Adds spacing between the sections
                        'height': '100%'  # Ensures the modal is large
                    },
                    # className="modal-grid"
                )
            ]
        ),
    ],
    id="image-details",
    size="xl",
    is_open=False,
)

layout = dbc.Container(
    [
        dcc.Store(id='df-k-most-freq-hashes'),
        dbc.Row([
            html.H4("Most shared images", style={'text-align': 'center'}),
            dbc.Col(
                [
                    dbc.Card([
                        dbc.CardBody([
                            
                            html.Div([
                                html.P('This bar chart shows the 20 most shared images across platforms. Click on a bar for more details about the image.'),
                                html.P('Filter images by selecting at least two platforms:'),
                                dbc.Checklist(
                                    options=[
                                        {"label": html.Span("Twitter", style={"color": "white","backgroundColor": config["platform_color_map"]["Twitter"], "borderRadius": "4px", "padding": "1px 10px 1px 10px"}), "value": "Twitter"},
                                        {"label": html.Span("Instagram", style={"color": "white","backgroundColor": config["platform_color_map"]["Instagram"], "borderRadius": "4px", "padding": "1px 10px 1px 10px"}), "value": "Instagram"},
                                        {"label": html.Span("Facebook", style={"color": "white","backgroundColor": config["platform_color_map"]["Facebook"], "borderRadius": "4px", "padding": "1px 10px 1px 10px"}), "value": "Facebook"},
                                    ],
                                    id="switches",
                                    value=["Twitter", "Instagram", "Facebook"],  # Default: all options are True
                                    switch=True
                                ),
                            ], style={
                                    'display': 'flex',
                                    'flex-direction': 'column',
                                    'justify-content': 'center',
                                    'align-items': 'center',
                                    'height': '400px'
                            })
                            ])
                    ])
                ],
                width='2',
                className='mb-3',
                style={'display': 'flex', 'align-items': 'center'}
            ),
            dbc.Col(
                [
                    html.Div(id='bar-chart-wrapper'),
                    image_details
                ],
                width="10", 
                className="mb-3"
            ),
            
        ])
    ],
    fluid=True,
    style={"padding": "20px"}
)

register_platform_view_callbacks(df)