import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

from app import app


def layout(matrix):
    available_viability_metrics = ['viability', 'inhibition']

    matrix_df = pd.DataFrame([w.to_dict() for w in matrix.well_results])

    matrix_df = matrix_df.assign(
        lib1_dose=matrix_df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'),
        lib2_dose=matrix_df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'),
        inhibition=lambda df: 1 - df.viability)
    matrix_df = matrix_df[['lib1_dose', 'lib2_dose'] + available_viability_metrics]

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
    zvalue = matrix_df[viability_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=matrix_df.lib1_dose,
                y=matrix_df.lib2_dose,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Viridis'
            )
        ],
        'layout': go.Layout(title=viability_heatmap_zvalue)
    }


@app.callback(
    dash.dependencies.Output('viability-surface', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value'),
     dash.dependencies.Input('viability-values', 'children')]
)
def update_viability_surface(viability_heatmap_zvalue, matrix_json):
    matrix_df = pd.read_json(matrix_json, orient='split')
    zvalue = matrix_df[['lib1_dose', 'lib2_dose', viability_heatmap_zvalue]]\
        .pivot(index='lib2_dose', columns='lib1_dose',
               values=viability_heatmap_zvalue)

    return {
        'data': [
            go.Surface(
                z=zvalue.values,
                colorscale='Viridis',
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