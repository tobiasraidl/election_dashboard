from dash.dependencies import Input, Output, State
from dash import callback, Output, Input, State, callback_context, dcc, html
import pandas as pd
import dash
import plotly.graph_objects as go
import plotly.express as px
import os

from utils.image_loader import load_image

def register_network_v2_callbacks(df, config):
    pass