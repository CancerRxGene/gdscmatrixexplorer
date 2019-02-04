import dash_bootstrap_components as dbc
import dash_html_components as html

from components.home_project_block import project_block
from db import session
from models import Project


def layout(*args, **kwargs):
    projects = session.query(Project).all()

    return html.Div([
        html.H1("GDSC Matrix Explorer", className='display-4 text-center mt-5 mb-3'),
        html.P("Projects", className='lead text-center'),
        dbc.Row([project_block(p) for p in projects])
    ])

