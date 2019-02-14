import dash_bootstrap_components as dbc
import dash_html_components as html

from components.home_project_block import project_block
from db import session
from models import Project


def layout(*args, **kwargs):
    projects = session.query(Project).all()

    return html.Div([
        dbc.Jumbotron(html.Img(src="assets/logo_2tone.svg"), className="d-flex justify-content-center"),
        html.H1("Matrix Explorer", className='display-4 text-center mb-3'),
        dbc.Row([project_block(p) for p in projects])
    ])

