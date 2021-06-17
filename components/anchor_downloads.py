import dash_html_components as html
import dash_bootstrap_components as dbc

from db import session
from models import Project
from utils import anchor_projects

def project_data_link(project):
    if(project.combination_type == 'anchor'):
        return html.Div([
            html.H4(html.A(f"{project.name} anchor data",
                           href=f'/downloads/{project.slug}/anchor_combo'),
                    className='d-inline'),html.Span(" (.csv.gz)"), html.Br(),
            html.Span("", className='small'), html.Br(), html.Br()
        ])

def layout(*args, **kwargs):
    if(anchor_projects):
        all_projects = session.query(Project).all()

        project_data_links = [project_data_link(p) for p in all_projects]

        return html.Div([
            html.H1("Anchor data Downloads", className='text-center mt-3 mb-5'),
            *project_data_links,

        ])

