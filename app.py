import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.components import Navbar
import sys, os
import yaml

from utils.data_loader import load_data

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

app.layout = html.Div(
    [
        dcc.Store(id='df-store'),
        dcc.Store(id='config-store'),
        Navbar(),
        # Content of each page
        dash.page_container
    ]
)

@app.callback(
    dash.dependencies.Output('df-store', 'data'),
    [dash.dependencies.Input('df-store', 'data')]
)
def load_data_frame(data):
    df = load_data('data/all_posts.csv')
    return df.to_dict()

@app.callback(
    dash.dependencies.Output('config-store', 'data'),
    [dash.dependencies.Input('config-store', 'data')]
)
def load_config(data):
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


if __name__ == "__main__":
    app.run(debug=True)