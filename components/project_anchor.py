import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
from components.anchor_heatmap import layout as anchor_heatmap
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import matrix_metrics, get_all_tissues, get_all_cancer_types

def layout(project):
    # get the data frame


    return [
        crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
                dbc.Row([   #1
                    dbc.Col(width=9, children=[   #2 col
                        dbc.Row([
                           dbc.Col(children=[
                                html.Div(
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
                                            id="display_opt",
                                            value='count',

                                        ),
                                        dcc.Loading(
                                            className='gdsc-spinner',
                                            children = dcc.Graph(
                                                id='synergy_heatmap',
                                                figure=[]
                                            )
                                        )
                                ])  # html
                            ]) #col
                        ]), # row
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
                                                        inline=True,
                                                        children=dbc.FormGroup(
                                                            dbc.Label('Tissue', html_for='tissue', className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c, 'value': c} for c in get_all_tissues()
                                                                ],
                                                                id='tissue',

                                                                className='flex-grow-1',
                                                                multi=True
                                                            )
                                                        )
                                                    ),
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup(
                                                            dbc.Label('Cancer type', html_for='cancertype', className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                    {'label': c, 'value': c} for c in get_all_cancer_types()
                                                                ],
                                                                id='cancertype',
                                                                className='flex-grow-1',
                                                                multi=True
                                                            )
                                                        )
                                                    )
                                                ]
                                            ),
                                            dbc.Col(
                                                width=6,
                                                className="mt-2 mb-4",
                                                children=[
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup(
                                                            dbc.Label('Anchor', html_for='anchor', className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                ],
                                                                id='anchor',
                                                                className='flex-grow-1',
                                                                multi=True
                                                            )
                                                        )
                                                    ),
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup(
                                                            dbc.Label('Library', html_for='library',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                ],
                                                                id='library',
                                                                className='flex-grow-1',
                                                                multi=True
                                                            )
                                                        )
                                                    ),
                                                    html.H5("OR"),
                                                    dbc.Form(
                                                        inline=True,
                                                        children=dbc.FormGroup(
                                                            dbc.Label('Combination', html_for='combination',
                                                                      className='mr-2'),
                                                            dcc.Dropdown(
                                                                options=[
                                                                ],
                                                                id='combination',
                                                                className='flex-grow-1',
                                                                multi=True
                                                            )
                                                        )
                                                    )
                                                ]
                                            )
                                        ]),
                                        dbc.Row([
                                            dbc.Col(),
                                            dbc.Col()
                                        ]),
                                        dbc.Row([
                                            dbc.Col()
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


                ]) #1 row
    ] #return


@app.callback(
    dash.dependencies.Output("synergy_heatmap", "figure"),
    # dash.dependencies.Output("synergy_heatmap", "children"),
    [dash.dependencies.Input("display_opt","value")],
    [dash.dependencies.State("url", "pathname")])
def load_heatmap(display_opt, url):
    return anchor_heatmap(display_opt,url)

