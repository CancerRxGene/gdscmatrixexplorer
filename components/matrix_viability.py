import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, DoseResponseCurve, SingleAgentWellResult


def layout(matrix: MatrixResult):
    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df['lib1_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    matrix_df['lib2_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]

    drug1 = matrix.combination.lib1.drug_name
    drug2 = matrix.combination.lib2.drug_name

    # find lib tag
    lib1_tag = matrix.lib1_tag
    lib2_tag = matrix.lib2_tag

    # find barcode
    barcode = matrix.barcode

    available_viability_metrics = ['viability', 'inhibition']

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)

    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_viability_metrics]

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
                                value='viability',
                                searchable=False,
                                clearable=False
                            )
                        )
                    ]),
                    dbc.Col(html.Hr(), width=12)
                ]),
               # dbc.Row([
               #     dbc.Col(width=8, children=[
               #         dcc.Graph(id='viability-heatmap'),
               #         html.Div(className='col-8 offset-2', children=[
               #         ])
               #     ]),
               #     dbc.Col(width=4, children=[
               #         dcc.Graph(id='viability-surface'),
               #     ])
               # ]),
                dbc.Row([
                    dbc.Col(width=2,className='align-top', children=[dcc.Graph(id='lib2-viability-heatmap'), ]),
                    dbc.Col(width=8, children=[
                        dbc.Row(
                            children=[dcc.Graph(id='viability-heatmap')]
                        ),
                        dbc.Row(children=[dcc.Graph(id='lib1-viability-heatmap') ]),
                    ]),

                ]),
                dbc.Row([
                    dbc.Col(width=10, children=[
                          dcc.Graph(id='viability-surface'),
                     ]),
                ]),
              #  dbc.Row([
              #      dbc.Col(width=8, children=[dcc.Graph(id='lib1-viability-heatmap'), ]),
              #  ]),
              #  dbc.Row([
              #      dbc.Col(width=8, children=[dcc.Graph(id='lib2-viability-heatmap'), ])
              #  ])
            ]),
            html.Div(id='viability-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_names', style={'display': 'none'},
                     children=f"{drug1}:_:{drug2}"),
            html.Div(id='barcode', style={'display': 'none'},
                     children=f"{barcode}"),
            html.Div(id='lib1_tag', style={'display': 'none'},
                     children=f"{lib1_tag}"),
            html.Div(id='lib2_tag', style={'display': 'none'},
                     children=f"{lib2_tag}")

        ])
    ])

@app.callback(
    dash.dependencies.Output('viability-heatmap', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children'),
     dash.dependencies.Input('drug_names', 'children')]
)
def update_viability_heatmap(viability_heatmap_zvalue, matrix_json, drug_names):
    matrix_df = pd.read_json(matrix_json, orient='split')
    drug1, drug2 = drug_names.split(':_:')

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
                #y=[1],
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Bluered',
                reversescale=True

            )
        ],
        'layout': go.Layout(title=viability_heatmap_zvalue.capitalize(),
                            xaxis={'type': 'category',
                                   'title': drug1 + " µM"
                                   },
                            yaxis={'type': 'category',
                                   'title': drug2 + " µM"

                                   },
                            margin={'l': 100, 't': 40}
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
                colorscale='Bluered',
                reversescale=True,
                cmax=1,
                cmin=0,
                showscale=False,
            )
        ],
        'layout': go.Layout(
            margin=go.layout.Margin(l=40, r=40, b=40, t=40),
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
    [
     dash.dependencies.Input('barcode', 'children'),
     dash.dependencies.Input('lib1_tag', 'children'),
     dash.dependencies.Input('drug_names', 'children')
    ]
)

def update_lib1_heatmap(barcode,lib1_tag,drug_names):
    lib1_name, lib2_name = drug_names.split(':_:')
    # get the single agent data
    lib1_well_result = session.query(SingleAgentWellResult).filter(SingleAgentWellResult.lib_drug == lib1_tag).filter(
        SingleAgentWellResult.barcode == barcode).all()

    lib1_df = pd.DataFrame([l.to_dict() for l in lib1_well_result ])
    lib1_df = lib1_df.sort_values('conc')
    lib1_df.conc = [np.format_float_scientific(conc, 3) for conc in lib1_df.conc]

    return {
        'data': [
            go.Heatmap(
                x=lib1_df.conc,
                y = [1] * len(lib1_df.conc),
                z=lib1_df.viability,
                zmax=1,
                zmin=0,
                colorscale='Bluered',
                reversescale=True,
                showscale=False
            )
        ],
        'layout': go.Layout(
            xaxis={'type': 'category', 'title': lib1_name +  " µM"},
            yaxis={'type': 'category', 'showticklabels': False},
            width=685, height=150,
            margin={'t':30,}
                )

    }

@app.callback(
    dash.dependencies.Output('lib2-viability-heatmap','figure'),
    [
     dash.dependencies.Input('barcode', 'children'),
     dash.dependencies.Input('lib2_tag', 'children'),
     dash.dependencies.Input('drug_names', 'children')
    ]
)

def update_lib2_heatmap(barcode,lib2_tag,drug_names):
    lib1_name, lib2_name = drug_names.split(':_:')
    # get the single agent data
    lib2_well_result = session.query(SingleAgentWellResult).filter(SingleAgentWellResult.lib_drug == lib2_tag).filter(
        SingleAgentWellResult.barcode == barcode).all()

    lib2_df = pd.DataFrame([ l.to_dict() for l in lib2_well_result ])
    lib2_df = lib2_df.sort_values('conc')
    lib2_df.conc = [np.format_float_scientific(conc, 3) for conc in lib2_df.conc]

    return {
        'data': [
            go.Heatmap(
                y=lib2_df.conc,
                x = [1] * len(lib2_df.conc),
                z=lib2_df.viability,
                zmax=1,
                zmin=0,
                colorscale='Bluered',
                reversescale=True,
                showscale = False
            )
        ],
        'layout': go.Layout(
            xaxis={'type': 'category', 'showticklabels': False},
            yaxis={'type': 'category', 'title': lib2_name + " µM"},
            width=200,
            height = 450,
            margin={'t': 45}
                )

    }
