import dash
import dash_core_components as dcc
import dash_html_components as html

import sqlalchemy as sa

from app import app
from db import session
from models import Project
from components.project_boxplot import layout as project_boxplot
from components.project_scatter import layout as project_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs


def layout(project_slug):
    try:
        project = session.query(Project).filter_by(slug=project_slug).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    def format_combo_links(combo):
        combo_string = (f"{combo.lib1.drug_name} + {combo.lib2.drug_name}")
        combo_ref = f"/project/{project_slug}/combination/{combo.lib1_id}+{combo.lib2_id}"
        return dcc.Link(combo_string, href=combo_ref)

    combo_links = [format_combo_links(combo) for combo in
                   project.combinations]

    tab_selected_style = {
        'borderTop': '2px solid #D9230F',
    }

    return html.Div([
        crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
        html.H2(f"{project.name}", className='display-4 mt-2'),
        html.P(f"Cell Lines: {len(project.models)} - Combinations: {len(project.combinations)}", className='lead mb-4'),
        html.Div(className='row', children=[

            html.Div(
                className='col-10',
                children=[
                    dcc.Tabs(id="tabs", value='overview', children=[
                        dcc.Tab(label='Overview', value='overview', selected_style=tab_selected_style),
                        dcc.Tab(label='FlexiScatter', value='scatter', selected_style=tab_selected_style),
                    ]),
                    html.Div(id='tabs-content'),
                ]),
            html.Div(
                children=[html.H3("Combinations")] +
                         [html.Div([combo_link, html.Br()]) for combo_link in
                          sorted(combo_links, key=lambda x: x.children)],
                className='col-2'
            )
        ]),
        html.Div(style={"display": "none"}, children=str(project.id),
                 id='project-id')
    ],
    style={'width':'100%'})



@app.callback(
    dash.dependencies.Output('tabs-content', 'children'),
    [dash.dependencies.Input('tabs', 'value'),
     dash.dependencies.Input('project-id', 'children')])
def render_content(tab, project_id):
    if tab == 'overview':
        return project_boxplot(project_id)
    elif tab == 'scatter':
        return project_scatter(project_id)