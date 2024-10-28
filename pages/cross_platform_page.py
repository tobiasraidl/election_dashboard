import dash
from dash import dcc, html
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

from callbacks.platform_view_callbacks import register_platform_view_callbacks

dash.register_page(__name__, path='/cross-platform')
    
df = pd.read_csv('data/cross_platform_posts.csv')

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
                                src='https://developers.elementor.com/docs/assets/img/elementor-placeholder-image.png', 
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
    scrollable=True,
)

layout = dbc.Container(
    [
        dcc.Store(id='df-k-most-freq-hashes'),
        dbc.Row([

            # html.Div(id="radio-buttons-error")
        ]),
        dbc.Row([
            html.H4("Platform View", style={'text-align': 'center'}),
            dbc.Col(
                [
                    html.Div([
                        dbc.Alert("Select at least two platforms.", color="secondary"),
                        dbc.Checklist(
                            options=[
                                {"label": "Twitter", "value": "Twitter"},
                                {"label": "Instagram", "value": "Instagram"},
                                {"label": "Facebook", "value": "Facebook"},
                            ],
                            id="switches",
                            value=["Twitter", "Instagram", "Facebook"],  # Default: all options are True
                            switch=True
                        ),
                    ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center'})
                ],
                width='2',
                className='mb-3'
            ),
            dbc.Col(
                [
                    dbc.Spinner(html.Div(id='bar-chart-wrapper')),
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