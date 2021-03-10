import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from app import app
from db import session
import pandas as pd
from models import Drug, AnchorCombi, Project, Model, Combination, AnchorSynergy
from components.anchor_heatmap import layout as anchor_heatmap
from components.anchor_flexiscatter import cached_update_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_all_tissues, get_all_cancer_types, anchor_metrics
from components.navigation.dropdowns import combo_links_from_project

colour_by = {
    'Tissue': 'tissue',
    'Cancer Type': 'cancer_type',
    'Combination': 'combo_name'
}

def layout(project):
    df_query = session.query(AnchorCombi).filter(AnchorCombi.project_id ==  project.id)
    df = pd.read_sql(df_query.statement, session.bind)
    cancer_types = df['cancer_type'].drop_duplicates().sort_values()
    tissues = df['tissue'].drop_duplicates().sort_values()
    celllines = df['cell_line_name'].drop_duplicates()
    lib_drugs = df['library_id'].drop_duplicates()
    anchor_drugs = df['anchor_id'].drop_duplicates()

    # get synergy frequency
    synergy_query = session.query(AnchorSynergy).filter(AnchorSynergy.project_id == project.id)
    synergy_df = pd.read_sql(synergy_query.statement,session.bind)
    total_count = synergy_df['cell_line_name'].size
    synergy  = synergy_df[synergy_df.synergy == 1]
    synergy_count = synergy['cell_line_name'].size

    synergy_frequency = round(synergy_count/total_count * 100, 2)

    # create lib names dictionary
    lib_names = {}
    for l in lib_drugs:
        l_drug = session.query(Drug).get(l)
        lib_names[l_drug.name] = l

    # create anchor names dictionary
    anchor_names = {}
    for ac in anchor_drugs:
        an_drug = session.query(Drug).get(ac)
        anchor_names[an_drug.name] = ac

    combos = project.combinations
    sorted_combos = sorted(combos, key=lambda combos: combos.lib2.name)

    my_table_df = []
    for c in project.combinations:
        my_table_df_dic = {}
        my_table_df_dic['lib_name'] = c.lib1.name
        my_table_df_dic['lib_target'] = c.lib1.target
        my_table_df_dic['anc_name'] = c.lib2.name
        my_table_df_dic['anc_target'] = c.lib2.target
        my_table_df_dic['link'] = '[View](pan-cancer/combination/' + str(c.lib1.id) + '+' + str(c.lib2.id)+')'
        my_table_df.append(my_table_df_dic)

    # columns = [
    #               {"name": i, "id": i } for i in my_table_df[0].keys()
    #           ]
    # print(columns)

    columns = [
        {'name':'Lib name', 'id': 'lib_name'},
        {'name': 'Lib target', 'id': 'lib_target'},
        {'name': 'Anchor name', 'id': 'anc_name'},
        {'name': 'Anchor target', 'id': 'anc_target'},
        {'name':'Link','id':'link', 'presentation': 'markdown'}
    ]
    # columns.append({'name': 'Link', 'id':'Link','presentation':'markdown'})
    print(columns)
    print(my_table_df)

    return [
         crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
                dbc.Row(className="mt-3 mb-3", children = [ #1

                    dbc.Col(width=12, children=[   #2 col
                        dbc.Row([ # row l2
                            dbc.Col(children=[  #clo l2
                                html.Div(
                                    className="bg-white pt-3 px-4 pb-2 mb-3 border shadow-sm",
                                    children=[
                                        html.H3(f"{project.name}"),
                                        html.Hr(),
                                        dbc.Row([
                                            dbc.Col(width=5,children=[
                                                dbc.Table(borderless=True, size='sm', children=[
                                                    html.Tr([
                                                        html.Td(html.Strong("Combinations")),
                                                        html.Td(project.combinations.count()),
                                                    ]),
                                                    html.Tr([
                                                        html.Td(html.Strong("Library drugs")),
                                                        html.Td(lib_drugs.size),

                                                    ]),
                                                    html.Tr([
                                                        html.Td(html.Strong("Anchor drugs")),
                                                        html.Td(anchor_drugs.size),

                                                    ]),
                                                ])
                                            ]),
                                            dbc.Col(width=1),
                                            dbc.Col(width=6, children=[
                                                dbc.Table(borderless=True, size='sm', children=[
                                                    html.Tr([

                                                        html.Td(html.Strong("Cell lines")),
                                                        html.Td(celllines.size),
                                                    ]),
                                                    html.Tr([

                                                        html.Td(html.Strong("Measurements")),
                                                        html.Td(len(df)),

                                                    ]),
                                                    html.Tr([

                                                        html.Td(html.Strong("Overall frequency of synergy")),
                                                        html.Td(str(synergy_frequency) + "%"),

                                                    ]),
                                                ])
                                            ]),
                                        ]),

                                    ]
                                ),


                            ]) #col l2
                        ]),  # row l2
                        dbc.Row([  # row l2
                               dbc.Col(children=[ #col l2
                                    html.Div(  #html l3
                                        className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                                        children=[
                                            html.H3("Synergy Heatmap"),
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
                                                    #figure=[]
                                                )
                                            )
                                    ])  # html l3
                                ]) #col l2
                            ]), # row l2
                        dbc.Row([
                                dbc.Col(
                                        children=[
                                            html.Div(
                                                className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
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
                                                                        {'label': c, 'value': c} for c in tissues
                                                                    ],
                                                                    id='tissue',
                                                                    className='flex-grow-1',
                                                                    multi=True
                                                                )
                                                            ])
                                                        ),
                                                        dbc.Form(
                                                          #  inline=True,
                                                            children=dbc.FormGroup([
                                                                dbc.Label('Cancer type', className="w-25 justify-content-start"),
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {'label': c, 'value': c} for c in cancer_types

                                                                    ],
                                                                    id='cancertype-select',
                                                                    className='flex-grow-1',
                                                                    multi=True
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
                                                                        {'label': c, 'value': anchor_names[c]} for c in sorted(anchor_names.keys())
                                                                    ],
                                                                    id='anchor',
                                                                    className='flex-grow-1',
                                                                    multi=True
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
                                                                        {'label': c, 'value': lib_names[c]} for c in sorted(lib_names.keys())
                                                                    ],
                                                                    id='library',
                                                                    className='flex-grow-1',
                                                                    multi=True
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
                                                                        { 'label': f" {c.lib2.name} + {c.lib1.name}",
                                                                            'value': f"{c.lib2_id} + {c.lib1_id}"} for c in sorted_combos
                                                                    ],
                                                                    id='combination',
                                                                    className='flex-grow-1',
                                                                    multi=True
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
                                                   # figure=[]
                                                )
                                             )
                                ]) #html
                            ]) #col
                            ]), #row
                    ]),  # 2 col

                    ####
                    # dbc.Col(
                    #     width=12,
                    #     className='d-print-none align-self-stretch pb-3',
                    #     children=
                    #     html.Div(
                    #         className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm h-100",
                    #         children=[
                    #             html.H3(f"View combinations in {project.name} ( {project.combinations.count()} )", dbc.Badge(f" {project.combinations.count()} ",
                    #                           color='info')),
                    #             html.Hr(),
                    #             dbc.Row(
                    #                 className="pb-4",
                    #                 children=dbc.Col(
                    #                     width=12,
                    #                     children=combo_links_from_project(project)
                    #                 ),
                    #             )
                    #         ],
                    #     )
                    # ),
                    dbc.Col(
                        width=12,
                        # className='d-print-none align-self-stretch pb-3',
                        children=
                        html.Div(
                            className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                            children=
                            [
                            html.H3(f"View combinations in {project.name} ( {project.combinations.count()} )"),
                             dash_table.DataTable(
                                    id='datatable-interactivity',
                                    # columns=[
                                    #     {"name": i, "id": i, "deletable": False, "selectable": True} for i in table_df.columns
                                    # ],
                                 # columns=[
                                 #     {"name": i, "id": i, "deletable": False, "selectable": True} for i in my_table_df[0].keys()
                                 # ],
                                 columns = columns,
                                  # data=table_df.to_dict('records'),
                                   data=my_table_df,
                                   editable=False,
                                   filter_action="native",

                                    sort_action="native",
                                    sort_mode="multi",
                                    # column_selectable="single",
                                    # row_selectable="multi",
                                    # row_deletable=True,
                                    # selected_columns=[],
                                    # selected_rows=[],
                                    page_action="native",
                                    page_current=0,
                                    page_size=15,
                                    style_cell={'textAlign': 'center'},
                                    style_header={
                                     'backgroundColor': 'white',
                                     'fontWeight': 'bold'
                                   },
                                    # style_table={'height': 400,},
                                    style_data={'width': '150px', 'minWidth': '150px',
                                                'maxWidth': '150px','overflow': 'hidden',
                                                'textOverflow': 'ellipsis'}
                             ),
                               ]
                        )
                    ),
                ]), #1 row
        html.Div(className="d-none", id='project-id', children=project.id)
    ] #return


