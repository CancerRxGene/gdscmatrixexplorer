from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, Model
from utils import matrix_metrics, get_all_tissues, matrix_hover_label

def layout():

    return dbc.Row([
        dcc.Location('project-boxplot-url'),
        dbc.Col(
            width=6,
            className="mt-2 mb-4",
            children=dbc.Form(inline=True, children=dbc.FormGroup([
                dbc.Label('Metric', html_for='boxplot-value', className='mr-2'),
                dcc.Dropdown(
                    options=list(matrix_metrics.values()),
                    value='Bliss_excess',
                    id='boxplot-value',
                    className='flex-grow-1',
                )
            ]))
        ),
        dbc.Col(width=6,
                className="mt-2 mb-4",
            children=dbc.Form(inline=True, children=dbc.FormGroup([
                dbc.Label('Tissue', html_for='tissue', className='mr-2'),
                dcc.Dropdown(
                    options=[{'label': c, 'value': c} for c in get_all_tissues()],
                    id='tissue',
                    className='flex-grow-1',
                )
            ]))
        ),
        dbc.Col(
            width=12,
            children=dcc.Graph(id='project-boxplot')
        )
    ])


@lru_cache()
def get_boxplot_summary_data(boxplot_value, project_id, tissue):
    all_matrices_query = session.query(getattr(MatrixResult, boxplot_value),
                                       MatrixResult.barcode,
                                       MatrixResult.cmatrix,
                                       MatrixResult.lib1_id,
                                       MatrixResult.lib2_id,
                                       Model.name.label('model_name'),
                                       Model.tissue) \
        .filter(Model.id == MatrixResult.model_id)\
        .filter(MatrixResult.project_id == int(project_id))

    if tissue:
        all_matrices_query = all_matrices_query.join(Model) \
            .filter(Model.tissue == tissue)

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


@app.callback(
    dash.dependencies.Output('project-boxplot', 'figure'),
    [dash.dependencies.Input('boxplot-value', 'value'),
     dash.dependencies.Input('project-id', 'children'),
     dash.dependencies.Input('tissue', 'value')]
)
def update_boxplot(boxplot_value, project_id, tissue):

    summary = get_boxplot_summary_data(boxplot_value, project_id, tissue)

    def get_drug_names(summary, combo_id):
        row = next(summary.drop_duplicates(subset=['combo_id']).query("combo_id == @combo_id").itertuples())
        return f"{row.drug_name_lib1} + {row.drug_name_lib2}"

    return {
        'data': [
            go.Box(
                name=get_drug_names(summary, combo_id),
                x=summary.query("combo_id == @combo_id")[boxplot_value],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=4,
                    opacity=0.5
                ),
                text=matrix_hover_label(summary),
                customdata=[{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in summary.query("combo_id == @combo_id").itertuples(index=False)],
                hoveron='points',
                hoverinfo='text',
            )
            for combo_id in summary[['combo_id', boxplot_value]]
                .groupby(by='combo_id', as_index=False)\
                .median()\
                .sort_values(by=boxplot_value)\
                .combo_id
        ],
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
