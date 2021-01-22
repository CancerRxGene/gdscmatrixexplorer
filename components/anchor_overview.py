from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

from app import app
from db import session
from models import AnchorCombi

def layout(combination):
    return html.Div(children=[
        dbc.Row(
            dbc.Col(width=12, children=[
                html.Div(
                    html.H3("Detailed overview of drug responses"),
                    html.Hr(),
            )]
        )),
         dbc.Row(
            dbc.Col(width=5,children=[
                dcc.Loading(className='gdsc-spinner', children=
                    dcc.Graph(
                        id='scatter1',
                        figure= generate_boxplot(combination)
                    )
                )
            ]),

            dbc.Col(width=6, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                        id='scatter2',
                        figure=generate_boxplot(combination)
                    )
                )
            ]),

            dbc.Col(width=2, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(

                ))
            ]),

            dbc.Col(width=6, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='scatter4',
                    # figure=generate_figure()
                ))
            ])
        ),
    ])

def generate_boxplot(combination):
    project_id = combination.project_id
    lib_id = combination.lib1_id
    anchor_id = combination.lib2_id

    anchor_combi_query = session.query(AnchorCombi).\
        filter(AnchorCombi.project_id == project_id).\
        filter(AnchorCombi.library_id ==  lib_id).\
        filter(AnchorCombi.anchor_id == anchor_id)

    anc_df = pd.read_sql(anchor_combi_query.statement, session.bind)

    anc_via = anc_df['anchor_viability']
    anc_via_df = anc_via.to_frame()
    anc_via_df['type'] = 'Anc_Via'
    anc_via_df = anc_via_df.rename(columns={"anchor_viability": 'Viability %'})

    lib_emax_df =  anc_df['library_emax'].to_frame()
    lib_emax_df['type'] = 'Lib_Emax'
    lib_emax_df = lib_emax_df.rename(columns = {"library_emax": 'Viability %'})

    final_df = anc_via_df.append(lib_emax_df)

    bliss_emax_df = anc_df['synergy_exp_emax'].to_frame()
    bliss_emax_df['type'] = 'Bliss_Emax'
    bliss_emax_df = bliss_emax_df.rename(columns = {"synergy_exp_emax": 'Viability %'})
    final_df = final_df.append(bliss_emax_df)

    combo_emax_df = anc_df['synergy_obs_emax'].to_frame()
    combo_emax_df['type'] = 'Combo_Emax'
    combo_emax_df = combo_emax_df.rename(columns={"synergy_obs_emax": 'Viability %'})
    final_df = final_df.append(combo_emax_df)

    print(final_df)
    fig = px.strip(final_df, x='type', y='Viability %')
    return fig