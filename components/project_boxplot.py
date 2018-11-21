import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import and_

from app import app
from db import session
from models import MatrixResult, Combination
from utils import metrics


def layout(project_id):

    return html.Div(className='row', children=[
        dcc.Location('project-boxplot-url'),
        html.Div(
                className="col-12 mt-2 mb-4",
                children=[
                    html.Label('Y-Axis', htmlFor='y-axis-select-boxplot'),
                    dcc.Dropdown(
                        options=[{'label': c, 'value': c} for c in metrics],
                        value='Bliss_excess',
                        id='y-axis-select-boxplot'
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
    [dash.dependencies.Input('y-axis-select-boxplot', 'value'),
     dash.dependencies.Input('project-id', 'children')]
)
def update_boxplot(y_axis_field, project_id):

    all_matrices_query = session.query(getattr(MatrixResult, y_axis_field), MatrixResult.barcode, MatrixResult.cmatrix, MatrixResult.drugset_id, Combination.lib1_id, Combination.lib2_id)\
        .join(Combination)\
        .filter(and_(MatrixResult.drugset_id == Combination.drugset_id,
                     MatrixResult.cmatrix == Combination.cmatrix))\
        .filter(MatrixResult.project_id == int(project_id))

    summary = pd.read_sql(all_matrices_query.statement, all_matrices_query.session.bind)

    all_drugs = pd.read_sql_table('drugs', session.bind)

    summary = summary.merge(all_drugs, left_on='lib1_id', right_on='id')\
        .merge(all_drugs, left_on='lib2_id', right_on='id', suffixes=['_lib1', '_lib2'])
    summary['combo_id'] = summary.cmatrix.astype(str) + "::" + summary.drugset_id.astype(str)

    def get_drug_names(summary, combo_id):
        row = next(summary.drop_duplicates(subset=['combo_id']).query("combo_id == @combo_id").itertuples())
        return f"{row.drug_name_lib1} - {row.drug_name_lib2}"

    return {
        'data': [
            go.Box(
                # name=str(cm),
                name=get_drug_names(summary, combo_id),
                y=summary.query("combo_id == @combo_id")[y_axis_field],
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
            ) for combo_id in summary.combo_id.unique()
        ],
        'layout': go.Layout(
            height=500,
            margin=dict(l=50, r=70, b=80, t=20),
            showlegend=False,
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': y_axis_field.replace('_', ' ')}
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