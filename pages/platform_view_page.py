import dash
from dash import dcc, html
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

dash.register_page(__name__, path='/platform-view')

layout = html.Div(
    [
        html.P('This will be the content of the platform view page.')
    ]
)