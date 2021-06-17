import dash_html_components as html
import dash_bootstrap_components as dbc

from db import session
from models import Project
from utils import matrix_projects

def project_data_link(project):
    if(project.combination_type == 'matrix'):
        return html.Div([
            html.H4(html.A(f"{project.name} matrix summaries",
                           href=f'/downloads/{project.slug}/matrix_results'),
                    className='d-inline'),html.Span(" (.csv.gz)"), html.Br(),
            html.Span("", className='small'), html.Br(), html.Br()
        ])

def layout(*args, **kwargs):
    if(matrix_projects):
        all_projects = session.query(Project).all()

        project_data_links = [project_data_link(p) for p in all_projects]

        return html.Div([
            html.H1("Matrix data Downloads", className='text-center mt-3 mb-5'),
            dbc.Row([
                dbc.Col(width=6, children=[
                    html.H2("Matrix-level data",
                            className='my-3'
                            ),
                    *project_data_links,
                ]),
                dbc.Col(width=6, children=[
                    html.H2("Documentation", className='my-3'),
                    html.H4(html.A("MatrixExplorer Documentation",
                                   href='downloads/matrixexplorer_documentation_20190211.pdf'),
                            className='d-inline'), html.Span(" (PDF, 768kB)"),
                    html.Br(),
                    html.Span("11 February 2019", className='small'), html.Br(),
                    html.Br(),
                    html.H4(
                        html.A("Glossary for datasets", href='/downloads/glossary.pdf'),
                        className='d-inline'), html.Span(" (PDF, 573kB)"), html.Br(),
                    html.Span("11 February 2019", className='small'), html.Br(),
                    html.Br(),
                    html.H4(html.A("Drug Screening Information",
                                   href='/downloads/screen_information_20190211.pdf'),
                            className='d-inline'), html.Span(" (PDF, 614kB)"),
                    html.Br(),
                    html.Span("11 February 2019", className='small'), html.Br(),
                    html.Br(),

                    html.H2("SOPs", className='my-3'),
                    html.H4(html.A("SOP 1: Exploring a combination",
                                   href='/downloads/matrixexplorer_sop_combination_20190222.pdf'),
                            className='d-inline'), html.Span(" (PDF, 4.5MB)"),
                    html.Br(),
                    html.Span("11 February 2019", className='small'), html.Br(),
                    html.Br(),
                    html.H4(html.A("SOP 2: Exploring a tissue / disease",
                                   href='/downloads/matrixexplorer_sop_disease_tissue_20190222.pdf'),
                            className='d-inline'), html.Span(" (PDF, 3.5MB)"),
                    html.Br(),
                    html.Span("11 February 2019", className='small'), html.Br(),
                    html.Br(),
                ])
            ])
        ])

