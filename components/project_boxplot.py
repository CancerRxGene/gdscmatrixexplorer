import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import and_

from app import app
from db import session
from models import MatrixResult, Combination, Model
from utils import metrics

def tissues():
    tissues = [s[0] for s in session.query(Model.tissue).distinct().all()]
    tissues.insert(0,'Pan-cancer')
    return tissues

def layout(project_id):
    return html.Div(className='row', children=[
        dcc.Location('project-boxplot-url'),
        html.Div(
                className="col-12 mt-2 mb-4",
                children=[
                    html.Label('X-Axis', htmlFor='boxplot-value'),
                    dcc.Dropdown(
                        options=[{'label': c, 'value': c} for c in metrics],
                        value='Bliss_excess',
                        id='boxplot-value'
                    )
                ]
            ),
        html.Div(
            className="col-12 mt-2 mb-4",
            children=[
                html.Label('Tissue', htmlFor='tissue'),
                dcc.Dropdown(
                    options=[{'label': c, 'value': c} for c in tissues()],
                    value='Pan-cancer',
                    id='tissue'
                )
            ]
        ),
            html.Div(
                className="col-12",
                children=dcc.Graph(id='project-boxplot')
            )
    ])


@app.callback(
    dash.dependencies.Output('project-boxplot', 'figure'),
    [dash.dependencies.Input('boxplot-value', 'value'),
     dash.dependencies.Input('project-id', 'children'),
     dash.dependencies.Input('tissue', 'value')]
)
def update_boxplot(boxplot_value, project_id,tissue):

    all_matrices_query = session.query(MatrixResult.project_id, getattr(MatrixResult, boxplot_value), MatrixResult.barcode, MatrixResult.cmatrix, Combination.lib1_id, Combination.lib2_id)\
        .join(Combination)\
        .filter(and_(MatrixResult.project_id == Combination.project_id,
                     MatrixResult.lib1_id == Combination.lib1_id,
                     MatrixResult.lib2_id == Combination.lib2_id))\
        .filter(MatrixResult.project_id == int(project_id))

    if tissue != 'Pan-cancer':
        all_matrices_query =  all_matrices_query.join(Model).filter(Model.tissue == tissue)

    summary = pd.read_sql(all_matrices_query.statement, all_matrices_query.session.bind)

    all_drugs = pd.read_sql_table('drugs', session.bind)

    summary = summary.merge(all_drugs, left_on='lib1_id', right_on='id')\
        .merge(all_drugs, left_on='lib2_id', right_on='id', suffixes=['_lib1', '_lib2'])
    summary['combo_id'] = summary.project_id.astype(str) + "::" + summary.lib1_id.astype(str) + "::" + summary.lib2_id.astype(str)

    def get_drug_names(summary, combo_id):
        row = next(summary.drop_duplicates(subset=['combo_id']).query("combo_id == @combo_id").itertuples())
        return f"{row.drug_name_lib1} - {row.drug_name_lib2}"

    return {
        'data': [
            go.Box(
                # name=str(cm),
                name=get_drug_names(summary, combo_id),
                x=summary.query("combo_id == @combo_id")[boxplot_value],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=4,
                    opacity=0.5
                ),
                customdata=[{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in summary.query("combo_id == @combo_id").itertuples(index=False)],
                hoveron='points'
            )
            for combo_id in summary[['combo_id', boxplot_value]].\
                groupby(by='combo_id', as_index=False).\
                median().\
                sort_values(by=boxplot_value).\
                combo_id
        ],
        'layout': go.Layout(
            height=1000,
            margin=dict(l=150, r=70, b=80, t=20),
            showlegend=False,
            xaxis={'type': 'log' if 'index' in boxplot_value else 'linear',
                   'title': boxplot_value.replace('_', ' ')}
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
