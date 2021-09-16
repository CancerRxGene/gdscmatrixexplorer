import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from app import app
from db import session
import pandas as pd
from models import Drug, AnchorCombi, AnchorSynergy, Project, AnchorProjectStats
from components.anchor_heatmap import layout as anchor_heatmap
from components.anchor_flexiscatter import cached_update_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import anchor_metrics


colour_by = {
    'Tissue': 'tissue',
    'Cancer Type': 'cancer_type',
    'Combination': 'combo_name'
}

#pre-coded the tissues & cancer_types instead of query DB on the fly to increase the performance
tissues = {
    'Pan-Cancer': [
        'Adrenal Gland',
        'Biliary Tract',
        'Bladder',
        'Bone',
        'Breast',
        'Central Nervous System',
        'Cervix',
        'Endometrium',
        'Esophagus',
        'Haematopoietic and Lymphoid',
        'Head and Neck',
        'Kidney',
        'Large Intestine',
        'Liver',
        'Lung',
        'Ovary',
        'Pancreas',
        'Peripheral Nervous System',
        'Prostate',
        'Skin',
        'Soft Tissue',
        'Stomach',
        'Testis',
        'Thyroid',
        'Uterus',
        'Vulva'
    ],
    'Breast': ['Breast'],
    'Colon': ['Large Intestine'],
    'Pancreas': ['Pancreas']
}

cancer_types = {
    'Pan-Cancer':[
        'Acute Myeloid Leukemia',
        "B-Cell Non-Hodgkin's Lymphoma",
        'B-Lymphoblastic Leukemia',
        'Biliary Tract Carcinoma',
        'Bladder Carcinoma',
        'Breast Carcinoma',
        "Burkitt's Lymphoma",
        'Cervical Carcinoma',
        'Chondrosarcoma',
        'Chronic Myelogenous Leukemia',
        'Colorectal Carcinoma',
        'Endometrial Carcinoma',
        'Esophageal Carcinoma',
        'Esophageal Squamous Cell Carcinoma',
        "Ewing's Sarcoma",
        'Gastric Carcinoma',
        'Glioblastoma',
        'Glioma',
        'Head and Neck Carcinoma',
        'Hepatocellular Carcinoma',
        "Hodgkin's Lymphoma",
        'Kidney Carcinoma',
        'Melanoma',
        'Mesothelioma',
        'Neuroblastoma',
        'Non-Cancerous',
        'Non-Small Cell Lung Carcinoma',
        'Oral Cavity Carcinoma',
        'Osteosarcoma',
        'Other Blood Carcinomas',
        'Other Solid Carcinomas',
        'Ovarian Carcinoma',
        'Pancreatic Carcinoma',
        'Plasma Cell Myeloma',
        'Prostate Carcinoma',
        'Rhabdomyosarcoma',
        'Small Cell Lung Carcinoma',
        'Squamous Cell Lung Carcinoma',
        "T-Cell Non-Hodgkin's Lymphoma",
        'T-Lymphoblastic Leukemia',
        'Thyroid Gland Carcinoma'

    ],
    'Breast': ['Breast Carcinoma'],
    'Colon': ['Colorectal Carcinoma'],
    'Pancreas': ['Pancreatic Carcinoma']
}

def layout(project):
    print('project name: ' + project.name)
    # get data for flexiscatter options
    combos = project.combinations
    sorted_combos = sorted(combos, key=lambda combos: combos.lib2.name)

    lib_names = {}
    anchor_names = {}
    for c in sorted_combos:
        lib_names[c.lib1.name] = c.lib1_id
        anchor_names[c.lib2.name] = c.lib2_id

    return [
         crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
                dbc.Row(className="mt-3 mb-3", children = [ #1

                    dbc.Col(width=12, children=[   #2 col
                         dbc.Row([ # row l2
                             dbc.Col(children=[  #clo l2
                                html.Div(
                                    className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                                    children=[
                                        html.H3(f"{project.name}"),
                                        html.Hr(),
                                        dcc.Loading(
                                            className='gdsc-spinner',
                                            children=html.Div(
                                                id='project_info',
                                            )
                                        )
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
                                                )
                                            )
                                    ])  # html l3
                                ]) #col l2
                            ]), # row l2
                        dbc.Row([
                                dcc.Location('anchor-scatter-url'),
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
                                                            children=dbc.FormGroup([
                                                                dbc.Label('Tissue', html_for='tissue', className='mr-2'),
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {'label': c, 'value': c} for c in tissues[project.name]
                                                                    ],
                                                                    id='tissue',
                                                                    className='flex-grow-1',
                                                                    multi=True
                                                                )
                                                            ])
                                                        ),
                                                        dbc.Form(
                                                            children=dbc.FormGroup([
                                                                dbc.Label('Cancer type', className="w-25 justify-content-start"),
                                                                dcc.Dropdown(
                                                                    options=[
                                                                        {'label': c, 'value': c} for c in cancer_types[project.name]
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
                                                )
                                             )
                                ]) #html
                            ]) #col
                            ]), #row
                    ]),  # 2 col

                    dbc.Col(
                        width=12,
                            # className='d-print-none align-self-stretch pb-3',
                            children=
                            html.Div(
                                className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                                children=
                                [
                                html.H3(f"View combinations in {project.name} ( {project.combinations.count()} )"),
                                dcc.Loading(
                                    className='gdsc-spinner',
                                    children=html.Div(
                                        id='combination_table',
                                    )
                                )
                                ])
                    )
                ]), #1 row
        html.Div(className="d-none", id='project-id', children=project.id),

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
    print("load flexi scatter")
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

