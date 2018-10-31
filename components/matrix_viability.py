import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np

import plotly.graph_objs as go
from app import app


def layout(matrix):
    available_viability_metrics = ['viability', 'inhibition']

    drug1 = matrix.drugs[matrix.drug_matrix.lib1_tag].drug_name
    drug2 = matrix.drugs[matrix.drug_matrix.lib2_tag].drug_name

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)
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
                                   'title': drug1 + " µM"
                                   },
                            yaxis={'type': 'category',
                                   'title': drug2 + " µM"

                                   },
                            margin={'l': 100}
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

    xaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib1_conc]
    yaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib2_conc]

    zvalues_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values=viability_heatmap_zvalue)
    zvalues_table = zvalues_table.sort_values(by=['lib2_conc'], ascending=0)
    lib1_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib1_conc')
    lib1_conc_table = lib1_conc_table.sort_values(by=['lib2_conc'], ascending=0)
    lib2_conc_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values='lib2_conc')
    lib2_conc_table = lib2_conc_table.sort_values(by=['lib2_conc'], ascending=0)


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
                    'title': drug1 + ' µM',
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
                    'title': drug2 + ' µM',
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
                    'range': (0,1),
                    'title': viability_heatmap_zvalue,
                    'titlefont': {
                        'size': 12
                    },
                    'tickfont': {
                        'size': 10
                    }
                }
            }
        )
    }