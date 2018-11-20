import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import pearsonr
import sqlalchemy as sa

from app import app
from db import session
from models import MatrixResult, Project


def layout(project_id):
    try:
        project = session.query(Project).get(project_id)
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    metrics = ["HSA_excess", "HSA_excess_syn", "HSA_excess_well_count",
               "HSA_excess_window", "HSA_excess_window_syn", "Bliss_excess",
               "Bliss_excess_syn", "Bliss_excess_well_count",
               "Bliss_excess_window",
               "Bliss_excess_window_syn"]




    return html.Div([
        dcc.Location('project-scatter-url'),
        html.Div(
            children=[
                html.Div(className='row mt-2 mb-4', children=[
                    html.Div(className='col-4', children=[
                        html.Label('x-axis'),
                        dcc.Dropdown(
                            options=[{'label': c, 'value': c} for c in metrics],
                            value='HSA_excess',
                            id='x-axis-select'
                        ),
                    ]),
                    html.Div(className='col-4', children=[
                        html.Label('y-axis'),
                        dcc.Dropdown(
                            options=[{'label': c, 'value': c} for c in metrics],
                            value='Bliss_excess',
                            id='y-axis-select'
                        )
                    ]),
                    html.Div(id='correlation')
                ])
            ]
        ),
        html.Div(
            className='row',
            children=html.Div(dcc.Graph(id='project-scatter'), className='col-12')
        )]
    )


@app.callback(
    dash.dependencies.Output('project-scatter', 'figure'),
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value'),
     dash.dependencies.Input('project-id', 'children')])
def update_scatter(x_axis_field, y_axis_field, project_id):
    all_matrices = session.query(MatrixResult) \
        .filter(MatrixResult.project_id == project_id) \
        .all()

    summary = pd.DataFrame([x.to_dict() for x in all_matrices])

    fig_data = summary
    return {
        'data': [
            go.Scatter(
                x=fig_data[x_axis_field],
                y=fig_data[y_axis_field],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 4,
                    'color':[ord(x) for x in fig_data.model_id.str[0]]
                },
                text=[f"drug1 - drug2<br />Cell line: {s.model_id}"  # TODO: Fill in real drug names
                      for s in fig_data.itertuples()],
                customdata=[{"barcode": row.barcode, "cmatrix": row.cmatrix,
                             "to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in fig_data.itertuples(index=False)]
            )
        ],
        'layout': go.Layout(
            height=500,
            hovermode='closest',
            xaxis={'type': 'log' if 'index' in x_axis_field else 'linear',
                   'title': x_axis_field.replace('_', ' ')},
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': y_axis_field.replace('_', ' ')}
        )
    }


@app.callback(
    dash.dependencies.Output('correlation', 'children'),
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value'),
     dash.dependencies.Input('project-id', 'children')])
def update_correlation(x_axis_field, y_axis_field, project_id):
    all_matrices_query = session.query(MatrixResult) \
        .filter_by(project_id=int(project_id))

    summary = pd.read_sql(all_matrices_query.statement,
                          all_matrices_query.session.bind)
    corr = pearsonr(
        np.log(summary[x_axis_field]) if 'index' in x_axis_field else summary[x_axis_field],
        np.log(summary[y_axis_field]) if 'index' in y_axis_field else summary[y_axis_field])
    return f"Correlation: {round(corr[0], 3)}"


@app.callback(
    dash.dependencies.Output('project-scatter-url', 'pathname'),
    [dash.dependencies.Input('project-scatter', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        p = clicked['points'][0]['customdata']
        return p['to']
    else:
        return "/"
