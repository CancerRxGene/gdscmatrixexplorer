import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import pearsonr
import sqlalchemy as sa
from sqlalchemy import and_

from app import app
from db import session
from models import MatrixResult, Project, Combination, Model
from utils import metrics, plot_colors


def layout(project_id):
    try:
        project = session.query(Project).get(project_id)
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    return html.Div([
        dcc.Location('project-scatter-url'),
        html.Div(
            children=[

                html.Div(className='row mt-2 mb-4', children=[
                    html.Div(className='col-4', children=[
                        html.Label('X-Axis'),
                        dcc.Dropdown(
                            options=[{'label': c, 'value': c} for c in metrics],
                            value='HSA_excess',
                            id='x-axis-select'
                        ),
                    ]),
                    html.Div(className='col-4', children=[
                        html.Label('Y-Axis'),
                        dcc.Dropdown(
                            options=[{'label': c, 'value': c} for c in metrics],
                            value='Bliss_excess',
                            id='y-axis-select'
                        )
                    ]),
                    html.Div(className='col-4', children=[
                        html.Label('Color'),
                        dcc.Dropdown(
                            options=[{'label': l, 'value': v} for l, v in
                                     [('Default', 'default'),
                                      ("Cell Line", 'model_name'),
                                      ("Tissue", 'tissue'),
                                      ("Combination", 'combo_id')]],
                            value='default',
                            id='color-select'
                        )
                    ]),
                    html.Div(id='correlation', className='ml-3 mt-2')
                ])
            ]
        ),
        html.Div(
            className='row',
            children=html.Div(dcc.Graph(id='project-scatter'),
                              className='col-12')
        )]
    )


@app.callback(
    dash.dependencies.Output('project-scatter', 'figure'),
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value'),
     dash.dependencies.Input('color-select', 'value'),
     dash.dependencies.Input('project-id', 'children')])
def update_scatter(x_axis_field, y_axis_field, color_field, project_id):
    all_matrices_query = session.query(
        getattr(MatrixResult, x_axis_field),
        getattr(MatrixResult, y_axis_field),
        MatrixResult.barcode, MatrixResult.cmatrix, MatrixResult.drugset_id,
        Combination.lib1_id, Combination.lib2_id,
        Model.name.label('model_name'), Model.tissue
    ) \
        .join(Combination) \
        .join(Model) \
        .filter(and_(MatrixResult.drugset_id == Combination.drugset_id,
                     MatrixResult.cmatrix == Combination.cmatrix)) \
        .filter(MatrixResult.model_id == Model.id) \
        .filter(MatrixResult.project_id == int(project_id))

    summary = pd.read_sql(all_matrices_query.statement,
                          all_matrices_query.session.bind)

    all_drugs = pd.read_sql_table('drugs', session.bind)

    summary = summary.merge(all_drugs, left_on='lib1_id', right_on='id') \
        .merge(all_drugs, left_on='lib2_id', right_on='id',
               suffixes=['_lib1', '_lib2'])
    summary['combo_id'] = summary.cmatrix.astype(
        str) + "::" + summary.drugset_id.astype(str)

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
                text=[
                    f"{s.drug_name_lib1} ({s.target_lib1}) - {s.drug_name_lib2} ({s.target_lib2})<br />"
                    f"Cell line: {s.model_name}<br />"
                    f"Tissue: {s.tissue}"
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
        np.log(summary[x_axis_field]) if 'index' in x_axis_field else summary[
            x_axis_field],
        np.log(summary[y_axis_field]) if 'index' in y_axis_field else summary[
            y_axis_field])
    return html.Div([html.Span("Pearson correlation: "), html.Strong(f"{round(corr[0], 3)}")])


@app.callback(
    dash.dependencies.Output('project-scatter-url', 'pathname'),
    [dash.dependencies.Input('project-scatter', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        p = clicked['points'][0]['customdata']
        return p['to']
    else:
        return "/"
