import dash_html_components as html
import dash_bootstrap_components as dbc
from components.breadcrumbs import breadcrumb_generator as crumbs

from db import session
from models import Project
from components.matrix_downloads import layout as matrix_download
from components.anchor_downloads import layout as anchor_download

def layout(*args, **kwargs):

    # return [
    #     html.H1("Downloads", className='display-4 text-center mt-5 mb-5'),
    #     matrix_download()
    # ]

    return html.Div([
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        html.Div([
                            crumbs([("Home", "/"), ("/downloads",)]),
                        ])
                    )
                ),
                dbc.Row(
                    dbc.Col(children=[
                    matrix_download(),
                    html.Br(),
                    html.Br(),
                    anchor_download()
                   ]
                )
                )
            ])
        ])

