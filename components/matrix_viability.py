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

    drug1 = matrix.combination.lib1.drug_name
    drug2 = matrix.combination.lib2.drug_name

    sliced_plot_ids = pd.DataFrame([
        {'id': c.id,
         'orient': 'column' if c.fixed_tag == matrix.lib1_tag else 'row',
         'position': c.fixed_dose[1:],
         'fixed_drug_name': drug1 if matrix.lib1_tag == c.fixed_tag else drug2,
         'dosed_drug_name': drug2 if matrix.lib1_tag == c.dosed_tag else drug1
         }
        for c in matrix.combination_curves])

    sliced_plot_ids = pd.merge(sliced_plot_ids, dose_conc_map, on=['position', 'orient'])

    available_viability_metrics = ['viability', 'inhibition']

    matrix_df = matrix_df.assign(inhibition=lambda df: 1 - df.viability)

    matrix_df = matrix_df[['lib1_conc', 'lib2_conc'] + available_viability_metrics]

    return html.Div(className='row pb-5', children=[
        html.Div(className='col-12', children=[
            html.Div(className='border bg-white p-4', children=[
                html.Div(className='row', children=[
                    html.Div(className='col-12 d-flex flex-row', children=[
                        html.Div(className='col-auto', children=[
                            html.H3(["Measured activity"], className='pt-1'),
                        ]),
                        html.Div(className='col-3', children=[
                            dcc.Dropdown(
                                id='viability-heatmap-zvalue',
                                options=[{'label': i, 'value': i} for i in
                                         available_viability_metrics],
                                value='viability',
                                searchable=False,
                                clearable=False
                            ),
                        ]),
                    ]),
                    html.Div(html.Hr(), className='col-12')
                ]),
                html.Div(className='row', children=[
                    html.Div(className='col-8', children=[
                        dcc.Graph(id='viability-heatmap'),
                        html.Div(className='col-8 offset-2', children=[
                        ])
                    ]),
                    html.Div(className='col-4', children=[
                        dcc.Graph(id='viability-surface'),
                    ]),
                ]),
                html.Div(className='row', children=[
                    html.Div(className='col-4 offset-1', children=[
                        html.Div(id='dr_row'),
                    ]),
                    html.Div(className='col-4', children=[
                        html.Div(id='dr_column')
                    ])
                ])
            ]),
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
    return html.Div(className="mb-2 mt-2", children=[
        html.H5("Row"),
        html.P(
            [
                html.Span("Fixed: "),
                html.Strong(f"{curve_row.fixed_drug_name} @ {row} µM"),
                html.Br(),
                html.Span("Titrated: "),
                html.Strong(f"{curve_row.dosed_drug_name}"),
            ]),
        curve.plot(display_datapoints=True, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   style={'height': '250px'}
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
    column = hoverdata['points'][0]['x']
    curve_col = next(
        curve_ids.query('orient == "column" and conc == @column').itertuples())
    curve = session.query(DoseResponseCurve).get(int(curve_col.id))
    return html.Div(className="mb-2 mt-2", children=[
        html.H5("Column"),
        html.P(
            [
             html.Span("Fixed: "), html.Strong(f"{curve_col.fixed_drug_name} @ {column} µM"),
             html.Br(),
             html.Span("Titrated: "), html.Strong(f"{curve_col.dosed_drug_name}"),
             ]),

        curve.plot(display_datapoints=True, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   style={'height': '250px'}
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
                showscale=False
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
