import dash_bootstrap_components as dbc
import dash_html_components as html

from components.project_boxplot import layout as project_boxplot
from components.project_scatter import layout as project_scatter
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_project_from_url, get_combination_link, \
    get_combination_url


def layout(url):
    project = get_project_from_url(url)

    combo_links = [get_combination_link(combo) for combo in project.combinations]

    return [
        crumbs([("Home", "/"), (project.name, "/" + project.slug)]),
        dbc.Row(
            dbc.Col(width=12, children=[
                dbc.Card([
                    dbc.CardBody([
                        dbc.CardTitle([f"Project ", html.Strong(f"{project.name}")], tag='h2', className='mb-5'),
                        dbc.Row([
                            dbc.Col(width=3, children=[
                                dbc.ListGroup(className='combinations-list', children=
                                    [dbc.ListGroupItem([
                                        html.H5([
                                            html.Strong(f"Combinations "),
                                            dbc.Badge(f" {project.combinations.count()} ", color='info')
                                        ], className="d-flex justify-content-between"),
                                        html.P("Sorted by target", className='small')
                                    ])] +
                                    [dbc.ListGroupItem(
                                        href=get_combination_url(c),
                                        action=True,
                                        children=[
                                            dbc.ListGroupItemHeading(
                                                f"{c.lib1.drug_name} + {c.lib2.drug_name}"),
                                            dbc.ListGroupItemText(
                                                f"{c.lib1.target} + {c.lib2.target}")
                                        ]
                                    ) for c in project.combinations]
                                )]),
                            dbc.Col(width=9, children=[
                                dbc.Tabs([
                                    dbc.Tab(project_boxplot(), label='Overview'),
                                    dbc.Tab(project_scatter(project.id),
                                            label='FlexiScatter')
                                ]),
                            ])
                        ])
                    ])
                ])
            ])
        ),
        html.Div(className="d-none", id='project-id', children=project.id)
    ]
