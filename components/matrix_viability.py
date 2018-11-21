import dash
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

    dose_conc_cols = matrix_df[['lib1_conc', 'lib1_dose']].drop_duplicates()
    dose_conc_cols = dose_conc_cols.assign(position=[dose[1:] for dose in dose_conc_cols['lib1_dose']])
    dose_conc_cols = dose_conc_cols.assign(orient='column')
    dose_conc_cols = dose_conc_cols.rename(index=str, columns={"lib1_conc": "conc"})
    dose_conc_cols = dose_conc_cols[['position', 'orient', 'conc']]

    dose_conc_rows = matrix_df[['lib2_conc', 'lib2_dose']].drop_duplicates()
    dose_conc_rows = dose_conc_rows.assign(position=[dose[1:] for dose in dose_conc_rows['lib2_dose']])
    dose_conc_rows = dose_conc_rows.assign(orient='row')
    dose_conc_rows = dose_conc_rows.rename(index=str, columns={"lib2_conc": "conc"})
    dose_conc_rows = dose_conc_rows[['position', 'orient', 'conc']]

    dose_conc_map = pd.concat([dose_conc_cols, dose_conc_rows])

    sliced_plot_ids = pd.DataFrame([
        {'id': c.id,
         'orient': 'column' if c.fixed_tag == matrix.combination.lib1_tag else 'row',
         'position': c.fixed_dose[1:],
         'fixed_drug_name': matrix.drugs[c.fixed_tag].drug_name,
         'dosed_drug_name': matrix.drugs[c.dosed_tag].drug_name
         }
        for c in matrix.combination_curves])

    sliced_plot_ids = pd.merge(sliced_plot_ids, dose_conc_map, on=['position', 'orient'])

    available_viability_metrics = ['viability', 'inhibition']

    drug1 = matrix.combination.lib1.drug_name
    drug2 = matrix.combination.lib2.drug_name

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)

    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_viability_metrics]

    return html.Div(className='row pb-5', children=[
        html.Div(className='col-12', children=[
            html.Div(className='border bg-white p-2', children=[
                html.Div(className='row pb-3', children=[
                    html.Div(className='col-3', children=[
                        dcc.Dropdown(
                            id='viability-heatmap-zvalue',
                            options=[{'label': i, 'value': i} for i in available_viability_metrics],
                            value='viability',
                            searchable=False,
                            clearable=False
                        )
                    ]),
                    html.Div(className='col-9 text-right', children=[
                        html.H2(["Measured activity"])
                    ])
                ]),
                html.Div(className='row', children=[
                    html.Div(className='col-6', children=[
                        dcc.Graph(id='viability-heatmap')
                    ]),
                    html.Div(className='col-6 flex-column d-flex align-self-center', children=[
                        html.Div(id='dr_row')
                    ])
                ]),
                html.Div(className='row pb-5', children=[
                    html.Div(className='col-6', children=[
                        dcc.Graph(id='viability-surface')
                    ]),
                    html.Div(className='col-6', children=[
                        html.Div(id='dr_column')
                    ])
                ])
            ]),

            # html.Div(className='col-4 d-flex flex-column h-100', children=[
            #     html.Div(id='dr_row', className='h-50'),
            #     html.Div(id='dr_column', className='h-50')
            # ]),
            html.Div(id='curve-ids', style={'display': 'none'},
                     children=sliced_plot_ids.to_json(date_format='iso',
                                                      orient='split')),
            html.Div(id='viability-values', style={'display': 'none'},
                     children=matrix_df.to_json(date_format='iso', orient='split')),
            html.Div(id='drug_names', style={'display': 'none'},
                     children=f"{drug1}:_:{drug2}")

        ])
    ])


@app.callback(
    dash.dependencies.Output('dr_row', 'children'),
    [dash.dependencies.Input('viability-heatmap', 'hoverData'),
     dash.dependencies.Input('curve-ids', 'children')])
def display_combo_row(hoverdata, curve_ids):
    curve_ids = pd.read_json(curve_ids, orient='split')
    if not hoverdata:
        return "Hover over the heatmap to view row-wise and column-wise plots"
    row = hoverdata['points'][0]['y']
    curve_row = next(curve_ids.query('orient == "row" and conc == @row').itertuples())
    curve = session.query(DoseResponseCurve).get(int(curve_row.id))
    newline = '\n'
    return html.Div(className="mb-2 mt-2", children=[
        html.H6(
            [html.Em("Row"),
             html.Strong(f" {curve_row.dosed_drug_name} titrated"),
             html.Br(),
             html.Strong(f"with {curve_row.fixed_drug_name} @ {row} µM")
             ]),
        curve.plot(display_datapoints=True, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   # style={'height': '350px'}
    )
    ])


@app.callback(
    dash.dependencies.Output('dr_column', 'children'),
    [dash.dependencies.Input('viability-heatmap', 'hoverData'),
     dash.dependencies.Input('curve-ids', 'children')])
def display_combo_column(hoverdata, curve_ids):
    curve_ids = pd.read_json(curve_ids, orient='split')
    if not hoverdata:
        return ""
    print(hoverdata)
    column = hoverdata['points'][0]['x']
    curve_col = next(
        curve_ids.query('orient == "column" and conc == @column').itertuples())
    curve = session.query(DoseResponseCurve).get(int(curve_col.id))
    return html.Div(className="mb-2 mt-2", children=[
        html.H6(
            [html.Em("Column"),
             html.Strong(f" {curve_col.dosed_drug_name} titrated"),
             html.Br(),
             html.Strong(f"with {curve_col.fixed_drug_name} @ {column} µM")
             ]),

        curve.plot(display_datapoints=True, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   # style={'height': '350px'}
                   )
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
                    'range': (0, 1),
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
