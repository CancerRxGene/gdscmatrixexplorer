from functools import lru_cache

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import sqlalchemy as sa
from sqlalchemy import and_, or_

from app import app
from db import session
from models import MatrixResult, Project, Combination, Model
from utils import plot_colors,  matrix_metrics, get_all_tissues, get_all_cancer_types, matrix_hover_label


def layout(project_id):
    try:
        project = session.query(Project).get(project_id)

    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    return dbc.Row([
        dcc.Location('project-scatter-url'),
        dbc.Col(width=12, children=[
            dbc.Row([
                dbc.Col(
                    width=5,
                    className='mt-2 mb-4',
                    children=[
                        html.H4("Plot settings"),
                        dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                            html.Label('X-Axis', className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=list(matrix_metrics.values()),
                                value='bliss_matrix',
                                id='x-axis-select'
                            ),
                        ])),
                        dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                            html.Label('Y-Axis', className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=list(matrix_metrics.values()),
                                value='combo_maxe',
                                id='y-axis-select'
                            )
                        ])),
                        dbc.Form(inline=True, children=dbc.FormGroup([
                            html.Label('Color', className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=[{'label': l, 'value': v} for l, v in
                                         [('Default', 'default'),
                                          ("Cell Line", 'model_name'),
                                          ("Tissue", 'tissue'),
                                          ("Cancer Type", "cancer_type"),
                                          ("Combination", 'combo_id')]],
                                value='default',
                                id='color-select'
                            )
                        ]))
                    ]),
                dbc.Col(
                    width={'size': 6, 'offset': 1},
                    className='mt-2 mb-4',
                    children=[
                        html.H4("Data filters"),
                        dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                            html.Label('Tissue', className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=[{'label': c, 'value': c} for c in
                                         get_all_tissues()],
                                id='tissue-select',
                                multi=True
                            ),
                        ])),
                        dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                            html.Label('Cancer type',
                                       className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=[{'label': c, 'value': c} for c in
                                         get_all_cancer_types()],
                                id='cancertype-select',
                                multi=True
                            ),
                        ])),
                        dbc.Form(inline=True, children=dbc.FormGroup([
                            html.Label('Combination', className="w-25 justify-content-start"),
                            dcc.Dropdown(
                                options=[{'label': f"{c.lib1.name} + {c.lib2.name}",
                                          'value': f"{c.lib1_id}+{c.lib2_id}"} for c in
                                         project.combinations],
                                id='combination-select',
                                multi=True,
                            ),
                        ]))
                    ]),
             ]),
            dbc.Row(id='correlation', className='ml-3 mt-2'),
            dbc.Row(dcc.Loading(dcc.Graph(id='project-scatter'), className='gdsc-spinner'))
        ])
    ])

@app.callback(
    [dash.dependencies.Output('project-scatter', 'figure'),
     dash.dependencies.Output('correlation', 'children'),
     dash.dependencies.Output('cancertype-select', 'options'),
     ],
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value'),
     dash.dependencies.Input('color-select', 'value'),
     dash.dependencies.Input('tissue-select', 'value'),
     dash.dependencies.Input('cancertype-select', 'value'),
     dash.dependencies.Input('combination-select', 'value'),
     dash.dependencies.Input('project-id', 'children')])
def update_scatter(x_axis_field, y_axis_field, color_field, tissues, cancer_types, combinations, project_id):
    if isinstance(combinations, list):
        combinations = tuple(combinations)
    if isinstance(tissues, list):
        tissues = tuple(tissues)
    if isinstance(cancer_types, list):
        cancer_types = tuple(cancer_types)

    return cached_update_scatter(x_axis_field, y_axis_field, color_field, tissues, cancer_types, combinations, project_id)


