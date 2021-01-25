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
    anc_df = get_anc_df(combination)

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
                        id='box1',
                        figure= generate_vialibity_boxplot(anc_df,'low')
                    )
                )
            ]),

            dbc.Col(width=5, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                        id='box2',
                        figure = generate_ic50_boxplot(anc_df,'low')
                    )
                )
            ]),
             dbc.Col(width=4, children=[
                 dcc.Loading(className='gdsc-spinner', children=
                 dcc.Graph(
                     id='box3',
                     figure=generate_delta_emax_boxplot(anc_df, 'low')
                 )
                             )
             ]),
             dbc.Col(width=4, children=[
                 dcc.Loading(className='gdsc-spinner', children=
                 dcc.Graph(
                     id='box4',
                     figure=generate_delta_ic50_boxplot(anc_df, 'low')
                 )
                             )
             ])
             ]
         ),
        dbc.Row([
            dbc.Col(width=6, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box5',
                    figure=generate_vialibity_boxplot(anc_df,'high')
                ))
            ]),
            dbc.Col(width=5, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box6',
                    figure=generate_ic50_boxplot(anc_df, 'high')
                ))
            ]),
            dbc.Col(width=4, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box7',
                    figure=generate_delta_emax_boxplot(anc_df, 'high')
                ))
            ]),
            dbc.Col(width=4, children=[
                dcc.Loading(className='gdsc-spinner', children=
                dcc.Graph(
                    id='box8',
                    figure=generate_delta_ic50_boxplot(anc_df, 'high')
                ))
            ]),
        ]),
    ])

def generate_vialibity_boxplot(anc_df,anc_conc_type):
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

    fig = px.strip(final_df, x='type', y='Viability %', title= title,
                   labels= {'type':' '})
    # fig = px.box(final_df, x='type', y='Viability %', title=title,points="all",
    #                hover_data=["type", "Viability %", "cell_line_name"])

    return fig

def generate_ic50_boxplot(anc_df,anc_conc_type):
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

    fig = px.strip(final_df, x='type', y='Norm. drug conc.', title = ' ', labels= {'type':' '})
    # fig = px.box(final_df, x='type', y='Norm. drug conc', title=title, points="all")

    return fig

def generate_delta_emax_boxplot(anc_df,anc_conc_type):
    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    if(anc_conc_type == 'low'):
        conc = anchor_conc[0]
    else:
        conc = anchor_conc[1]

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    delta_emax_df = get_delta_emax_df(anc_df_per_conc)
    fig = px.strip(delta_emax_df,x='type',y='Delta Viability (%)',title=' ', labels= {'type':' '})
    return fig

def generate_delta_ic50_boxplot(anc_df, anc_conc_type):
    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    if (anc_conc_type == 'low'):
        conc = anchor_conc[0]
    else:
        conc = anchor_conc[1]

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    delta_emax_df = get_delta_ic50_df(anc_df_per_conc)
    fig = px.strip(delta_emax_df, x='type', y='Delta Norm. drug conc.', title=' ', labels= {'type':' '})
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
    type_ic50_df['type'] = type
    type_ic50_df = type_ic50_df.rename(columns = { col_name: 'Norm. drug conc.'})
    return type_ic50_df

def get_delta_ic50_df(df):
    delta_ic50_df = df['synergy_delta_xmid'].to_frame()
    delta_ic50_df['type'] = 'Delta_IC50'
    delta_ic50_df = delta_ic50_df.rename(columns = { 'synergy_delta_xmid':'Delta Norm. drug conc.' })
    return delta_ic50_df

def get_delta_emax_df(df):
    delta_emax_df = df['synergy_delta_emax'].to_frame()
    delta_emax_df['type'] = 'Delta_Emax'
    delta_emax_df['synergy_delta_emax'].update(delta_emax_df['synergy_delta_emax'] * 100)
    delta_emax_df = delta_emax_df.rename(columns = { 'synergy_delta_emax' : 'Delta Viability (%)'})
    return delta_emax_df

def get_anc_df(combination):
    project_id = combination.project_id
    lib_id = combination.lib1_id
    anchor_id = combination.lib2_id

    anchor_combi_query = session.query(AnchorCombi). \
        filter(AnchorCombi.project_id == project_id). \
        filter(AnchorCombi.library_id == lib_id). \
        filter(AnchorCombi.anchor_id == anchor_id)

    anc_df = pd.read_sql(anchor_combi_query.statement, session.bind)
    return anc_df