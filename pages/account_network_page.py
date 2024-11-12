import dash
from dash import html, dcc, callback
import yaml
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import pandas as pd
import os

from callbacks.account_network_callbacks import register_account_network_callbacks
from utils.account_graph import AccountGraph

dash.register_page(__name__, path='/')

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
df = pd.read_csv('data/outputs/posts_with_party.csv')

account_graph = AccountGraph(df, config)

### ELEMENTS
account_graph_element = dbc.Spinner(
    color="primary",
    delay_show=500,
    children=cyto.Cytoscape(
        id='account-graph',
        layout={'name': 'preset'},
        style={'width': '100%', 'height': '600px', "background-color": "#121212", "border-radius": "15px"},
        elements=account_graph.gen_cytoscape_elements(element_list_path="data/outputs/init_account_network_elements.json"),
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

party_filter_col1_element = dbc.Checklist(
    options=[
        {"label": "AFD", "value": "afd"},
        {"label": "SPD", "value": "spd"},
        {"label": "Die Grünen", "value": "die_gruenen"},
    ],
    value=["afd", "spd", "die_gruenen"],
    id="party-filter-checklist-col2",
    inline=False
)

party_filter_col2_element = dbc.Checklist(
    options=[
        {"label": "Die Linke", "value": "die_linke"},
        {"label": "CDU/CSU", "value": "cdu_csu"},
        {"label": "FDP", "value": "fdp"}
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
        # dbc.Col(width=4),
        dbc.Col(
            dbc.Checklist(
                options=[
                    {"value": "highlight"},
                ],
                value=[],
                id="highlight-cross-party-connections-toogle",
                # switch=True
            ), width=4
        ),
    ])
])

layout = html.Div(
    style={
        # 'backgroundColor': '#333333',
        # 'color': '#FFFFFF',
        'height': '100vh',
    },
    children=dbc.Container(
        [
            dbc.Row([
                dbc.Col([
                    account_graph_element,
                ],width=8),
                dbc.Col([
                    dbc.Card([
                            dbc.Row(min_same_imgs_shared_slider, className='mb-3'),
                            dbc.Row(party_filter_element, className='mb-3'),
                            dbc.Row(highlight_cross_party_connections_toggle_element),
                        
                    ], body=True, className="mb-3", style={'background-color': '#121212', 'border-radius': '15px'})
                ],width=4)
            ])
        ],
        fluid=True,
        style={"padding": "20px"}
    )
)

register_account_network_callbacks(df, config, account_graph)