#from functools import lru_cache

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from utils import anchor_hover_label_for_boxplot

#from app import app
from db import session
from models import AnchorCombi

def layout(combination):
    anc_df = get_anc_df(combination)

    return html.Div(children=[  #html l1
        dbc.Row([   #row l1
            dbc.Col(width=12, children=[   #col l1
                html.Div(className="bg-white pt-3 px-4 pb-3 mb-3 border border-primary shadow-sm",children=[  #html l2
                    html.H3("Detailed overview of drug responses"),
                    html.Hr(),

                    dbc.Row([  #row l21
                        dbc.Col(width=4,children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                    id='box1',
                                    figure= generate_vialibity_boxplot(anc_df,'low')
                                )
                            )
                        ]),

                        dbc.Col(width=2, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                            dcc.Graph(
                                    id='box3',
                                    figure=generate_delta_emax_boxplot(anc_df, 'low')
                                )
                                        )
                        ]),

                        dbc.Col(width=3, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                        id='box2',
                                        figure = generate_ic50_boxplot(anc_df,'low')
                                    )
                                )
                        ]),

                        dbc.Col(width=2, children=[
                             dcc.Loading(className='gdsc-spinner', children=
                                 dcc.Graph(
                                     id='box4',
                                     figure=generate_delta_ic50_boxplot(anc_df, 'low')
                                 )
                                         )
                         ])
                    ]),  #row l21
                    dbc.Row([  #row l22
                        dbc.Col(width=4, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                    id='box5',
                                    figure=generate_vialibity_boxplot(anc_df,'high')
                                ))
                        ]),

                        dbc.Col(width=2, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                    id='box7',
                                    figure=generate_delta_emax_boxplot(anc_df, 'high')
                                ))
                        ]),
                        dbc.Col(width=3, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                    id='box6',
                                    figure=generate_ic50_boxplot(anc_df, 'high')
                                ))
                        ]),
                        dbc.Col(width=2, children=[
                            dcc.Loading(className='gdsc-spinner', children=
                                dcc.Graph(
                                    id='box8',
                                    figure=generate_delta_ic50_boxplot(anc_df, 'high')
                                ))
                        ]),
                    ]),  #row l22
                ]) #html l2
            ])  # col l1
        ])  #row l1
    ])  #html l1

def generate_vialibity_boxplot(anc_df,anc_conc_type):
    labels = anchor_hover_label_for_boxplot(anc_df)

    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()

    # find the low & high conc
    anchor_low = anchor_conc[0]
    anchor_high = anchor_conc[1]

    if (anchor_conc[0] > anchor_conc[1]):
        anchor_low = anchor_conc[1]
        anchor_high = anchor_conc[0]

    if (anc_conc_type == 'low'):
        conc = anchor_low
    else:
        conc = anchor_high

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    anc_via_df = get_emax_df(anc_df_per_conc,'Anc_via', 'anchor_viability')
    lib_emax_df = get_emax_df(anc_df_per_conc,'Lib_Emax','library_emax')
    bliss_emax_df = get_emax_df(anc_df_per_conc,'Bliss_Emax','synergy_exp_emax')
    combo_emax_df = get_emax_df(anc_df_per_conc,'Combo_Emax','synergy_obs_emax')
    title = 'Anchor '+ anc_conc_type

    fig = go.Figure(
                     data = [
                         go.Box(
                           name = 'Anc Via',
                           y=anc_via_df['Viability %'],
                           text=labels,
                           boxpoints = 'all',
                           jitter=0.3,
                           pointpos=0,
                           hoveron='points',
                           hoverinfo='y+text',
                           ),
                         go.Box(
                             name='Lib Emax',
                             y=lib_emax_df['Viability %'],
                             text=labels,
                             boxpoints='all',
                             jitter=0.3,
                             pointpos=0,
                             hoveron='points',
                             hoverinfo='y+text',
                         ),
                         go.Box(
                             name='Bliss Emax',
                             y=bliss_emax_df['Viability %'],
                             text=labels,
                             boxpoints='all',
                             jitter=0.3,
                             pointpos=0,
                             hoveron='points',
                             hoverinfo='y+text',
                         ),
                         go.Box(
                             name='Combo Emax',
                             y=combo_emax_df['Viability %'],
                             text = labels,
                             boxpoints='all',
                             jitter=0.3,
                             pointpos=0,
                             hoveron='points',
                             hoverinfo='y+text',
                         )
                     ],
                    layout = go.Layout(
                        yaxis={
                            'title': "Viability %"
                        },
                        showlegend=False,
                        title = title,
                        width=400,
                        height=500
                    )
                )
    return fig

def generate_ic50_boxplot(anc_df,anc_conc_type):
    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()
    labels = anchor_hover_label_for_boxplot(anc_df)
    # find the low & high conc
    anchor_low = anchor_conc[0]
    anchor_high = anchor_conc[1]

    if (anchor_conc[0] > anchor_conc[1]):
        anchor_low = anchor_conc[1]
        anchor_high = anchor_conc[0]

    if (anc_conc_type == 'low'):
        conc = anchor_low
    else:
        conc = anchor_high

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    lib_ic50_df = get_ic50_df(anc_df_per_conc, 'Lib_IC50', 'library_xmid')
    combo_ic50_df = get_ic50_df(anc_df_per_conc, 'Combo_IC50', 'synergy_xmid')

    fig = go.Figure(
            data = [
               go.Box(
                   name = 'Lib IC50',
                   y = lib_ic50_df['Norm. drug conc.'],
                   text=labels,
                   boxpoints='all',
                   jitter=0.3,
                   pointpos=0,
                   hoveron='points',
                   hoverinfo='y+text',
                ),
                go.Box(
                    name = 'Combo IC50',
                    y = combo_ic50_df['Norm. drug conc.'],
                    text=labels,
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=0,
                    hoveron='points',
                    hoverinfo='y+text',
                ),
                ],
            layout = go.Layout(
                        yaxis={
                            'title': "Norm. drug conc."
                        },
                        showlegend=False,
                       # title = title,
                        width=300,
                        height=500
                    )
        )
    return fig

