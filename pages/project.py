import dash_bootstrap_components as dbc
import dash_html_components as html

from components.project_boxplot import layout as project_boxplot
from components.project_scatter import layout as project_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_project_from_url


def layout(url):
    project = get_project_from_url(url)

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
                               dbc.Tab(project_boxplot(), label='Overview'),
                               dbc.Tab(project_scatter(project.id),
                                       label='FlexiScatter')
                           ])
                       ])
                   ),
                    dbc.Col(width=3, children=[
                        html.Div(
                            className="bg-white pt-3 pb-2 mb-3 border border-info shadow-sm",
                            children=[
                                html.H3([
                                    f"Combinations ",
                                    dbc.Badge(f" {project.combinations.count()} ",
                                              color='info')
                                ], className="d-flex justify-content-between align-items-center px-3"),
                                html.Span(f"in {project.name}, sorted by target", className='small px-3'),
                                dbc.ListGroup(className='combinations-list mt-2', flush=True, children=[
                                    dbc.ListGroupItem(
                                        href=c.url,
                                        action=True,
                                        children=[
                                            dbc.ListGroupItemHeading(
                                                f"{c.lib1.drug_name} + {c.lib2.drug_name}"),
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
