import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
from components.anchor_heatmap import layout as anchor_heatmap
from components.breadcrumbs import breadcrumb_generator as crumbs

def layout(project):

    return [
        crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
                dbc.Row([
                    dbc.Col(width=9, children=[
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

                                    dcc.Loading(className='gdsc-spinner', children=
                                    dcc.Graph(
                                        id='synergy_heatmap',
                                        figure=[]
                                    ))

                                ])
                            ])
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div(
                                    children=[
                                        html.H3("Flexiscatter"),
                                        html.Hr(),
                                    ]
                                )
                            ])
                        ])

                    ]),

                    dbc.Col(width=3, children=[
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
                                ])
                            ])
                    ])
                ])
    ]

@app.callback(
    dash.dependencies.Output("synergy_heatmap", "figure"),
    # dash.dependencies.Output("synergy_heatmap", "children"),
    [dash.dependencies.Input("display_opt","value")],
    [dash.dependencies.State("url", "pathname")])
def load_heatmap(display_opt, url):
    return anchor_heatmap(display_opt,url)

