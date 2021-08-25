from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd

from app import app
from db import session
from models import MatrixResult, Combination
from utils import matrix_hover_label, add_label_vars


@lru_cache()
def get_combination_max_effects(project_id, lib1_id, lib2_id):
    combination = session.query(Combination)\
        .filter(Combination.project_id == project_id,
                Combination.lib1_id == lib1_id,
                Combination.lib2_id == lib2_id)\
        .one()

    max_effects_query = combination.matrices \
        .with_entities(
        MatrixResult.barcode,
        MatrixResult.cmatrix,
        MatrixResult.combo_maxe,
        MatrixResult.lib1_maxe,
        MatrixResult.lib2_maxe,
        MatrixResult.delta_maxe_lib1,
        MatrixResult.delta_maxe_lib2,
        MatrixResult.bliss_matrix,
        MatrixResult.lib1_id,
        MatrixResult.lib2_id,
        MatrixResult.model_id
    )

    df_max_effects = pd.read_sql(max_effects_query.statement, session.get_bind())

    df_max_effects = add_label_vars(df_max_effects)
    labels = matrix_hover_label(df_max_effects)
    customdata = [{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                  for row in df_max_effects.itertuples(index=False)]

    return df_max_effects, labels, customdata


def layout(combination):

    df_max_effects, labels, customdata = \
        get_combination_max_effects(combination.project_id,
                                    combination.lib1_id,
                                    combination.lib2_id)

    def generate_box(name, y, text, customdata):
        return go.Box(
            name=name, y=y, text=text, customdata=customdata,
            boxpoints='all',
            jitter=0.3,
            marker=dict(
                size=4,
                opacity=0.5
            ),
            hoveron='points',
            hoverinfo='y+text'
        )

    def generate_standard_box(name, y):
        return generate_box(name, y, text=labels, customdata=customdata)

    return html.Div(
        children=[
            dcc.Location(id='combo-max-effect-url'),
            dbc.Row(
                dbc.Col(width=12, children=[
                    html.Div(className="bg-white pt-3 px-4 pb-3 mb-3 border shadow-sm", children=[
                        html.H3("MaxE - Monotherapies vs Combination"),
                        html.Hr(),
                        dbc.Row(className="pb-4", children=[
                            dbc.Col(width=5, children=
                                dcc.Loading(className='gdsc-spinner', children=
                                    dcc.Graph(
                                        id='combo-max-effect-boxplot',
                                        figure=go.Figure(
                                            data=[
                                                generate_standard_box(
                                                    name=f"{combination.lib1.name}",
                                                    y=df_max_effects.lib1_maxe
                                                ),
                                                generate_standard_box(
                                                    name=f"{combination.lib2.name}",
                                                    y=df_max_effects.lib2_maxe
                                                ),
                                                generate_standard_box(
                                                    name=f"{combination.lib1.name} + {combination.lib2.name}",
                                                    y=df_max_effects.combo_maxe
                                                )
                                            ],
                                            layout=go.Layout(
                                                showlegend=False,
                                                yaxis={
                                                    'title': "MaxE",
                                                    'range': (0, 1)
                                                },
                                                title="MaxE monotherapies vs combination",
                                            ),
                                        ),
                                        config={"displayModeBar": False}
                                    )
                                )
                            ),
                            dbc.Col(width=4, children=
                                dcc.Loading(className='gdsc-spinner', children=
                                    dcc.Graph(
                                        id='combo-delta-max-effect-boxplot',
                                        figure=go.Figure(
                                            data=[
                                                generate_standard_box(
                                                    name=f"Δ {combination.lib1.name}",
                                                    y=df_max_effects.delta_maxe_lib1
                                                ),
                                                generate_standard_box(
                                                    name=f"Δ {combination.lib2.name}",
                                                    y=df_max_effects.delta_maxe_lib2
                                                )
                                            ],
                                            layout=go.Layout(
                                                showlegend=False,
                                                yaxis={
                                                    'title': "Combination - Monotherapy",
                                                    'range': (-1, 1)
                                                },
                                                title="Delta MaxE"
                                            )
                                        ),
                                        config={"displayModeBar": False}
                                    )
                                    )
                                ),
                            dbc.Col(width=3, children=
                                dcc.Loading(className='gdsc-spinner', children=
                                    dcc.Graph(
                                        id='combo-bliss-boxplot',
                                        figure=go.Figure(
                                            data=[
                                                generate_standard_box(
                                                    name="Bliss excess",
                                                    y=df_max_effects.bliss_matrix
                                                )
                                            ],
                                            layout=go.Layout(
                                                showlegend=False,
                                                yaxis={
                                                    'title': "Bliss Excess",
                                                    'range': (-1, 1)
                                                },
                                                title="Bliss Excess"
                                            )
                                        ),
                                        config={"displayModeBar": False}
                                    )
                                )
                            )
                        ])
                    ])
                ])
            )
        ]
    )


@app.callback(
    dash.dependencies.Output('combo-max-effect-url', 'pathname'),
    [dash.dependencies.Input('combo-max-effect-boxplot', 'clickData'),
     dash.dependencies.Input('combo-delta-max-effect-boxplot', 'clickData'),
     dash.dependencies.Input('combo-delta-max-effect-boxplot', 'clickData')])
def go_to_dot(p1, p2, p3):
    p = p1 or p2 or p3
    if p:
        return p['points'][0]['customdata']['to']
    # else:
    #     return "/"
