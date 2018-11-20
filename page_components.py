import dash_html_components as html
import dash_core_components as dcc

header = html.Div(
    className="navbar navbar-expand-sm navbar-light bg-light",
    children=[
        dcc.Link("GDSC Matrix Explorer", href="/", className="navbar-brand"),
        html.Div(
            html.Ul(className="navbar-nav mr-auto", children=[
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', href='#', id="projectsDropdown", role="button", children='Projects', **{'data-toggle': "dropdown"}),
                    html.Div(className='dropdown-menu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ]),
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', href='#', id="combinationsDropdown", role="button", children='Combinations'),
                    html.Div(className='dropdown-menu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ]),
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', href='#', id="modelsDropdown", role="button", children='Cell Lines'),
                    html.Div(className='dropdown-menu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ])
            ])
        )
    ]
)