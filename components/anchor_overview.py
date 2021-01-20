from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd

from app import app
from db import session
from models import Combination

def layout(combination):
    return html.Div(children=[
        dbc.Row(
            dbc.Col(width=12, children=[
                html.Div(
                    html.H3("Detailed overview of drug responses"),
                    html.Hr(),
            )]
        ))
    ])