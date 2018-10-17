import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlalchemy as sa
from db import engine
import pandas as pd
import plotly.graph_objs as go

from db import session
from app import app
from models import MatrixResult, Drug, DrugMatrix, Model, WellResult

session = sa.orm.sessionmaker(bind=engine)()

my_model = session.query(Model).filter_by(name='SW620').one()
mydrug1 = session.query(Drug).filter(Drug.drug_name.startswith('LY260')).one()
mydrug2 = session.query(Drug).filter_by(drug_name='Irinotecan').one()

my_cmatrix = session.query(DrugMatrix).filter_by(lib1_id=mydrug1.id, lib2_id=mydrug2.id).one()

my_matrices = session.query(MatrixResult).filter_by(
    model_id=my_model.id,
    cmatrix=my_cmatrix.cmatrix,
    drugset_id=my_cmatrix.drugset_id
)

# my_matrix = next(x for x in my_matrices if x.barcode == 39354)
my_matrix = my_matrices.first()

df = pd.DataFrame([w.to_dict() for w in my_matrix.well_results])

df = df.assign(lib1_dose=df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'))
df = df.assign(lib2_dose=df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'))
df = df.assign(inhibition=lambda df: 1 - df.viability)

viability_surface = df[['lib1_dose', 'lib2_dose', 'viability']].pivot(index='lib2_dose', columns='lib1_dose',
                                                                      values='viability')

inhib_surface = df[['lib1_dose', 'lib2_dose', 'inhibition']].pivot(index='lib2_dose', columns='lib1_dose',
                                                                              values='inhibition')
HSA_surface = df[['lib1_dose', 'lib2_dose', 'HSA']].pivot(index='lib2_dose', columns='lib1_dose', values='HSA')

available_viability_metrics = ['viability', 'inhibition']

available_combo_metrics = ['HSA_excess', 'Bliss_excess']

layout = html.Div(children=[
    html.H2(children=f'Cell line name: {my_model.name}'),
    html.H2(children=f'Drugs: {mydrug1.drug_name} + {mydrug2.drug_name}'),
    html.H2(children=f'Barcode:{my_matrix.barcode}'),


    html.Div(className='row', children=[
        html.Div(className='col-6', children=[
            html.Div(className='border p-3', children=[
                dcc.Dropdown(
                    id='viability-heatmap-zvalue',
                    options=[{'label': i, 'value': i} for i in available_viability_metrics],
                    value='viability'
                ),
                dcc.Graph(
                    id='viability-heatmap'
                ),
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Surface(
                                z=viability_surface.values
                            )
                        ],
                        layout=go.Layout(title='Viability surface')
                    ),
                    id='viability-surface'
                ),
            ]),
        ]),
        html.Div(className='col-6', children=[
            html.Div(className='border p-3', children=[

                dcc.Dropdown(
                    id='combo-heatmap-zvalue',
                    options=[{'label': i, 'value': i} for i in available_combo_metrics],
                    value='HSA_excess'
                ),
                dcc.Graph(
                    id='combo-heatmap'
                ),
                dcc.Graph(
                    id='combo-surface'
                ),
            ])
        ])
    ]),

    html.Div(className='row', children=[
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Surface(
                        z=inhib_surface.values, opacity=0.7, colorscale='Blues'
                    ),
                    go.Surface(
                        z=HSA_surface.values, showscale=False, opacity=0.7, colorscale='Reds'
                    ),
                ],
                layout=go.Layout(title='Comparison to null model')
            ),
            id='surface-comparison'
        )
    ])
])


@app.callback(
    dash.dependencies.Output('viability-heatmap', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value')]
)
def update_viability_heatmap(viability_heatmap_zvalue):
    zvalue = df[viability_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=df.lib1_dose,
                y=df.lib2_dose,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Viridis'
            )
        ],
        'layout' : go.Layout(title=viability_heatmap_zvalue)
    }

@app.callback(
    dash.dependencies.Output('viability-surface', 'figure'),
    [dash.dependencies.Input('viability-heatmap-zvalue', 'value')]
)
def update_viability_surface(viability_heatmap_zvalue):
    zvalue = df[['lib1_dose', 'lib2_dose', viability_heatmap_zvalue]].pivot(index='lib2_dose',
                                                                                      columns='lib1_dose',
                                                                                      values=viability_heatmap_zvalue)

    return {
        'data': [
            go.Surface(
                z=zvalue.values,
                colorscale = 'Viridis',
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

@app.callback(
    dash.dependencies.Output('combo-heatmap', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value')]
)
def update_combo_heatmap(combo_heatmap_zvalue):
    zvalue = df[combo_heatmap_zvalue]

    return {
        'data': [
            go.Heatmap(
                x=df.lib1_dose,
                y=df.lib2_dose,
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
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value')]
)
def update_combo_surface(combo_heatmap_zvalue):
    zvalue = df[['lib1_dose', 'lib2_dose', combo_heatmap_zvalue]].pivot(index='lib2_dose',
                                                                                      columns='lib1_dose',
                                                                                      values=combo_heatmap_zvalue)

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


if __name__ == '__main__':
    app.run_server(debug=True)
