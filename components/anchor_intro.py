import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from db import session
from models import AnchorCombi, Project
import pandas as pd
from utils import get_combination_from_url, get_project_from_url
#from components.navigation.dropdowns import model_links_from_combo


def layout(project,combination):
    # combination = get_combination_from_url(url)
    # project = get_project_from_url(url)

    # query = session.query(AnchorCombi).filter(AnchorCombi.project_id == project.id
    #         ).filter(AnchorCombi.library_id == combination.lib1.id
    #                  ).filter(AnchorCombi.anchor_id == combination.lib2.id)
    #
    # df = pd.read_sql(query.statement, session.bind)
    # anchor_conc = df['anchor_conc'].drop_duplicates().sort_values()
    #
    # # find the low & high conc
    # anchor_low = anchor_conc[0]
    # anchor_high = anchor_conc[1]
    #
    # if(anchor_conc[0] > anchor_conc[1]):
    #     anchor_low = anchor_conc[1]
    #     anchor_high = anchor_conc[0]
    #
    # maxc = df['maxc'].drop_duplicates().sort_values()

    return html.Div(
        children=[
            dbc.Row(className="mt-3 mb-3", children=
                dbc.Col(width=12, children=[
                    html.H3(project.name),
                    html.H1([
                        html.Strong(f"{combination.lib2.name}"), " + ",
                        html.Strong(f"{combination.lib1.name}")
                    ]),
                   # html.P("Combination Report", className='lead')
                ])
            ),
            dbc.Row(className='d-flex', children=[
                dbc.Col(width=12, children=[
                    html.Div(className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                             children=[
                                html.H3("Drug Information"),
                                html.Hr(),
                                dcc.Loading(
                                     className='gdsc-spinner',
                                     children=html.Div(
                                         load_intro(project,combination)
                                     )
                                 )

                     #            dbc.Row([
                     #                dbc.Col(width=6, children=[
                     #                    dbc.Table(borderless=True, size='sm', children=[
                     #                        html.Tbody([
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Anchor"))
                     #
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Name")),
                     #                                html.Td(combination.lib2.name)
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Target")),
                     #                                html.Td(combination.lib2.target)
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Pathway")),
                     #                                html.Td(combination.lib2.pathway)
                     #                            ]),
                     #
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Low conc.")),
                     #                                html.Td(f"{anchor_low} µM")
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("High conc.")),
                     #                                html.Td(f"{anchor_high} µM")
                     #                            ])
                     #                        ])
                     #                    ])
                     #                ]),
                     #
                     #                dbc.Col(width=6, children=[
                     #                    dbc.Table(borderless=True, size='sm', children=[
                     #                        html.Tbody([
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Library"))
                     #
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Name")),
                     #                                html.Td(combination.lib1.name)
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Target")),
                     #                                html.Td(combination.lib1.target)
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Pathway")),
                     #                                html.Td(combination.lib1.pathway)
                     #                            ]),
                     #                            html.Tr([
                     #                                html.Td(html.Strong("Max. conc.")),
                     #                                html.Td(f"{maxc[0]} µM")
                     #                            ])
                     #                        ])
                     #                    ])
                     #                ])
                     #            ])
                      ])
                ]),

            ]),
          html.Div(className="d-none", id='project-id', children=project.id),
        ]
    )

# @app.callback(
#     dash.dependencies.Output('intro','children'),
#     dash.dependencies.Input('project-id', 'children'),
#     dash.dependencies.State("url", "pathname")
# )

def load_intro(project,combination):
    query = session.query(AnchorCombi).filter(AnchorCombi.project_id == project.id
                    ).filter(AnchorCombi.library_id == combination.lib1.id
                ).filter(AnchorCombi.anchor_id == combination.lib2.id)

    df = pd.read_sql(query.statement, session.bind)
    anchor_conc = df['anchor_conc'].drop_duplicates().sort_values()

    # find the low & high conc
    anchor_low = anchor_conc[0]
    anchor_high = anchor_conc[1]

    if (anchor_conc[0] > anchor_conc[1]):
        anchor_low = anchor_conc[1]
        anchor_high = anchor_conc[0]

    maxc = df['maxc'].drop_duplicates().sort_values()

    return (
        dbc.Row([
            dbc.Col(width=6, children=[
                dbc.Table(borderless=True, size='sm', children=[
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong("Anchor"))

                        ]),
                        html.Tr([
                            html.Td(html.Strong("Name")),
                            html.Td(combination.lib2.name)
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Target")),
                            html.Td(combination.lib2.target)
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Pathway")),
                            html.Td(combination.lib2.pathway)
                        ]),

                        html.Tr([
                            html.Td(html.Strong("Low conc.")),
                            html.Td(f"{anchor_low} µM")
                        ]),
                        html.Tr([
                            html.Td(html.Strong("High conc.")),
                            html.Td(f"{anchor_high} µM")
                        ])
                    ])
                ])
            ]),

            dbc.Col(width=6, children=[
                dbc.Table(borderless=True, size='sm', children=[
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong("Library"))

                        ]),
                        html.Tr([
                            html.Td(html.Strong("Name")),
                            html.Td(combination.lib1.name)
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Target")),
                            html.Td(combination.lib1.target)
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Pathway")),
                            html.Td(combination.lib1.pathway)
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Max. conc.")),
                            html.Td(f"{maxc[0]} µM")
                        ])
                    ])
                ])
            ])
        ])
    )