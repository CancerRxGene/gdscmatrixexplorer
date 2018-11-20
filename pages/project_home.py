import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import pandas as pd
import sqlalchemy as sa
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, Project, Drug
from components.project_boxplot import layout as project_boxplot
from components.project_scatter import layout as project_scatter


def layout(project_slug):
    try:
        project = session.query(Project).filter_by(slug=project_slug).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")
    # metrics = ["HSA_excess", "HSA_excess_syn", "HSA_excess_well_count",
    #            "HSA_excess_window", "HSA_excess_window_syn", "Bliss_excess",
    #            "Bliss_excess_syn", "Bliss_excess_well_count",
    #            "Bliss_excess_window",
    #            "Bliss_excess_window_syn"
    #            ]
    # table_columns = ['model_id', 'cmatrix', 'barcode', 'drugset_id'] + metrics

    # Get the combination names for the project
    # ....
    def format_combo_links(combo):
        combo_string = (f"{combo.lib1.drug_name} + {combo.lib2.drug_name}")
        combo_ref = f"/combination/{combo.lib1_id}+{combo.lib2_id}"
        return dcc.Link(combo_string, href=combo_ref)

    combo_links = [format_combo_links(combo) for combo in
                   project.combinations]

    return html.Div([

        html.H2(f"{project.name} Overview", className='my-5'),
        html.Div(className='row', children=[

            html.Div(
                className='col-10',
                children=[
                    dcc.Tabs(id="tabs", value='overview', children=[
                        dcc.Tab(label='Overview', value='overview'),
                        dcc.Tab(label='FlexiScatter', value='scatter'),
                    ]),
                    html.Div(id='tabs-content'),
                ]),
            html.Div(
                children=[html.H3("Combinations")] +
                         [html.Div([combo_link, html.Br()]) for combo_link in
                          sorted(combo_links, key=lambda x: x.children)],
                className='col-2'
            ),
            # html.Div(
            #     className='col-12',
            #     children=[
            #         dt.DataTable(
            #             rows=summary.to_dict('records'),
            #             columns=table_columns,
            #             row_selectable=True,
            #             filterable=True,
            #             sortable=True,
            #             selected_row_indices=[],
            #             editable=False,
            #             id='datatable1_2'
            #         )
            #     ]
            #
            # )
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