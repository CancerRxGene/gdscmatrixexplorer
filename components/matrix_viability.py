import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import json
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, SingleAgentWellResult
from utils import inhibition_colorscale, viability_colorscale


def layout(matrix: MatrixResult):
    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df['lib1_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    matrix_df['lib2_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]

    available_viability_metrics = ['viability', 'inhibition']

    matrix_df = matrix_df.assign(viability=lambda df: 1 - df.inhibition)

    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_viability_metrics]

    drug_info = json.dumps(dict(lib1_tag=matrix.lib1_tag,
                                lib2_tag=matrix.lib2_tag,
                                drug1_name=matrix.combination.lib1.name,
                                drug2_name=matrix.combination.lib2.name,
                                barcode=matrix.barcode
                                ))

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
                            children=[dcc.Graph(id='viability-heatmap')]
                        ),
                        dbc.Row(children=[dcc.Graph(id='lib1-viability-heatmap',config={'displayModeBar': False}) ]),
                    ]),

                    dbc.Col(width=4, children=[
                          dcc.Graph(id='viability-surface'),
                     ]),
                ]),

            ]),
            html.Div(id='viability-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_info', className='d-none',
                     children= drug_info)

        ])
    ])

@app.callback(
    dash.dependencies.Output('viability-heatmap', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children'),
    ]
)
def update_viability_heatmap(viability_heatmap_zvalue, matrix_json):
    matrix_df = pd.read_json(matrix_json, orient='split')

    # sort the data frame before the conc convert to scientific notation
    matrix_df = matrix_df.sort_values(['lib1_conc', 'lib2_conc'])
    matrix_df['lib1_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    matrix_df['lib2_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]
    zvalue = matrix_df[viability_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_conc,
                y=matrix_df.lib2_conc,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale=inhibition_colorscale if viability_heatmap_zvalue == 'inhibition' else viability_colorscale,
            )

        ],
        'layout': go.Layout(title=viability_heatmap_zvalue.capitalize(),
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

@app.callback(
    dash.dependencies.Output('viability-surface', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children'),
     dash.dependencies.Input('drug_names', 'children')]
)
def update_viability_surface(viability_heatmap_zvalue, matrix_json, drug_names):
    matrix_df = pd.read_json(matrix_json, orient='split')
    drug1, drug2 = drug_names.split(':_:')

    zvalues_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values=viability_heatmap_zvalue)

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
                colorscale= inhibition_colorscale if viability_heatmap_zvalue == 'inhibition' else viability_colorscale,
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
                    'title': viability_heatmap_zvalue,
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

@app.callback(
    dash.dependencies.Output('lib1-viability-heatmap','figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('drug_info', 'children')
    ]
)
def update_lib1_heatmap(viability_heatmap_zvalue, drug_info):
    drug_info=json.loads(drug_info)
    tag = drug_info['lib1_tag']
    barcode = drug_info['barcode']
    drug_name = drug_info['drug1_name']

    return single_agent_heatmap(viability_heatmap_zvalue, tag, drug_name, barcode,'h')

@app.callback(
    dash.dependencies.Output('lib2-viability-heatmap','figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('drug_info', 'children'),
    ]
)
def update_lib2_heatmap(viability_heatmap_zvalue, drug_info):
    drug_info = json.loads(drug_info)
    tag = drug_info['lib2_tag']
    barcode = drug_info['barcode']
    drug_name = drug_info['drug2_name']

    return single_agent_heatmap(viability_heatmap_zvalue, tag, drug_name, barcode,'v')


def single_agent_heatmap(viability_heatmap_zvalue, tag, drug_name, barcode, orientation):
    # get the single agent data
    lib_well_result = session.query(SingleAgentWellResult).filter(SingleAgentWellResult.lib_drug == tag).filter(
        SingleAgentWellResult.barcode == barcode)

    lib_df = pd.read_sql(lib_well_result.statement, session.bind)
    lib_df = lib_df.sort_values('conc')
    lib_df.conc = [np.format_float_scientific(conc, 3) for conc in lib_df.conc]

    if viability_heatmap_zvalue == 'viability':
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
                colorscale=inhibition_colorscale if viability_heatmap_zvalue == 'inhibition' else viability_colorscale,
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