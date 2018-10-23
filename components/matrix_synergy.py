import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

from app import app


def layout(matrix):
    available_combo_metrics = ['HSA_excess', 'Bliss_excess']

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(
        lib1_dose=matrix_df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'),
        lib2_dose=matrix_df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'),
        inhibition=lambda df: 1 - df.viability)
    matrix_df = matrix_df[['lib1_dose', 'lib2_dose'] + available_combo_metrics]

    return html.Div(className='row', children=[
        html.Div(className='col-6', children=[
            html.Div(className='border p-3', children=[

                dcc.Dropdown(
                    id='combo-heatmap-zvalue',
                    options=[{'label': i, 'value': i} for i in available_combo_metrics],
                    value='HSA_excess'
                ),
                dcc.Graph(id='combo-heatmap'),
                dcc.Graph(id='combo-surface'),
            ])
        ]),
        html.Div(id='combo-values', style={'display': 'none'},
                 children=matrix_df.to_json(date_format='iso',
                                            orient='split'))
    ])


@app.callback(
    dash.dependencies.Output('combo-heatmap', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value'),
     dash.dependencies.Input('combo-values', 'children')]
)
def update_combo_heatmap(combo_heatmap_zvalue, combo_json):
    matrix_df = pd.read_json(combo_json, orient='split')
    zvalue = matrix_df[combo_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_dose,
                y=matrix_df.lib2_dose,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Reds'
            )
        ],
        'layout': go.Layout(title=combo_heatmap_zvalue)
    }


@app.callback(
    dash.dependencies.Output('combo-surface', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value'),
     dash.dependencies.Input('combo-values', 'children')]
)
def update_combo_surface(combo_heatmap_zvalue, combo_json):
    matrix_df = pd.read_json(combo_json, orient='split')
    zvalue = matrix_df[['lib1_dose', 'lib2_dose', combo_heatmap_zvalue]]\
        .pivot(index='lib2_dose', columns='lib1_dose', values=combo_heatmap_zvalue)

    return {
        'data': [
            go.Surface(
                z=zvalue.values,
                colorscale='Reds',
                cmax=1,
                cmin=0,
                showscale=False
            )
        ],
        'layout': go.Layout(
            width=500,
            height=500
        )
    }