def generate_delta_emax_boxplot(anc_df,anc_conc_type):
    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()
    labels = anchor_hover_label_for_boxplot(anc_df)
    # find the low & high conc
    anchor_low = anchor_conc[0]
    anchor_high = anchor_conc[1]

    if (anchor_conc[0] > anchor_conc[1]):
        anchor_low = anchor_conc[1]
        anchor_high = anchor_conc[0]

    if (anc_conc_type == 'low'):
        conc = anchor_low
    else:
        conc = anchor_high

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    delta_emax_df = get_delta_emax_df(anc_df_per_conc)
   # print(delta_emax_df)
    # fig = px.strip(delta_emax_df,x='type',y='Delta Viability %',
    #                title=' ', labels= {'type':' '},
    #                hover_name="hover_name",
    #                width=250,
    #                height=500
    #                )

    fig = go.Figure(
                     data = [
                         go.Box(
                             name='Delta Emax',
                             y=delta_emax_df['Delta Viability %'],
                             text=labels,
                             boxpoints='all',
                             jitter=0.3,
                             pointpos=0,
                             hoveron='points',
                             hoverinfo='y+text',
                         )
                     ],
                    layout = go.Layout(
                        yaxis={
                            'title': "Delta Viability %"
                            },
                        showlegend=False,
                       # hover_name="hover_name",
                        width=250,
                        height=500
                        #title = title
                        )
    )

    fig.add_shape(type="line",x0=-1,y0=20,x1=1,y1=20,
                  line=dict(color="black", width=3))
    fig.add_annotation(x=0,y=20,
                           text="Synergy threshold",
                           showarrow=True,
                           arrowhead=1)
    return fig

def generate_delta_ic50_boxplot(anc_df, anc_conc_type):
    anchor_conc = anc_df['anchor_conc'].drop_duplicates().sort_values()
    labels = anchor_hover_label_for_boxplot(anc_df)
    # find the low & high conc
    anchor_low = anchor_conc[0]
    anchor_high = anchor_conc[1]

    if (anchor_conc[0] > anchor_conc[1]):
        anchor_low = anchor_conc[1]
        anchor_high = anchor_conc[0]

    if (anc_conc_type == 'low'):
        conc = anchor_low
    else:
        conc = anchor_high

    anc_df_per_conc = anc_df.loc[anc_df['anchor_conc'] == conc]

    delta_ic50_df = get_delta_ic50_df(anc_df_per_conc)

    fig = go.Figure(
        data=[
            go.Box(
                name='Delta IC50',
                y=delta_ic50_df['Delta Norm. drug conc.'],
                text=labels,
                boxpoints='all',
                jitter=0.3,
                pointpos=0,
                hoveron='points',
                hoverinfo='y+text',
            )
        ],
        layout=go.Layout(
            yaxis={
                'title': "Log2 Delta IC50"
            },
            showlegend=False,
            # hover_name="hover_name",
            width=250,
            height=500
            # title = title
        )
    )

    fig.add_shape(type="line", x0=-1, y0=3, x1=1, y1=3,
                  line=dict(color="black", width=3))
    fig.add_annotation(x=0, y=3,
                       text="Synergy threshold",
                       showarrow=True,
                       arrowhead=1)
    return fig

def get_emax_df(df,type,col_name):
    type_emax_df = df[[col_name,'cell_line_name','cancer_type','tissue','hover_name']]

    type_emax_df[col_name].update(type_emax_df[col_name] * 100)
    type_emax_df['type'] = type.replace('_',' ')

    type_emax_df = type_emax_df.rename(columns = { col_name: 'Viability %'})
    return type_emax_df

def get_ic50_df(df,type,col_name):
    type_ic50_df = df[[col_name, 'cell_line_name', 'cancer_type', 'tissue','hover_name']]
    type_ic50_df['type'] = type.replace('_',' ')
    type_ic50_df = type_ic50_df.rename(columns = { col_name: 'Norm. drug conc.'})
    return type_ic50_df

def get_delta_ic50_df(df):
    delta_ic50_df = df[['synergy_delta_xmid', 'cell_line_name', 'cancer_type', 'tissue','hover_name']]
    delta_ic50_df['type'] = 'Delta IC50'
    delta_ic50_df = delta_ic50_df.rename(columns = { 'synergy_delta_xmid':'Delta Norm. drug conc.' })
    return delta_ic50_df

def get_delta_emax_df(df):
    delta_emax_df = df[['synergy_delta_emax', 'cell_line_name', 'cancer_type', 'tissue','hover_name']]
    delta_emax_df['type'] = 'Delta Emax'
    delta_emax_df['synergy_delta_emax'].update(delta_emax_df['synergy_delta_emax'] * 100)
    delta_emax_df = delta_emax_df.rename(columns = { 'synergy_delta_emax' : 'Delta Viability %'})
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
    # add new column for hover
    anc_df['hover_name'] = "Cell line name: " + anc_df["cell_line_name"] + " ("+ anc_df["tissue"] + ")"

    return anc_df