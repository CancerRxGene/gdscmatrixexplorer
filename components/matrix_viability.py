from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from app import app
from db import session
from models import SingleAgentWellResult, WellResult
from utils import inhibition_colorscale, viability_colorscale, get_matrix_from_url, \
    float_formatter


def layout():
    available_viability_metrics = ['viability', 'inhibition']

    return dbc.Row(className='pb-5', children=[
        dbc.Col(width=12, children=[
            html.Div(className='border bg-white p-4 shadow-sm', children=[
                dbc.Row([
                    dbc.Col(width=12, className='d-flex flex-row', children=[
                        dbc.Col(width='auto', children=[
                            html.H3(["Measured activity"], className='pt-1'),
                        ]),
                        dbc.Col(width=3, children=
                            dcc.Dropdown(
                                id='viability-heatmap-zvalue',
                                options=[{'label': i.capitalize(), 'value': i} for i in
                                         available_viability_metrics],
                                value='inhibition',
                                searchable=False,
                                clearable=False
                            )
                        )
                    ]),
                    dbc.Col(html.Hr(), width=12)
                ]),

                dbc.Row([
                    dbc.Col(width=2,className='align-top', children=[dcc.Graph(id='lib2-viability-heatmap',config={'displayModeBar': False}), ]),
                    dbc.Col(width=6, children=[
                        dbc.Row(
                            children=dcc.Loading(dcc.Graph(id='viability-heatmap'), className='gdsc-spinner')
                        ),
                        dbc.Row(children=dcc.Graph(id='lib1-viability-heatmap',config={'displayModeBar': False})),
                    ]),

                    dbc.Col(width=4, children=
                          dcc.Loading(dcc.Graph(id='viability-surface'), className='gdsc-spinner'),
                     ),
                ]),

            ])
        ])
    ])


@lru_cache()
def get_viability_matrix_from_url(pathname):
    matrix = get_matrix_from_url(pathname)

    well_query = matrix.well_results.with_entities(
        WellResult.lib1_conc, WellResult.lib2_conc, WellResult.inhibition
    )
    matrix_df = pd.read_sql(well_query.statement, session.bind)
    matrix_df['viability'] = 1 - matrix_df.inhibition
    return matrix_df


@app.callback(
    [dash.dependencies.Output('viability-heatmap', 'figure'),
     dash.dependencies.Output('viability-surface', 'figure'),
     dash.dependencies.Output('lib1-viability-heatmap','figure'),
     dash.dependencies.Output('lib2-viability-heatmap','figure'),],
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value')],
    [dash.dependencies.State('url', 'pathname')]
)
@lru_cache(maxsize=10000)
def update_viability_plots(viability_heatmap_zvalue, pathname):
    matrix = get_matrix_from_url(pathname)
    matrix_df = get_viability_matrix_from_url(pathname)

    # sort the data frame before the conc convert to scientific notation
    matrix_df = matrix_df.sort_values(['lib1_conc', 'lib2_conc'])


    heatmap = generate_viability_heatmap(matrix_df, viability_heatmap_zvalue)
    surface = generate_viability_surface(matrix_df, viability_heatmap_zvalue,
                                         [matrix.combination.lib1.name, matrix.combination.lib2.name])
    lib1_heatmap = single_agent_heatmap(
        metric=viability_heatmap_zvalue,
        tag=matrix.lib1_tag,
        drug_name=matrix.combination.lib1.name,
        barcode=matrix.barcode,
        orientation='h'
    )
    lib2_heatmap = single_agent_heatmap(
        metric=viability_heatmap_zvalue,
        tag=matrix.lib2_tag,
        drug_name=matrix.combination.lib2.name,
        barcode=matrix.barcode,
        orientation='v'
    )

    return heatmap, surface, lib1_heatmap, lib2_heatmap