@app.callback(
     dash.dependencies.Output('project_info','children'),
    [dash.dependencies.Input('project-id', 'children')]
)
def load_project_info(project_id):
    project = session.query(Project).get(project_id)

    df_query = session.query(AnchorProjectStats).filter(AnchorProjectStats.project_id == project_id)
    df = pd.read_sql(df_query.statement, session.bind)

    celllines_count = df['cell_lines_count']
    lib_drugs_count = df['lib_drugs_count']
    anchor_drugs_count = df['anchor_drugs_count']
    combination_counts = df['combinations_count']
    measurements = df['measurements']

    (synergy_count, synergy_frequency) = get_syngergy_data(project)

    return (
        dbc.Row([
            dbc.Col(width=5,children=[
                dbc.Table(borderless=True, size='sm', children=[
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong("Combinations")),
                            html.Td(combination_counts),
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Library drugs")),
                            html.Td(lib_drugs_count),
                        ]),
                        html.Tr([
                            html.Td(html.Strong("Anchor drugs")),
                            html.Td(anchor_drugs_count),
                       ])
                    ])
                ])
            ]),
            dbc.Col(width=1),
            dbc.Col(width=6, children=[
                dbc.Table(borderless=True, size='sm', children=[
                    html.Tbody([
                        html.Tr([

                            html.Td(html.Strong("Cell lines")),
                            html.Td(celllines_count),
                        ]),
                        html.Tr([

                            html.Td(html.Strong("Measurements")),
                            html.Td(measurements),

                        ]),
                        html.Tr([

                            html.Td(html.Strong("Overall frequency of synergy")),
                            html.Td(str(synergy_frequency) + "%"),

                        ]),
                    ])
                ])
            ]),
        ]),
    )

@app.callback(
    dash.dependencies.Output('anchor-scatter-url', 'pathname'),
    [dash.dependencies.Input('flexiscatter', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        #p = clicked['points'][0]['custom_data']
        # return p['to']
        print(clicked['points'][0]['customdata'][3])
        to = f"https://cellmodelpassports.sanger.ac.uk/passports/{clicked['points'][0]['customdata'][3]}"
        print(to)
        #return to
#     else:
#         return "/"


def get_anchor_combi_data(project_id):
    df_query = session.query(AnchorCombi).filter(AnchorCombi.project_id == project_id)
    df = pd.read_sql(df_query.statement, session.bind)
    return df

def get_syngergy_data(project):
    # get synergy frequency
    synergy_query = session.query(AnchorSynergy).filter(AnchorSynergy.project_id == project.id)
    synergy_df = pd.read_sql(synergy_query.statement, session.bind)

    total_count = synergy_df['cell_line_name'].size
    synergy = synergy_df[synergy_df.synergy == 1]
    synergy_count = synergy['cell_line_name'].size

    synergy_frequency = round(synergy_count / total_count * 100, 2)

    return (synergy_count, synergy_frequency)

def get_combination_drugs(project_id):
    project = session.query(Project).get(project_id)
    combos = project.combinations
    lib_names = {}
    anchor_names = {}

    for c in combos:
        lib = c.lib1
        lib_names[lib.name] = lib.id

        anchor = c.lib2
        anchor_names[anchor.name] = anchor.id

    sorted_combos = sorted(combos, key=lambda combos: combos.lib2.name)

    my_table_df = []
    id = 1
    for c in combos:
        my_table_df_dic = {}
        my_table_df_dic['id'] = id
        my_table_df_dic['lib_name'] = c.lib1.name
        my_table_df_dic['lib_target'] = c.lib1.target
        my_table_df_dic['lib_pathway'] = c.lib1.pathway
        my_table_df_dic['anc_name'] = c.lib2.name
        my_table_df_dic['anc_target'] = c.lib2.target
        my_table_df_dic['anc_pathway'] = c.lib2.pathway
        my_table_df_dic['link'] = '[' + c.lib2.name + ' + ' + c.lib1.name + '](' + project.slug + '/combination/' + str(
            c.lib1.id) + '+' + str(c.lib2.id) + ')'
        my_table_df.append(my_table_df_dic)
        id = id + 1

    my_table_df = sorted(my_table_df, key=lambda k: k['anc_name'])

    columns = [
        {'name': 'Anchor name', 'id': 'anc_name'},
        {'name': 'Anchor target', 'id': 'anc_target'},
        {'name': 'Anchor pathway', 'id': 'anc_pathway'},
        {'name': 'Lib name', 'id': 'lib_name'},
        {'name': 'Lib target', 'id': 'lib_target'},
        {'name': 'Lib pathway', 'id': 'lib_pathway'},
        {'name': 'Link', 'id': 'link', 'presentation': 'markdown'}
    ]

    return (my_table_df, columns)

@app.callback(
     dash.dependencies.Output('combination_table','children'),
    [dash.dependencies.Input('project-id', 'children')]
)
def load_combination_table(project_id):
    (my_table_df, columns) = get_combination_drugs(project_id)
    return (
        dash_table.DataTable(
              id='datatable-interactivity',
              columns = columns,
              data=my_table_df,

              filter_action="native",

              sort_action="native",
              sort_mode="multi",

              page_action="native",
              page_current=0,
              page_size=10,
              style_cell={'textAlign': 'left'},
              style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',

              },
              style_data={'width': '80px', 'minWidth': '50px',
                          'maxWidth': '80px','overflow': 'hidden',
                           'textOverflow': 'ellipsis'},
              style_cell_conditional=[
                {'if': {'column_id': 'link'},
                 'width': '30px'
                 },
                 ]
        ),
    )
