import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, DoseResponseCurve


def layout(matrix: MatrixResult):
    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df['lib1_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    matrix_df['lib2_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]

    drug1 = matrix.combination.lib1.drug_name
    drug2 = matrix.combination.lib2.drug_name

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
                dbc.Row([
                    dbc.Col(width=8, children=[
                        dcc.Graph(id='viability-heatmap'),
                        html.Div(className='col-8 offset-2', children=[
                        ])
                    ]),
                    dbc.Col(width=4, children=[
                        dcc.Graph(id='viability-surface'),
                    ])
                ])
            ]),
            html.Div(id='viability-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_names', style={'display': 'none'},
                     children=f"{drug1}:_:{drug2}")

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
    #print (zvalue)
    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_conc,
                y=matrix_df.lib2_conc,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Bluered',
                #reversescale=True

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
                #reversescale=True,
                cmax=1,
                cmin=0,
                #showscale=False,
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
