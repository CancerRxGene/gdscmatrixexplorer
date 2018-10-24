import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, DoseResponseCurve


def layout(matrix: MatrixResult):
    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(
        lib1_dose=matrix_df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'),
        lib2_dose=matrix_df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'))

    zvalue = matrix_df[['lib1_dose', 'lib2_dose', 'viability']] \
        .pivot(index='lib2_dose', columns='lib1_dose',
               values='viability')

    sliced_plot_ids = pd.DataFrame([
        {'id': c.id,
         'orient': 'row' if c.fixed_tag == matrix.drug_matrix.lib1_tag else 'column',
         'position': c.fixed_dose[1:],
         'fixed_drug_name': matrix.drugs[c.fixed_tag].drug_name,
         'dosed_drug_name': matrix.drugs[c.dosed_tag].drug_name}
        for c in matrix.combination_curves])

    return html.Div(className='row pb-5', children=[
        html.Div(className='col-12', children=[
            html.Div(className='border bg-white d-flex flex-row p-2', children=[

                html.Div(className='col-4 d-flex flex-column', children=[
                    html.Div(className="p-2",
                             children=[
                                 html.H2("Viability"),
                                 html.P("Maybe an interesting stat here"),
                             ]),
                    dcc.Graph(id='viability-surface',
                              style={"height": "350px", "width": "100%"},
                              figure={
                                  'data': [
                                      go.Surface(
                                          z=zvalue.values,
                                          colorscale='Viridis',
                                          cmax=1,
                                          cmin=0,
                                          showscale=False,
                                      )
                                  ],
                                  'layout': go.Layout(
                                      margin=dict(l=0, r=0, b=30, t=0),
                                      scene=dict(
                                          aspectratio=dict(x=1, y=1, z=0.5),
                                          camera=dict(
                                              eye=dict(x=-1.0, y=1.0, z=0.5))
                                      ),
                                  )
                              }
                              )
                ]),
                html.Div(className='col-5', children=[
                    dcc.Graph(id='viability-heatmap',
                              figure={
                                  'data': [
                                      go.Heatmap(
                                          x=matrix_df.lib1_dose,
                                          y=matrix_df.lib2_dose,
                                          z=matrix_df.viability,
                                          zmax=1,
                                          zmin=0,
                                          colorscale='Viridis',
                                          colorbar={'x': -.2}
                                      )
                                  ],
                                  'layout': go.Layout(
                                      # title='Viability',
                                      xaxis=dict(autorange='reversed',range=[1, 7]),
                                      yaxis=dict(autorange='reversed',range=[1, 7]),
                              )
                              })
                ]),
                html.Div(className='col-3 d-flex flex-column h-100', children=[
                    html.Div(id='dr_row', className='h-50'),
                    html.Div(id='dr_column', className='h-50')
                ]),
                html.Div(id='curve-ids', style={'display': 'none'},
                         children=sliced_plot_ids.to_json(date_format='iso',
                                                    orient='split'))

            ])
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
    curve_row = next(curve_ids.query('orient == "row" and position == @row').itertuples())
    curve = session.query(DoseResponseCurve).get(int(curve_row.id))
    return html.Div(className="mb-2 mt-2", children=[
        html.H6([html.Em("Row"), html.Strong(f" {curve_row.fixed_drug_name} @ Dose {row} vs {curve_row.dosed_drug_name}")]),
        curve.plot(display_datapoints=False, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   style={'height': '200px'})
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
    curve_row = next(
        curve_ids.query('orient == "column" and position == @column').itertuples())
    curve = session.query(DoseResponseCurve).get(int(curve_row.id))
    return html.Div([
        html.H6([html.Em("Column"), html.Strong(
            f" {curve_row.fixed_drug_name} @ Dose {column} vs {curve_row.dosed_drug_name}")]),
        curve.plot(display_datapoints=False, mark_auc=True,
                   label_auc=False, mark_ic50=True, label_ic50=True,
                   mark_emax=False, label_emax=False, label_rmse=True,
                   style={'height': '200px'})
    ])