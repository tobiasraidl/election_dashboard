import dash
from dash import dcc, html
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

dash.register_page(__name__, path='/')

layout = html.Div(
    [
        html.P('This will be the content of the landing page.')
    ]
)