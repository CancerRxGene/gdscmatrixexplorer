import dash_html_components as html
import dash_core_components as dcc


def project_block(project):
    return html.Div(className='col-3', children=[
        html.Div(className='card', children=[
            html.Div(className='card-body', children=[
                html.H3(
                    dcc.Link(children=project.name, href=f"/project/{project.name}"),
                    className='card-title'
                ),
                html.P(f"{len(project.models)} Cell Lines"),
                html.P(f"{len(project.combinations)} Combinations"),
                dcc.Link(f"View Project", className='btn btn-primary',
                         href=f"/project/{project.name}")
            ])
        ])
    ])