@app.callback(
    dash.dependencies.Output("synergy_heatmap", "figure"),
    [dash.dependencies.Input("display_opt", "value"),
     dash.dependencies.Input('project-id', 'children')])
def load_heatmap(display_opt, url):
    return anchor_heatmap(display_opt,url)

@app.callback(
    dash.dependencies.Output('flexiscatter','figure'),
    # dash.dependencies.Output('cancertype-select','options')],
    [dash.dependencies.Input('tissue','value'),
    dash.dependencies.Input('cancertype-select','value'),
    dash.dependencies.Input('library','value'),
    dash.dependencies.Input('anchor','value'),
    dash.dependencies.Input('combination','value'),
    dash.dependencies.Input('color', 'value'),
    dash.dependencies.Input('xaxis','value'),
    dash.dependencies.Input('yaxis','value'),
    dash.dependencies.Input('project-id', 'children')]
)
def load_flexiscatter(tissue,cancertype,library,anchor,combination,color,xaxis,yaxis,project_id):
    if isinstance(tissue, list):
        tissue = tuple(tissue)
    if isinstance(cancertype, list):
        cancertype = tuple(cancertype)
    if isinstance(library, list):
        library = tuple(library)
    if isinstance(anchor, list):
        anchor = tuple(anchor)
    if isinstance(combination, list):
        combination = tuple(combination)
    return cached_update_scatter(tissue,cancertype,library,anchor,combination,color,xaxis,yaxis,project_id)

