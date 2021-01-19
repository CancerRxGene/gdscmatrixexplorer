import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
from components.project_boxplot import layout as project_boxplot
from components.project_scatter import layout as project_scatter
from components.anchor_heatmap import layout as anchor_heatmap
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_project_from_url

def layout(url):
    project = get_project_from_url(url)

    if project is None:
        return [
            dbc.Row(className="mt-5", children=
                dbc.Col(width=12, children=[
                    html.H3("Project not found"),
                    html.P([
                        "Go back to the ",
                        dcc.Link("homepage", href="/")
                            ]),
                ])
            )
        ]
    if(project.combination_type == 'matrix'):
        return [
            crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
            dbc.Row(
                dbc.Col(width=12, children=[
                    dbc.Row([
                       dbc.Col(width=9, children=
                           html.Div(className="bg-white pt-3 px-4 pb-2 mb-3 border border shadow-sm", children=[
                               html.H3(f"{project.name}"),
                               html.Hr(),
                               dbc.Tabs([
                                       dbc.Tab(label='Overview', tab_id="tab-overview"),
                                       dbc.Tab(label='FlexiScatter', tab_id="tab-flexiscatter")
                                   ],
                                   id="project-tabs",
                                   active_tab='tab-overview'),
                               html.Div(id="content")
                           ]),

                       ),
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
                ])
            ),
            html.Div(className="d-none", id='project-id', children=project.id)
        ]
    else:
        return [
            crumbs([("Home", "/"), (project.name, "/" + project.slug)]),

            dbc.Row(
                dbc.Col(width=12, children=[
                    dbc.Row([
                        dbc.Col(width=9, children=[
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
                                      id = "cellline",
                                      value='count'
                                  ),
                                  #html.Div(id="synergy_heatmap",children=[])
                                  dcc.Loading(className='gdsc-spinner', children=
                                      dcc.Graph(
                                           id='synergy_heatmap',
                                           figure =[]
                                   ))

                                ])]),
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
                ])
            )
        ]


@app.callback(
    dash.dependencies.Output("content", "children"),
    [dash.dependencies.Input("project-tabs", "active_tab")],
    [dash.dependencies.State("url", "pathname")])
def switch_tab(at, url):
    if at == "tab-overview":
        return project_boxplot()
    elif at == "tab-flexiscatter":
        project = get_project_from_url(url)
        return project_scatter(project.id)
    return html.P("This shouldn't ever be displayed...")

@app.callback(
    dash.dependencies.Output("synergy_heatmap", "figure"),
    # dash.dependencies.Output("synergy_heatmap", "children"),
    [dash.dependencies.Input("cellline","value")],
    [dash.dependencies.State("url", "pathname")])
def load_heatmap(cellline, url):
    project = get_project_from_url(url)
    return anchor_heatmap(project.id,cellline)

