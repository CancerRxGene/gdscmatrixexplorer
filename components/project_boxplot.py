from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, Model
from utils import matrix_metrics, get_all_tissues, get_all_cancer_types, matrix_hover_label


def layout():
    return dbc.Row([
        dcc.Location('project-boxplot-url'),
        dbc.Col(width=6,
                className="mt-2 mb-4",
                children=[dbc.Form(inline=True, children=dbc.FormGroup([
                    dbc.Label('Tissue', html_for='tissue', className='mr-2'),
                    dcc.Dropdown(
                        options=[{'label': c, 'value': c} for c in get_all_tissues()],
                        id='tissue',
                        className='flex-grow-1',
                        multi=True
                    )
                ])),
                          dbc.Form(inline=True, className='mt-2', children=dbc.FormGroup([
                              dbc.Label('Cancer type', html_for='cancertype', className='mr-2'),
                              dcc.Dropdown(
                                  options=[{'label': c, 'value': c} for c in get_all_cancer_types()],
                                  id='cancertype',
                                  className='flex-grow-1',
                                  multi=True
                              )
                          ]))
                          ]
                ),
        dbc.Col(
            width=6,
            className="mt-2 mb-4",
            children=dbc.Form(inline=True, children=dbc.FormGroup([
                dbc.Label('Metric', html_for='boxplot-value', className='mr-2'),
                dcc.Dropdown(
                    options=list(matrix_metrics.values()),
                    value='bliss_matrix',
                    id='boxplot-value',
                    className='flex-grow-1',
                    clearable=False
                )
            ]))
        ),
        dbc.Col(
            width=12,
            children=dcc.Loading(dcc.Graph(id='project-boxplot'), className='gdsc-spinner')
        )
    ])


# @lru_cache()
def get_boxplot_summary_data(boxplot_value, project_id, tissue, cancertype):
    all_matrices_query = session.query(getattr(MatrixResult, boxplot_value),
                                       MatrixResult.barcode,
                                       MatrixResult.cmatrix,
                                       MatrixResult.lib1_id,
                                       MatrixResult.lib2_id,
                                       Model.cell_line_name.label('model_name'),
                                       Model.tissue,
                                       Model.cancer_type) \
        .filter(Model.id == MatrixResult.model_id)\
        .filter(MatrixResult.project_id == int(project_id))

    if tissue:
        all_matrices_query = all_matrices_query\
            .filter(Model.tissue.in_(tissue))

    if cancertype:
        all_matrices_query = all_matrices_query\
            .filter(Model.cancer_type.in_(cancertype))

    summary = pd.read_sql(all_matrices_query.statement,
                          all_matrices_query.session.bind)

    all_drugs = pd.read_sql_table('drugs', session.bind)

    summary = summary.merge(all_drugs, left_on='lib1_id', right_on='id') \
        .merge(all_drugs, left_on='lib2_id', right_on='id',
               suffixes=['_lib1', '_lib2'])
    summary['combo_id'] = str(project_id) + "::" + \
                          summary.lib1_id.astype(str) + "::" + \
                          summary.lib2_id.astype(str)

    return summary

@lru_cache()
@app.callback(
    [dash.dependencies.Output('project-boxplot', 'figure'),
     dash.dependencies.Output('cancertype', 'options')
     ],
    [dash.dependencies.Input('boxplot-value', 'value'),
     dash.dependencies.Input('project-id', 'children'),
     dash.dependencies.Input('tissue', 'value'),
     dash.dependencies.Input('cancertype', 'value')]
)
def update_boxplot(boxplot_value, project_id, tissue, cancertype):

    print(tissue)

    print(cancertype)

    summary = get_boxplot_summary_data(boxplot_value, project_id, tissue, cancertype)

    if tissue:
        cancer_type_options = [
            ct[0]
            for ct in session.query(Model.cancer_type)
                .filter(Model.tissue.in_(tissue))\
                .distinct()\
                .all()]
    else:
        cancer_type_options = get_all_cancer_types()

    ct_options = [{'label': c, 'value': c} for c in sorted(cancer_type_options)]

    return (get_boxplot(summary, boxplot_value),
            ct_options)


def get_boxplot(summary, boxplot_value):
    data = []
    for combo_id in summary[['combo_id', boxplot_value]].groupby(by='combo_id', as_index=False).median().sort_values(by=boxplot_value).combo_id:
        subset = summary[summary.combo_id == combo_id]
        data.append(
            go.Box(
                name=f"{subset.iloc[0].name_lib1} + {subset.iloc[0].name_lib2}",
                x=subset[boxplot_value],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=4,
                    opacity=0.5
                ),
                text=matrix_hover_label(subset),
                customdata=[{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in subset.itertuples(index=False)],
                hoveron='points',
                hoverinfo='text',
            )
        )

    return {
        'data': data,
        'layout': go.Layout(
            height=1000,
            margin=dict(l=150, r=70, b=80, t=20),
            showlegend=False,
            xaxis={'type': 'log' if 'index' in boxplot_value else 'linear',
                   'title': matrix_metrics[boxplot_value]['label']},
        )
    }

@app.callback(
    dash.dependencies.Output('project-boxplot-url', 'pathname'),
    [dash.dependencies.Input('project-boxplot', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        p = clicked['points'][0]['customdata']
        return p['to']
    else:
        return "/"
