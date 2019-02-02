import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc


def project_block(project):
    return dbc.Col(
        dbc.Card(
            dbc.CardBody([
                dbc.CardTitle(dcc.Link(children=project.name, href=f"/project/{project.slug}")),
                html.P(f"{len(project.models)} Cell Lines"),
                html.P(f"{project.combinations.count()} Combinations"),
                dcc.Link(f"View Project", className='btn btn-primary',
                         href=f"/project/{project.slug}")
            ])
        ),
        width=3
    )