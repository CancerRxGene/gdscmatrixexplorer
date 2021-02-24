import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from components.home_project_block import project_block, project_card
from db import session
from models import Project


def layout(*args, **kwargs):
    projects = session.query(Project).order_by(Project.name).all()
    matrix_projects = session.query(Project).filter(Project.combination_type == 'matrix').all()
    anchor_projects = session.query(Project).filter(Project.combination_type == 'anchor').all()

    return html.Div([
        dbc.Jumbotron(html.Img(src="assets/logo_2tone.svg"), className="d-flex justify-content-center"),
        html.H1("Genomics of Drug Sensitivity in Cancer", className='display-4 text-center'),
        html.P("Drug Combination Matrix Explorer", className="lead text-center"),
        html.P("An interactive tool for the interpretation of bitherapy data generated at the Wellcome Sanger Institute.", className='text-center post-lead'),
        project_card(matrix_projects,"Matrix projects"),
        project_card(anchor_projects,'Anchor projects')

        # dbc.Row(className='mt-5',
        #         children=[dbc.Col(width=12, children=html.H3("Screening Projects", className='mt-5 mb-3'))] +
        #                  [project_block(p) for p in projects])

    ])

