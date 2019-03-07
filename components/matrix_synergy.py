from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from components.synergy_info.syn_info import infoblock_matrix

from app import app
from db import session
from models import WellResult
from utils import get_metric_axis_range, well_metrics, synergy_colorscale, \
    get_matrix_from_url, float_formatter


def layout(matrix):

    drug1 = matrix.combination.lib1.name
    drug2 = matrix.combination.lib2.name

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(viability=lambda df: 1 - df.inhibition)
    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + list(well_metrics.keys())]

    return dbc.Row(
        dbc.Col(width=12, children=[
            html.Div(className='border p-3 bg-white shadow-sm', children=[
                dbc.Row([
                    dbc.Col(width=12, className='d-flex flex-row', children=[
                        dbc.Col(width='auto', children=
                            html.H3(["Drug combination interaction"], className='pt-1'),
                        ),
                        dbc.Col(width=3, children=
                            dcc.Dropdown(
                                id='combo-heatmap-zvalue',
                                options=list(well_metrics.values()),
                                value='bliss_excess',
                                searchable=False,
                                clearable=False
                            )
                        ),
                    ]),
                    dbc.Col(html.Hr(), width=12)
                ]),
                dbc.Row([
                    dbc.Col(width=7, children=[
                        dcc.Graph(id='combo-heatmap'),
                        dcc.Graph(id='combo-surface')
                    ]),
                    dbc.Col(width={"size": 4, "offset": 1}, children=[
                        infoblock_matrix(matrix)
                    ])
                ])
            ]),
            html.Div(id='combo-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_names', style={'display': 'none'},
                     children=f"{drug1}:_:{drug2}")
        ])
    )


@lru_cache()
def get_synergy_matrix_from_url(pathname):
    matrix = get_matrix_from_url(pathname)

    well_query = matrix.well_results
    matrix_df = pd.read_sql(well_query.statement, session.bind)
    matrix_df['viability'] = 1 - matrix_df.inhibition
    return matrix_df


@app.callback(
    [dash.dependencies.Output('combo-heatmap', 'figure'),
     dash.dependencies.Output('combo-surface', 'figure')],
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value')],
    [dash.dependencies.State('url', 'pathname')]
)
def update_synergy_plots(metric, pathname):
    matrix = get_matrix_from_url(pathname)
    matrix_df = get_synergy_matrix_from_url(pathname)

    # sort the data frame before the conc convert to scientific notation
    matrix_df = matrix_df.sort_values(['lib1_conc', 'lib2_conc'])

    combo_heatmap = generate_combo_heatmap(
        matrix_df, metric, [matrix.combination.lib1.name, matrix.combination.lib2.name]
    )
    combo_surface = generate_combo_surface(
        matrix_df, metric, [matrix.combination.lib1.name, matrix.combination.lib2.name]
    )

    return combo_heatmap, combo_surface


def generate_combo_heatmap(matrix_df, metric, drug_names):

    # sort the data frame before the conc convert to scientific notation
    x = matrix_df['lib1_conc'].astype('category').map(float_formatter)
    y = matrix_df['lib2_conc'].astype('category').map(float_formatter)

    zvalue = matrix_df[metric]
    zmin, zmax = get_metric_axis_range(metric)

    return {
        'data': [
            go.Heatmap(
                x=x,
                y=y,
                z=zvalue,
                zmax=zmax,
                zmin=zmin,
                colorscale=synergy_colorscale,
                reversescale=False
            )
        ],
        'layout': go.Layout(title=well_metrics[metric]['label'],
                            xaxis={'type': 'category',
                                   'title': drug_names[0] + " µM"
                                   },
                            yaxis={'type': 'category',
                                   'title': drug_names[1] + " µM"
                                   },
                            margin={'l': 100}
                            )
    }


def generate_combo_surface(matrix_df, metric, drug_names):

    xaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib1_conc]
    yaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib2_conc]

    # change lib2_conc ascending to 1
    zvalues_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values=metric)\
        .sort_values(by=['lib2_conc'], ascending=True)
    lib1_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib1_conc')\
        .sort_values(by=['lib2_conc'], ascending=True)
    lib2_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib2_conc')\
        .sort_values(by=['lib2_conc'], ascending=True)
    zmin, zmax = get_metric_axis_range(metric)

    return {
        'data': [
            go.Surface(
                z=zvalues_table.values,
                x=lib1_conc_table.values,
                y=lib2_conc_table.values,
                colorscale=synergy_colorscale,
                reversescale=True,
                cmax=zmax,
                cmin=zmin,
                showscale=False
            )
        ],
        'layout': go.Layout(
            margin=go.layout.Margin(
                l=40,
                r=40,
                b=40,
                t=40,
                pad=10
            ),
            scene={
                'xaxis': {
                    'type': 'category',
                    'title': drug_names[0] + ' µM',
                    'ticktext': xaxis_labels,
                    'tickvals': matrix_df.lib1_conc,
                    'titlefont': {
                        'size': 12
                    },
                    'tickfont': {
                        'size': 10
                    }
                },
                'yaxis': {
                    'type': 'category',
                    'title': drug_names[1] + ' µM',
                    'ticktext': yaxis_labels,
                    'tickvals': matrix_df.lib2_conc,
                    'titlefont': {
                        'size': 12
                    },
                    'tickfont': {
                        'size': 10
                    }
                },
                'zaxis': {
                    'range': (zmin, zmax),
                    'title': metric,
                    'titlefont': {
                        'size': 12
                    },
                    'tickfont': {
                        'size': 10
                    }
                },
                'camera': {
                    'eye': {
                        'x': -1.25,
                        'y': -1.25,
                        'z': 1.25
                    }
                }
            }
        )
    }
