import dash
from dash import html, dcc
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd

from callbacks.account_network_callbacks import register_account_network_callbacks
from utils.account_graph import AccountGraph

dash.register_page(__name__, path='/')

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
df = pd.read_csv('data/posts_with_party.csv')
df_base_posts = pd.read_csv('data/base_posts.csv')

account_graph = AccountGraph(df, config)

### ELEMENTS
account_graph_element = dbc.Spinner(
    color="primary",
    delay_show=500,
    children=cyto.Cytoscape(
        id='account-graph',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '750px', "background-color": config['style']['foreground_color'], "border-radius": "15px"},
        elements=account_graph.gen_cytoscape_elements(element_list_path="data/init_account_network_elements.json"),
    )
)

min_same_imgs_shared_slider = html.Div([
    dbc.Row([
        dbc.Col(html.P("Min. same images shared:", style={'margin-right': '10px'}), width=4),
        dbc.Col(
            dcc.Slider(
                1, 10, 1,
                value=1,
                id="min-same-imgs-shared-slider"
            ), width=8
        )
    ])
])

min_account_connections_slider = html.Div([
    dbc.Row([
        dbc.Col(html.P("Min. account connections:", style={'margin-right': '10px'}), width=4),
        dbc.Col(
            dcc.Slider(
                1, 10, 1,
                value=1,
                id="min-account-connections-slider"
            ), width=8
        )
    ])
])

party_filter_col1_element = dbc.Checklist(
    options=[
        {"label": html.Span("AFD", style={"color": "white","backgroundColor": config["party_color_map"]["afd"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "afd"},
        {"label": html.Span("SPD", style={"color": "white","backgroundColor": config["party_color_map"]["spd"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "spd"},
        {"label": html.Span("Die Grünen", style={"color": "white","backgroundColor": config["party_color_map"]["die_gruenen"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "die_gruenen"},
    ],
    value=["afd", "spd", "die_gruenen"],
    id="party-filter-checklist-col2",
    inline=False
)

party_filter_col2_element = dbc.Checklist(
    options=[
        {"label": html.Span("Die Linke", style={"color": "white","backgroundColor": config["party_color_map"]["die_linke"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "die_linke"},
        {"label": html.Span("CDU/CSU", style={"color": "white","backgroundColor": config["party_color_map"]["cdu_csu"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "cdu_csu"},
        {"label": html.Span("FDP", style={"color": "white","backgroundColor": config["party_color_map"]["fdp"], "borderRadius": "4px", "padding": "0px 10px 2px 10px"}), "value": "fdp"}
    ],
    value=["die_linke", "cdu_csu", "fdp"],
    id="party-filter-checklist-col1",
    inline=False
)

party_filter_element = html.Div([
    dbc.Row([
        dbc.Col(html.P('Filter by Party:'), width=4),
        dbc.Col(party_filter_col1_element, width=4),  # First column takes up half the row
        dbc.Col(party_filter_col2_element, width=4),  # Second column takes up half the row
    ])
])

highlight_cross_party_connections_toggle_element = html.Div([
    dbc.Row([
        dbc.Col(html.P('Highlight Cross Party Connections:'), width=8),
        dbc.Col(
            dbc.Checklist(
                options=[
                    {"value": "highlight"},
                ],
                value=[],
                id="highlight-cross-party-connections-toogle",
            ), width=4
        ),
    ])
])


scaling_ratio_slider_element = html.Div([
    dbc.Row([
        dbc.Col(html.P("Scale Node Distance:"), width=4),
        dbc.Col(
            dcc.Slider(
                1.0, 10.0, 1.0,
                value=3.0,
                id="scaling-ratio-slider"
            ), width=8
        )
    ])
])

iterations_tooltip = html.Div([
    # Create an info icon
    html.Span(
        "ℹ️",  # Unicode symbol for info icon, or use dbc.Icon("info-circle") for a different style
        id="info-icon",
        style={"cursor": "pointer", "fontSize": "20px", "marginLeft": "10px"}
    ),
    
    # Tooltip for the info icon
    dbc.Tooltip(
        [
            "Low -> Performance",
            html.Br(),
            "High -> Better cluster visualization"
        ],
        target="info-icon",
        placement="right"
    )
])

iterations_slider_element = html.Div([
    dbc.Row([
        dbc.Col(html.P(["Iterations:", iterations_tooltip], style={"display": "flex", "alignItems": "center"}), width=4),
        dbc.Col(
            dcc.Slider(
                50, 200, 50,
                value=100,
                id="iterations-slider"
            ), width=8
        )
    ])
])

image_details_modal_element = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Image Details")),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.Div(id='image-details-text-account-page', className='top-left', style={'height': '100%', 'overflow': 'auto'}),
                        html.Div(
                            html.Img(
                                id='image-details-image-account-page',
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
                        dcc.Graph(id='image-timeline-account-page', className='bottom-left'),
                        dcc.Graph(figure={}, id='image-party-ratios-account-page', className='bottom-right'),
                    ],
                    style={
                        'display': 'grid',
                        'grid-template-columns': '1fr 1fr',
                        'grid-template-rows': '1fr 2fr',
                        'gap': '10px',
                        'height': '100%'
                    },
                )
            ]
        ),
    ],
    id="image-details-account-page",
    size="xl",
    is_open=False,
)

layout = html.Div(
    style={
        'height': '100vh',
    },
    children=dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    dbc.Row(account_graph_element, className='mb-3'),
                    dbc.Row([
                        html.Div([
                            dbc.Card([
                                html.H5("Plot Description"),
                                html.P(
                                    """
                                    Nodes represent social media accounts. Two accounts are connected if they shared at least one same image in 
                                    the six-week time period leading up to the election. Besides a filter option the graph visualization features 
                                    the following interactivity. Clicking on a node leads to more information about the account, and clicking 
                                    on a connection provides the images that both accounts shared. Furthermore, clicking on an image will provide 
                                    more information about it. This network plot includes all accounts of the dataset with known party affiliation.
                                    """
                                )
                            ], body=True, style={'width': '100%', "background-color": config['style']['foreground_color'], "border-radius": "15px"}),
                        ])
                    ])
                ],width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row(min_same_imgs_shared_slider, className='mb-3 mt-3 mx-3'),
                            dbc.Row(min_account_connections_slider, className='mb-3 mt-3 mx-3'),
                            dbc.Row(highlight_cross_party_connections_toggle_element, className='mb-3 mx-3'),
                            dbc.Row(party_filter_element, className='mb-3 mx-3'),
                            dbc.Row(scaling_ratio_slider_element, className='mb-3 mx-3'),
                            dbc.Row(iterations_slider_element, className='mb-3 mx-3'),
                            dbc.Row(dbc.Button("Apply", id="apply-button", color="primary"), justify='center', className="mx-3 mb-3"),
                        ]),
                    ], className="mb-3", style={'background-color': config['style']['foreground_color'], 'border-radius': '15px'}),
                    dbc.Card([
                        html.P('Click on a node or an edge for details.')
                    ], id='on-click-output-card', body=True, style={'background-color': config['style']['foreground_color'], 'border-radius': '15px'}),
                    image_details_modal_element
                ],width=4)
            ]),
        ],
        fluid=True,
        style={"padding": "20px"}
    )
)

register_account_network_callbacks(df, df_base_posts, config, account_graph)