@lru_cache(maxsize=1000)
def cached_update_scatter(x_axis_field, y_axis_field, color_field, tissues, cancer_types, combinations, project_id):
    all_matrices_query = session.query(MatrixResult.project_id,
        getattr(MatrixResult, x_axis_field),
        getattr(MatrixResult, y_axis_field),
        MatrixResult.barcode, MatrixResult.cmatrix, MatrixResult.drugset_id,
        Combination.lib1_id, Combination.lib2_id,
        Model.cell_line_name.label('model_name'), Model.tissue, Model.cancer_type
    ) \
        .join(Combination) \
        .join(Model) \
        .filter(and_(MatrixResult.project_id == Combination.project_id,
                     MatrixResult.lib1_id == Combination.lib1_id,
                     MatrixResult.lib2_id == Combination.lib2_id)) \
        .filter(MatrixResult.model_id == Model.id) \
        .filter(MatrixResult.project_id == int(project_id))

    if tissues:
        all_matrices_query = all_matrices_query.filter(Model.tissue.in_(tissues))
    if cancer_types:
        all_matrices_query = all_matrices_query.filter(Model.cancer_type.in_(cancer_types))

    if combinations:
        rules = []
        for c in combinations:
            lib1, lib2 = c.split('+')
            rule = and_(Combination.lib1_id == lib1, Combination.lib2_id == lib2)
            rules.append(rule)

        all_matrices_query = all_matrices_query .filter(or_(*rules))

    summary = pd.read_sql(all_matrices_query.statement,
                          all_matrices_query.session.bind)

    all_drugs = pd.read_sql_table('drugs', session.bind)

    summary = summary.merge(all_drugs, left_on='lib1_id', right_on='id') \
        .merge(all_drugs, left_on='lib2_id', right_on='id',
               suffixes=['_lib1', '_lib2'])
    summary['combo_id'] = summary.project_id.astype(str) + "::" + summary.lib1_id.astype(str) + "::" + summary.lib2_id.astype(str)

    if tissues:
        cancer_type_options = [
            ct[0]
            for ct in session.query(Model.cancer_type)
                .filter(Model.tissue.in_(tissues))\
                .distinct()\
                .all()]
    else:
        cancer_type_options = get_all_cancer_types()

    ct_options = [{'label': c, 'value': c} for c in sorted(cancer_type_options)]

    return (get_scatter(summary, x_axis_field, y_axis_field, color_field),
            get_correlation(summary, x_axis_field, y_axis_field),
            ct_options)


def get_correlation(summary, x_axis_field, y_axis_field):

    corr = summary[[x_axis_field, y_axis_field]].corr().iloc[0,1]
    return html.Div([html.Span("Pearson correlation: "), html.Strong(f"{round(corr, 3)}")])


def get_scatter(summary, x_axis_field, y_axis_field, color_field):
    color_values = {}
    if color_field != 'default':
        for i, v in enumerate(summary[color_field].unique()):
            color_values[v] = plot_colors[i % len(plot_colors)]

    fig_data = summary
    return {
        'data': [
            go.Scattergl(
                x=fig_data[x_axis_field],
                y=fig_data[y_axis_field],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 4,
                    'color': [ord(x) for x in fig_data.model_name.str[
                        0]] if color_field == 'default' else [color_values[x]
                                                              for x in fig_data[
                                                                  color_field]]
                },
                text=matrix_hover_label(fig_data),
                customdata=[{"barcode": row.barcode, "cmatrix": row.cmatrix,
                             "to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in fig_data.itertuples(index=False)]
            )
        ],
        'layout': go.Layout(
            height=750,
            hovermode='closest',
            xaxis={'type': 'log' if 'index' in x_axis_field else 'linear',
                   'title': matrix_metrics[x_axis_field]['label']},
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': matrix_metrics[y_axis_field]['label']}
        )
    }

@app.callback(
    dash.dependencies.Output('project-scatter-url', 'pathname'),
    [dash.dependencies.Input('project-scatter', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        p = clicked['points'][0]['customdata']
        return p['to']
    else:
        return "/"
