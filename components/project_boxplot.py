import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, DoseResponseCurve


def layout(project_id):
    metrics = ["HSA_excess", "HSA_excess_syn", "HSA_excess_well_count",
               "HSA_excess_window", "HSA_excess_window_syn", "Bliss_excess",
               "Bliss_excess_syn", "Bliss_excess_well_count",
               "Bliss_excess_window",
               "Bliss_excess_window_syn"
               ]

    return html.Div(className='row', children=[
        dcc.Location('project-boxplot-url'),
        html.Div(
                className="col-12 mt-2 mb-4",
                children=[
                    html.Label('y-axis', htmlFor='y-axis-select-boxplot'),
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

    all_matrices_query = session.query(MatrixResult) \
        .filter_by(project_id=int(project_id))

    summary = pd.read_sql(all_matrices_query.statement, all_matrices_query.session.bind)

    ds = []
    cmatrix = []
    lib1 = []
    lib2 = []
    lib_names = []
    cm = []

    for matrix in all_matrices_query.all():
        ds.append(matrix.drugset_id)
        cmatrix.append(matrix.cmatrix)
        lib1.append(matrix.combination.lib1.drug_name)
        lib2.append(matrix.combination.lib2.drug_name)
        lib_names.append(f"{matrix.combination.lib1.drug_name} {matrix.combination.lib2.drug_name}")
        cm.append(f"{matrix.drugset_id}::{matrix.cmatrix}")

    lib_names_df = pd.DataFrame({
        'drugset_id' : ds,
        'cmatrix' : cmatrix,
        'lib1_name' : lib1,
        'lib2_name' : lib2,
        'lib_names' : lib_names,
        'cm' : cm
    }).drop_duplicates()

    summary = pd.merge(lib_names_df, summary, "right")

    return {
        'data': [
            go.Box(
                # name=str(cm),
                name=np.array2string(summary.query("cm == @cm")['lib_names'].unique()),
                y=summary.query("cm == @cm")[y_axis_field],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=4,
                    opacity=0.5
                ),
                customdata=[{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in summary.query("cm == @cm").itertuples(index=False)]
            ) for cm in summary.cm.unique()
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
