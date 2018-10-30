import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np

import plotly.graph_objs as go
from app import app


def layout(matrix):
    available_viability_metrics = ['viability', 'inhibition']

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(
    #     # lib1_dose=matrix_df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'),
    #     # lib2_dose=matrix_df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'),
    #     lib1_dose=matrix_df.lib1_conc,
    #     lib2_dose=matrix_df.lib2_conc,
    #     lib1_conc=matrix_df.lib1_conc / 1000000,
    #     lib2_conc=matrix_df.lib2_conc / 1000000,
        inhibition=lambda df: 1 - df.viability)
    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_viability_metrics]

    return html.Div(className='row', children=[
        html.Div(className='col-6', children=[
            html.Div(className='border p-3', children=[
                dcc.Dropdown(
                    id='viability-heatmap-zvalue',
                    options=[{'label': i, 'value': i} for i in available_viability_metrics],
                    value='viability'
                ),
                dcc.Graph(id='viability-heatmap'),
                dcc.Graph(id='viability-surface'),
            ]),
            html.Div(id='viability-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split'))
        ])
    ])


@app.callback(
    dash.dependencies.Output('viability-heatmap', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children')]
)
def update_viability_heatmap(viability_heatmap_zvalue, matrix_json):
    matrix_df = pd.read_json(matrix_json, orient='split')

    matrix_df['lib1_conc'] = matrix_df['lib1_conc'].astype('category')
    matrix_df['lib2_conc'] = matrix_df['lib2_conc'].astype('category')
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
                colorscale='Viridis'
            )
        ],
        'layout': go.Layout(title=viability_heatmap_zvalue,
                            xaxis={'type': 'category',
                                   'title': 'Concentration (uM)'
                                   },
                            yaxis={'type': 'category',
                                   'title': 'Concentration (uM)'
                                   },
                            margin={'l': 100}
                            )
        # 'layout': go.Layout(title=viability_heatmap_zvalue,
        #                     xaxis={'type': '-',
        #                            'title': 'Concentration (uM)',
        #                            'tickmode': 'array',
        #                            'tickvals': matrix_df.lib1_conc.unique(),
        #                            'ticktext': matrix_df.lib1_conc.unique()
        #                            },
        #                     yaxis={'type':'-',
        #                            'title': 'Concentration (uM)',
        #                            'tickmode': 'array',
        #                            'tickvals': matrix_df.lib1_conc.unique(),
        #                            'ticktext': matrix_df.lib1_conc.unique()
        #                            }
        #
        #                     )
    }


@app.callback(
    dash.dependencies.Output('viability-surface', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children')]
)
def update_viability_surface(viability_heatmap_zvalue, matrix_json):
    matrix_df = pd.read_json(matrix_json, orient='split')

    # zvalue = matrix_df[['lib1_conc', 'lib2_conc', viability_heatmap_zvalue]]\
    #     .pivot(index='lib2_conc', columns='lib1_conc',
    #            values=viability_heatmap_zvalue)
    # matrix_df['lib1.conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    # matrix_df['lib2.conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]
    #
    # xaxis_labels = CategoricalDtype(categories=matrix_df['lib1_conc'].sort_values().unique(), ordered=True)
    # yaxis_labels = CategoricalDtype(categories=matrix_df['lib2_conc'].sort_values().unique(), ordered=True)

    zvalues = matrix_df[['lib1_conc', 'lib2_conc', viability_heatmap_zvalue]].copy()
    # zvalues['lib1_conc']=zvalues['lib1_conc'].astype(xaxis_labels)
    # zvalues['lib2_conc']=zvalues['lib2_conc'].astype(yaxis_labels)
    # zvalues=zvalues.assign(lib1_conc=lib1_conc.astype(xaxis_labels))
    # zvalues=zvalues.assign(lib2_conc=lib1_conc.astype(yaxis_labels))

    xaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib1_conc]
    yaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib2_conc]


    zvalues_table = zvalues.pivot(index='lib2_conc', columns='lib1_conc', values=viability_heatmap_zvalue)
    lib1_conc_table = zvalues.pivot(index='lib2_conc', columns='lib1_conc', values='lib1_conc')
    lib2_conc_table = zvalues.pivot(index='lib2_conc', columns='lib1_conc', values='lib2_conc')


    return {
        'data': [
            go.Surface(
                z=zvalues_table.values,
                x=lib1_conc_table.values,
                y=lib2_conc_table.values,
                colorscale='Viridis',
                cmax=1,
                cmin=0,
                showscale=False
            )
        ],
        'layout': go.Layout(
            width=500,
            height=500,
            scene={
                'xaxis': {
                    'type': 'category',
                    'title': 'Drug 1 (uM)',
                    'ticktext': xaxis_labels,
                    'tickvals': zvalues.lib1_conc
                },
                'yaxis': {
                    'type': 'category',
                    'title': 'Drug 2 (uM)',
                    'ticktext': yaxis_labels,
                    'tickvals': zvalues.lib2_conc
                },
                'zaxis': {
                    'title': viability_heatmap_zvalue
                }
            }
        )
    }