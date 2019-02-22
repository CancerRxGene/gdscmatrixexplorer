import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go

from components.synergy_info.syn_info import infoblock_matrix

from app import app
from utils import get_metric_axis_range, well_metrics, synergy_colorscale

def layout(matrix):

    drug1 = matrix.combination.lib1.drug_name
    drug2 = matrix.combination.lib2.drug_name

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)
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
                                value='Bliss_excess',
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
    zmin, zmax = get_metric_axis_range(combo_heatmap_zvalue)

    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_conc,
                y=matrix_df.lib2_conc,
                z=zvalue,
                zmax=zmax,
                zmin=zmin,
                colorscale=synergy_colorscale,
                reversescale=False
            )
        ],
        'layout': go.Layout(title=well_metrics[combo_heatmap_zvalue]['label'],
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
    zmin, zmax = get_metric_axis_range(combo_heatmap_zvalue)

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
                    'range': (zmin, zmax),
                    'title': combo_heatmap_zvalue,
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
