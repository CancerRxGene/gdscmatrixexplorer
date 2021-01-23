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
         dbc.Row([
            dbc.Col(width=6,children=[
                dcc.Loading(className='gdsc-spinner', children=
                    dcc.Graph(
                        id='scatter1',
                        figure= generate_anchor_boxplot(combination,'low')
                    )
                )
            ]),

            # dbc.Col(width=6, children=[
            #     dcc.Loading(className='gdsc-spinner', children=
            #     dcc.Graph(
            #             id='scatter2',
            #             # figure=generate_anchor_boxplot(combination,'high')
            #         )
            #     )
            # ])
             ]
         ),
        dbc.Row([
            # dbc.Col(width=6, children=[
            #     dcc.Loading(className='gdsc-spinner', children=
            #     dcc.Graph(
            #
            #     ))
            # ]),

            dbc.Col(width=6, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='scatter4',
                    figure=generate_anchor_boxplot(combination,'high')
                ))
            ])
        ]),
    ])

def generate_anchor_boxplot(combination,conc_type):
    project_id = combination.project_id
    lib_id = combination.lib1_id
    anchor_id = combination.lib2_id

    anchor_combi_query = session.query(AnchorCombi).\
        filter(AnchorCombi.project_id == project_id).\
        filter(AnchorCombi.library_id ==  lib_id).\
        filter(AnchorCombi.anchor_id == anchor_id)

    anc_df = pd.read_sql(anchor_combi_query.statement, session.bind)

    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    if(conc_type == 'low'):
        conc = anchor_conc[0]
    else:
        conc = anchor_conc[1]

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    anc_via_df = get_emax_df(anc_df_per_conc,'Anc_via', 'anchor_viability')
    lib_emax_df = get_emax_df(anc_df_per_conc,'Lib_Emax','library_emax')
    bliss_emax_df = get_emax_df(anc_df_per_conc,'Bliss_Emax','synergy_exp_emax')
    combo_emax_df = get_emax_df(anc_df_per_conc,'Combo_Emax','synergy_obs_emax')
    title = 'Anchor '+ conc_type
    final_df = anc_via_df.append(lib_emax_df).append(bliss_emax_df).append(combo_emax_df)

    # fig = px.strip(final_df, x='type', y='Viability %', title= title, hover_data=["type","Viability %","cell_line_name"])
    fig = px.box(final_df, x='type', y='Viability %', title=title,points="all",
                   hover_data=["type", "Viability %", "cell_line_name"])

    return fig

def get_emax_df(df,type,col_name):
    #type_df = df[col_name].to_frame()
    type_df = df[[col_name,'cell_line_name']]
    type_df['type'] = type
    type_df = type_df.rename(columns = { col_name: 'Viability %'})
    return type_df
