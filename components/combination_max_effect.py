import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd

from db import session
from models import MatrixResult, Model


def layout(combination):

    max_effects_query = combination.matrices\
        .join(Model)\
        .with_entities(MatrixResult.combo_max_effect,
                       MatrixResult.lib1_max_effect,
                       MatrixResult.lib2_max_effect,
                       MatrixResult.lib1_delta_max_effect,
                       MatrixResult.lib2_delta_max_effect,
                       MatrixResult.Bliss_excess,
                       Model.name.label('Cell Line'))

    df_max_effects = pd.read_sql(max_effects_query.statement, session.get_bind())

    print(df_max_effects.shape)
    print(df_max_effects.head())

    return html.Div(
        children=[
            html.Div(className="row", children=[
                html.Div(className="col-12", children=[
                    html.Div(className="bg-white pt-3 px-4 pb-3 mb-3 border border-warning ", children=[
                        html.H3("Combination Max Effect vs Monotherapies"),
                        html.Hr(),
                        html.Div(className="row pb-4", children=[
                            html.Div(className="col-5", children=[
                                dcc.Graph(
                                    id='combo-max-effect-boxplot',
                                    figure=go.Figure(
                                        data=[
                                            go.Box(
                                                name=f"{combination.lib1.drug_name} monotherapy",
                                                y=df_max_effects.lib1_max_effect,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                text=[f"Cell Line: {x}" for x in df_max_effects['Cell Line']],
                                                hoveron='points'
                                            ),
                                            go.Box(
                                                name=f"{combination.lib2.drug_name} monotherapy",
                                                y=df_max_effects.lib2_max_effect,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                hoveron='points'
                                            ),
                                            go.Box(
                                                name=f"{combination.lib1.drug_name} + {combination.lib2.drug_name}",
                                                y=df_max_effects.combo_max_effect,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                hoveron='points'
                                            )
                                        ],
                                        layout=go.Layout(
                                            showlegend=False,
                                            yaxis={
                                                'title': "Max Effect",
                                                'range': (0, 1)
                                            },
                                            title="Max effect monotherapies vs combination",
                                        ),
                                    ),
                                    config={"displayModeBar": False}
                                )
                            ]),
                            html.Div(className="col-4", children=[
                                dcc.Graph(
                                    id='combo-delta-max-effect-boxplot',
                                    figure=go.Figure(
                                        data=[
                                            go.Box(
                                                name=f"Δ {combination.lib1.drug_name}",
                                                y=df_max_effects.lib1_delta_max_effect,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                hoveron='points'
                                            ),
                                            go.Box(
                                                name=f"Δ {combination.lib2.drug_name}",
                                                y=df_max_effects.lib2_delta_max_effect,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                hoveron='points'
                                            )
                                        ],
                                        layout=go.Layout(
                                            showlegend=False,
                                            yaxis={
                                                'title': "Combination - Monotherapy",
                                                'range': (-1, 1)
                                            },
                                            title="Delta Max Effect"
                                        )
                                    ),
                                    config={"displayModeBar": False}
                                )
                            ]),
                            html.Div(className="col-3", children=[
                                dcc.Graph(
                                    id='combo-bliss-boxplot',
                                    figure=go.Figure(
                                        data=[
                                            go.Box(
                                                name=f"Bliss excess",
                                                y=df_max_effects.Bliss_excess,
                                                boxpoints='all',
                                                jitter=0.3,
                                                marker=dict(
                                                    size=4,
                                                    opacity=0.5
                                                ),
                                                hoveron='points'
                                            ),
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
                            ]),
                        ])
                    ])
                ])
            ])
        ]
    )