def generate_viability_heatmap(matrix_df, metric):

    x = matrix_df.lib1_conc.map(float_formatter)
    y = matrix_df.lib2_conc.map(float_formatter)

    return {
        'data': [
            go.Heatmap(
                x=x,
                y=y,
                z=matrix_df[metric],
                zmax=1,
                zmin=0,
                colorscale=inhibition_colorscale if metric == 'inhibition' else viability_colorscale,
            )

        ],
        'layout': go.Layout(title=metric.capitalize(),
                            xaxis={'type': 'category',
                                   'showticklabels': False
                                   },
                            yaxis={'type': 'category',
                                   'showticklabels': False
                                  },
                            margin={'l': 5, 't': 70,'b': 15, 'r':0},
                            width=500,
                            height=400
                            )
    }


def generate_viability_surface(matrix_df, metric, drug_names):
    drug1, drug2 = drug_names

    # matrix_df['lib1_conc'] = matrix_df.lib1_conc.map(float_formatter)
    # matrix_df['lib2_conc'] = matrix_df.lib2_conc.map(float_formatter)
    zvalues_table = matrix_df.pivot(
        index='lib2_conc', columns='lib1_conc', values=metric)

    # change lib2_conc ascending to 1
    zvalues_table = zvalues_table.sort_values(by=['lib2_conc'], ascending=1)
    lib1_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib1_conc')
    lib1_conc_table = lib1_conc_table.sort_values(by=['lib2_conc'], ascending=1)
    lib2_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib2_conc')
    lib2_conc_table = lib2_conc_table.sort_values(by=['lib2_conc'], ascending=1)

    return {
        'data': [
            go.Surface(
                z=zvalues_table.values,
                x=lib1_conc_table.values,
                y=lib2_conc_table.values,
                colorscale=inhibition_colorscale if metric == 'inhibition' else viability_colorscale,
                cmax=1,
                cmin=0,
                showscale=False,
            )
        ],
        'layout': go.Layout(
            margin=go.layout.Margin(l=10, r=10, b=40, t=40),
            scene={
                'xaxis': {
                    'type': 'category',
                    'title': drug1,
                    'showticklabels': False,
                    'titlefont': {
                        'size': 12
                    },
                },
                'yaxis': {
                    'type': 'category',
                    'title': drug2,
                    'ticktext': None,
                    'showticklabels': False,
                    'titlefont': {'size': 12},
                },
                'zaxis': {
                    'range': (0, 1),
                    'title': metric,
                    'titlefont': {
                        'size': 12
                    },
                    'tickfont': {
                        'size': 10
                    }
                },
                'camera': dict(eye=dict(x=1, y=-2, z=1.25)),
            }
        )
    }


@lru_cache()
def single_agent_heatmap(metric, tag, drug_name, barcode, orientation):
    # get the single agent data
    lib_well_result = session.query(SingleAgentWellResult)\
        .filter(SingleAgentWellResult.lib_drug == tag)\
        .filter(SingleAgentWellResult.barcode == barcode)

    lib_df = pd.read_sql(lib_well_result.statement, session.bind)
    lib_df = lib_df.sort_values('conc')
    lib_df.conc = [np.format_float_scientific(conc, 3) for conc in lib_df.conc]

    if metric == 'viability':
        z = 1 - lib_df.inhibition
    else:
        z = lib_df.inhibition

    return {
        'data': [
            go.Heatmap(
                y=lib_df.conc if orientation=='v' else [1] * len(lib_df.conc),
                x=[1] * len(lib_df.conc) if orientation=='v' else lib_df.conc,
                z=z,
                zmax=1,
                zmin=0,
                colorscale=inhibition_colorscale if metric == 'inhibition' else viability_colorscale,
                showscale=False,
            )
        ],

        'layout': go.Layout(
            xaxis={'type': 'category', 'showticklabels': False},
            yaxis={'type': 'category', 'title': drug_name + " (µM)"},
            width=120,
            height=460,
            margin={'t': 70, 'r': 0, }
        ) if orientation=='v' else
            go.Layout(
               xaxis={'type': 'category', 'title': drug_name + " (µM)"},
               yaxis={'type': 'category', 'showticklabels': False},
               width=500, height=150,
               margin={'t': 30, 'l': 5}
            ),

        'config': {
            'displayModeBar': False
        }

    }