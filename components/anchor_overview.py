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
            dbc.Col(width=5,children=[
                dcc.Loading(className='gdsc-spinner', children=
                    dcc.Graph(
                        id='box1',
                        figure= generate_vialibity_boxplot(combination,'low')
                    )
                )
            ]),

            dbc.Col(width=4, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                        id='box2',
                        figure = generate_ic50_boxplot(combination,'low')
                    )
                )
            ])
             ]
         ),
        dbc.Row([
            dbc.Col(width=5, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box3',
                    figure=generate_vialibity_boxplot(combination,'high')
                ))
            ]),
            dbc.Col(width=4, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box4',
                    figure=generate_ic50_boxplot(combination, 'high')
                ))
            ]),

        ]),
    ])

def generate_vialibity_boxplot(combination,anc_conc_type):
    project_id = combination.project_id
    lib_id = combination.lib1_id
    anchor_id = combination.lib2_id

    anchor_combi_query = session.query(AnchorCombi).\
        filter(AnchorCombi.project_id == project_id).\
        filter(AnchorCombi.library_id ==  lib_id).\
        filter(AnchorCombi.anchor_id == anchor_id)

    anc_df = pd.read_sql(anchor_combi_query.statement, session.bind)

    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    if(anc_conc_type == 'low'):
        conc = anchor_conc[0]
    else:
        conc = anchor_conc[1]

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    anc_via_df = get_emax_df(anc_df_per_conc,'Anc_via', 'anchor_viability')
    lib_emax_df = get_emax_df(anc_df_per_conc,'Lib_Emax','library_emax')
    bliss_emax_df = get_emax_df(anc_df_per_conc,'Bliss_Emax','synergy_exp_emax')
    combo_emax_df = get_emax_df(anc_df_per_conc,'Combo_Emax','synergy_obs_emax')
    title = 'Anchor '+ anc_conc_type
    final_df = anc_via_df.append(lib_emax_df).append(bliss_emax_df).append(combo_emax_df)

    fig = px.strip(final_df, x='type', y='Viability %', title= title)
    # fig = px.box(final_df, x='type', y='Viability %', title=title,points="all",
    #                hover_data=["type", "Viability %", "cell_line_name"])

    return fig

def generate_ic50_boxplot(combination,anc_conc_type):
    project_id = combination.project_id
    lib_id = combination.lib1_id
    anchor_id = combination.lib2_id

    anchor_combi_query = session.query(AnchorCombi). \
        filter(AnchorCombi.project_id == project_id). \
        filter(AnchorCombi.library_id == lib_id). \
        filter(AnchorCombi.anchor_id == anchor_id)

    anc_df = pd.read_sql(anchor_combi_query.statement, session.bind)

    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    if (anc_conc_type == 'low'):
        conc = anchor_conc[0]
    else:
        conc = anchor_conc[1]

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    lib_ic50_df = get_ic50_df(anc_df_per_conc, 'Lib_IC50', 'library_xmid')
    combo_ic50_df = get_ic50_df(anc_df_per_conc, 'Combo_IC50', 'synergy_xmid')
    title = 'Anchor ' + anc_conc_type
    final_df = lib_ic50_df.append(combo_ic50_df)

    fig = px.strip(final_df, x='type', y='Norm. drug conc', title = ' ')
    # fig = px.box(final_df, x='type', y='Norm. drug conc', title=title, points="all")

    return fig

def get_emax_df(df,type,col_name):
    #type_emax_df = df[col_name].to_frame()
    type_emax_df = df[[col_name,'cell_line_name']]

    type_emax_df[col_name].update(type_emax_df[col_name] * 100)
    type_emax_df['type'] = type
    type_emax_df = type_emax_df.rename(columns = { col_name: 'Viability %'})
    return type_emax_df

def get_ic50_df(df,type,col_name):
    type_ic50_df = df[col_name].to_frame()

    # check which method is correct
    #normalise method 1
    type_ic50_df = (type_ic50_df - type_ic50_df.mean())/ type_ic50_df.std()

    # normalise method 2
    # type_ic50_df[col_name].update((type_ic50_df[col_name] - type_ic50_df[col_name].min())/ ( type_ic50_df[col_name].max() - type_ic50_df[col_name].min()))
    # type_ic50_df[col_name].update((type_ic50_df[col_name] - type_ic50_df[col_name].mean()) / (
    #             type_ic50_df.std))
    type_ic50_df['type'] = type
    type_ic50_df = type_ic50_df.rename(columns = { col_name: 'Norm. drug conc'})
    return type_ic50_df

