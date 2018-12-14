import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from components.synergy_info.syn_info import infoblock_matrix

from app import app


def layout(matrix):
    available_combo_metrics = ["HSA_excess", "Bliss_excess", "HSA",
                               "Bliss_additivity", "Bliss_index", "Loewe_index"]

    drug1 = matrix.drugs[matrix.combination.lib1_tag].drug_name
    drug2 = matrix.drugs[matrix.combination.lib2_tag].drug_name

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)
    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_combo_metrics]

    return html.Div(className='row', children=[
        html.Div(className='col-12', children=[
            html.Div(className='border p-3 bg-white', children=[
                html.Div(className='row pb-3', children=[
                    html.Div(className='col-12 d-flex flex-row', children=[
                        html.Div(className='col-auto', children=[
                            html.H3(["Drug combination interaction"], className='pt-1'),
                        ]),
                        html.Div(className='col-3', children=[
                            dcc.Dropdown(
                                id='combo-heatmap-zvalue',
                                options=[{'label': i, 'value': i} for i in
                                         available_combo_metrics],
                                value='HSA_excess',
                                searchable=False,
                                clearable=False
                            )
                        ]),
                    ]),
                    html.Div(html.Hr(), className='col-12'),
                ]),
                html.Div(className='row', children=[
                    html.Div(className='col-7', children=[
                        html.Div(className='row ', children=[
                            html.Div(className='col-12', children=[
                                dcc.Graph(id='combo-heatmap')
                            ])
                        ]),
                        html.Div(className='row', children=[
                            html.Div(className='col-12', children=[
                                dcc.Graph(id='combo-surface')
                            ])
                        ])
                    ]),
                    html.Div(className="col-4 offset-1", children=[
                        html.Div(
                            children=[
                                infoblock_matrix(matrix)
                            ]
                        ),
                    ])
                ])
            ]),
            html.Div(id='combo-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_names', style={'display': 'none'},
                     children=f"{drug1}:_:{drug2}")
        ])
    ])



@app.callback(
    dash.dependencies.Output('combo-heatmap', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value'),
     dash.dependencies.Input('combo-values', 'children'),
     dash.dependencies.Input('drug_names', 'children')]
)
def update_combo_heatmap(combo_heatmap_zvalue, combo_json, drug_names):
    matrix_df = pd.read_json(combo_json, orient='split')
    drug1, drug2 = drug_names.split(':_:')

    # sort the data frame before the conc convert to scientific notation
    matrix_df = matrix_df.sort_values(['lib1_conc', 'lib2_conc'])

    matrix_df['lib1_conc'] = matrix_df['lib1_conc'].astype('category')
    matrix_df['lib2_conc'] = matrix_df['lib2_conc'].astype('category')
    matrix_df['lib1_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib1_conc']]
    matrix_df['lib2_conc'] = [np.format_float_scientific(conc, 3) for conc in matrix_df['lib2_conc']]

    zvalue = matrix_df[combo_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_conc,
                y=matrix_df.lib2_conc,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Reds',
                reversescale=True
            )
        ],
        'layout': go.Layout(title=combo_heatmap_zvalue,
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
    dash.dependencies.Output('combo-surface', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value'),
     dash.dependencies.Input('combo-values', 'children'),
     dash.dependencies.Input('drug_names', 'children')]
)
def update_combo_surface(combo_heatmap_zvalue, combo_json, drug_names):
    matrix_df = pd.read_json(combo_json, orient='split')

    drug1, drug2 = drug_names.split(':_:')

    xaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib1_conc]
    yaxis_labels = [f"{conc:.2e}" for conc in matrix_df.lib2_conc]

    # change lib2_conc ascending to 1
    zvalues_table = matrix_df.pivot(index='lib2_conc', columns='lib1_conc', values=combo_heatmap_zvalue)
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
                colorscale='Reds',
                reversescale=True,
                cmax=1,
                cmin=0,
                showscale=False
            )
        ],
        'layout': go.Layout(
            # width=500,
            # height=500,
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
                    'range': (-0.2, 0.3),
                    'title': combo_heatmap_zvalue,
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
