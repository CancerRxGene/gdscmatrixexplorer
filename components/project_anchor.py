import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
from db import session
import pandas as pd
from models import Drug, AnchorCombi, Project, Model, Combination
from components.anchor_heatmap import layout as anchor_heatmap
from components.anchor_flexiscatter import cached_update_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_all_tissues, get_all_cancer_types, anchor_metrics

colour_by = {
    'Tissue': 'tissue',
    'Cancer Type': 'cancer_type',
}

def layout(project):
    tissue_query = session.query(AnchorCombi.tissue.distinct()).filter(AnchorCombi.project_id == project.id)
    tissue_df = pd.read_sql(tissue_query.statement,session.bind)

    ct_query = session.query(AnchorCombi.cancer_type.distinct()).filter(AnchorCombi.project_id == project.id)
    ct_df = pd.read_sql(ct_query.statement,session.bind)

    drugs_query = session.query(Combination).filter(Combination.project_id == project.id).distinct()
    drugs_df = pd.read_sql(drugs_query.statement, session.bind)

    lib_drugs = drugs_df['lib1_id']
    anchor_drugs = drugs_df['lib2_id']

    # create list of lib names
    lib_names = {}
    for l in lib_drugs:
        l_drug = session.query(Drug).get(l)
        lib_names[l_drug.name] = l

    # create list of anchor names
    anchor_names = {}
    for ac in anchor_drugs:
        an_drug = session.query(Drug).get(ac)
        anchor_names[an_drug.name] = ac

    #
    # cancer_types = filtered_df['cancer_type'].drop_duplicates().sort_values()
    # tissues = filtered_df['tissue'].drop_duplicates().sort_values()

    return [
         crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
                dbc.Row([   #1
                    dbc.Col(width=9, children=[   #2 col
                        dbc.Row([  # row l2
                           dbc.Col(children=[ #col l2
                                html.Div(  #html l3
                                    className="bg-white pt-3 px-4 pb-2 mb-3 border border shadow-sm",
                                    children=[
                                        html.H3(f"{project.name}"),
                                        html.Hr(),
                                        dcc.Dropdown(
                                            options=[
                                                {'label': '# synergistic cell lines',
                                                 'value': 'count'
                                                 },
                                                {'label': '% synergistic cell lines',
                                                 'value': 'percentage'
                                                 }
                                            ],
                                            id='display_opt',
                                            value='count',

                                        ),

                                        dcc.Loading(
                                            className='gdsc-spinner',
                                            children = dcc.Graph(
                                                id='synergy_heatmap',
                                                figure=[]
                                            )
                                        )
                                ])  # html l3
                            ]) #col l2
                        ]), # row l2
                        dbc.Row([
                            dbc.Col(
                                    children=[
                                        html.Div(
                                            className="bg-white pt-3 px-4 pb-2 mb-3 border border shadow-sm",
                                            children=[
                                        html.H3("Flexiscatter"),
                                        html.Hr(),
                                        dbc.Row([
                                            dbc.Col(
                                                width=6,
                                                className="mt-2 mb-4",
                                                children=[
                                                    dbc.Form(
                                                       # inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Tissue', html_for='tissue', className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                     {'label': c[0], 'value': c[0]} for c in tissue_df.values
                                                                ],
                                                                id='tissue',
                                                                className='flex-grow-1',
                                                             #   multi=True
                                                            )
                                                        ])
                                                    ),
                                                    dbc.Form(
                                                      #  inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Cancer type', className="w-25 justify-content-start"),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c[0], 'value': c[0]} for c in ct_df.values
                                                                ],
                                                                id='cancertype',
                                                                className='flex-grow-1',
                                                              #  multi=True
                                                            )
                                                        ])
                                                    )
                                                ]
                                            ),
                                            dbc.Col(
                                                width=6,
                                                className="mt-2 mb-4",
                                                children=[
                                                    dbc.Form(
                                                       # inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Anchor', html_for='anchor', className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c, 'value': anchor_names[c]} for c in anchor_names.keys()
                                                                ],
                                                                id='anchor',
                                                                className='flex-grow-1',
                                                                #multi=True
                                                            )
                                                        ])
                                                    ),
                                                    dbc.Form(
                                                      #  inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Library', html_for='library',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c, 'value': lib_names[c]} for c in lib_names.keys()
                                                                ],
                                                                id='library',
                                                                className='flex-grow-1',
                                                               # multi=True
                                                            )
                                                        ])
                                                    ),
                                                    html.H5("OR"),
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Combination', html_for='combination',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {  'label': f"{c.lib1.name} + {c.lib2.name}",
                                                                        'value': f"{c.lib1_id} + {c.lib2_id}" } for c in project.combinations
                                                                ],
                                                                id='combination',
                                                                className='flex-grow-1',
                                                                #multi=True
                                                            )
                                                        ])
                                                    )
                                                ]
                                            )
                                        ]),
                                        dbc.Row([
                                            dbc.Col(
                                                    width=6,
                                                    className="mt-2 mb-4",
                                                    children=[
                                                        dbc.Form(
                                                            #  inline=True,
                                                            children=dbc.FormGroup([
                                                                dbc.Label('x-Axis', html_for='xaxis',
                                                                          className='mr-2'),
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {'label': anchor_metrics[c]['label'], 'value': anchor_metrics[c]['value'] } for c in
                                                                           anchor_metrics
                                                                    ],
                                                                    id='xaxis',
                                                                    value = 'synergy_delta_xmid',
                                                                    className='flex-grow-1'
                                                                )
                                                            ])
                                                        )
                                                    ]
                                                ###
                                            ),
                                            dbc.Col(
                                                className="mt-2 mb-4",
                                                children=[
                                                    dbc.Form(
                                                        #  inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('y-Axis', html_for='yaxis',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': anchor_metrics[c]['label'],
                                                                     'value': anchor_metrics[c]['value']} for c in
                                                                        anchor_metrics
                                                                ],
                                                                id='yaxis',
                                                                value = 'synergy_delta_emax',
                                                                className='flex-grow-1'

                                                            )
                                                        ])
                                                    )
                                                ]
                                            )
                                        ]),
                                        dbc.Row([
                                            dbc.Col(
                                                className="mt-2 mb-4",
                                                children=[
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup([
                                                            dbc.Label('Colour by', html_for='color',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c, 'value': colour_by[c]} for c in
                                                                      colour_by
                                                                ],
                                                                id='color',
                                                                value='tissue',
                                                                className='flex-grow-1',
                                                               # multi=True
                                                            )
                                                        ])
                                                    )
                                                ]
                                            )
                                        ]),
                                        dcc.Loading(
                                            className='gdsc-spinner',
                                            children=dcc.Graph(
                                                id='flexiscatter',
                                                figure=[]
                                            )
                                         )
                            ]) #html
                        ]) #col
                        ]), #row
                    ]),  # 2 col

                    ###
                    dbc.Col(width=3, children=[  #3 col
                        html.Div(
                            className="bg-white pt-3 pb-2 mb-3 border border-primary shadow-sm",
                            children=[
                                html.H3([
                                    f"Combinations ",
                                    dbc.Badge(f" {project.combinations.count()} ",
                                              color='info')
                                ], className="d-flex justify-content-between align-items-center px-3 mb-0"),

                                html.Span(f"in {project.name}, sorted by target", className='small px-3'),

                                dbc.ListGroup(className='combinations-list mt-2', flush=True, children=[
                                    dbc.ListGroupItem(
                                        href=c.url,
                                        action=True,
                                        children=[
                                            dbc.ListGroupItemHeading(
                                                f"{c.lib1.name} + {c.lib2.name}"),
                                            dbc.ListGroupItemText(
                                                f"{c.lib1.target} + {c.lib2.target}")
                                        ]
                                    ) for c in project.combinations
                                ]) #listgroup
                        ]) #html
                    ]) # 3 col
                    ###

                ]), #1 row
        html.Div(className="d-none", id='project-id', children=project.id)
    ] #return


@app.callback(
    dash.dependencies.Output("synergy_heatmap", "figure"),
    [dash.dependencies.Input("display_opt", "value"),
     dash.dependencies.Input('project-id', 'children')])
    #[dash.dependencies.State("url", "pathname")])
def load_heatmap(display_opt, url):
    return anchor_heatmap(display_opt,url)

@app.callback(
    dash.dependencies.Output('flexiscatter',"figure"),
     #dash.dependencies.Output('cancertype',"options")],
    [dash.dependencies.Input('tissue','value'),
    dash.dependencies.Input('cancertype','value'),
    dash.dependencies.Input('library','value'),
    dash.dependencies.Input('anchor','value'),
    dash.dependencies.Input('combination','value'),
    dash.dependencies.Input('color', 'value'),
    dash.dependencies.Input('xaxis','value'),
    dash.dependencies.Input('yaxis','value'),
    dash.dependencies.Input('project-id', 'children')]
)
def load_flexiscatter(tissue,cancertype,library,anchor,combination,color,xaxis,yaxis,project_id):
    return cached_update_scatter(tissue,cancertype,library,anchor,combination,color,xaxis,yaxis,project_id)

