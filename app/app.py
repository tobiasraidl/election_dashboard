import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.components import Navbar
import sys, os
import yaml
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server # when ran as a server

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

app.layout = html.Div(
    [
        dcc.Store(id='config-store'),
        Navbar(),
        dash.page_container
    ],
)
    
@app.callback(
    dash.dependencies.Output('config-store', 'data'),
    [dash.dependencies.Input('config-store', 'data')]
)
def load_config(data):
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    
    # When launched without docker
    # app.run(debug=True)
    
    # When launched using docker
    app.run(host='0.0.0.0', port=8050, debug=False)

