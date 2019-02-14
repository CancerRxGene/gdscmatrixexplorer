import dash_bootstrap_components as dbc
import dash_html_components as html
from db import session
from models import Project

all_projects = session.query(Project).all()

header = dbc.Navbar(
    children=[
        dbc.Container([
            dbc.Row(className='w-100 align-items-center', children=[
                dbc.Col(width=2, children=[
                    dbc.NavbarBrand(children=html.Img(src="/assets/sanger_logo.png", height='50rem'), href="https://sanger.ac.uk"),

                ]),
                dbc.Col(width=2, children=[
                    dbc.NavbarBrand(children=html.Img(src="/assets/logo_white.svg", height='40rem'), href="/"),
                ]),
                dbc.Col(width=8, className="d-flex align-items-center justify-content-end", children=[
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="/")),
                        dbc.DropdownMenu(
                            children=
                            [dbc.DropdownMenuItem(f"{p.name}", href=f"/project/{p.slug}")
                             for p in all_projects],
                            nav=True,
                            in_navbar=True,
                            label="Projects",
                        ),
                        dbc.DropdownMenu(
                            children=[
                                dbc.DropdownMenuItem(
                                    f"{c.lib1.drug_name} + {c.lib2.drug_name} ({p.name})",
                                    href=f"/project/{p.slug}/combination/{c.lib1_id}+{c.lib2_id}")
                                for p in all_projects
                                for c in sorted(p.combinations, key=lambda x: f"{x.lib1.drug_name}_{x.lib2.drug_name}")],
                            nav=True,
                            in_navbar=True,
                            label="Combinations",
                            className="dropdown-combinations"
                        ),
                    ])
                ])
            ])


        ])
    ],
    dark=True,
    className='shadow-sm'
)

footer = dbc.Container(fluid=True, className='mt-5 pt-3 footer-wrapper', children=
            dbc.Container([
                dbc.Row(className='w-100', children=[
                    dbc.Col(width=3, children=[
                        html.Div([
                            html.H4("GDSC² Matrix Explorer"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Interface version: 1.0.0-beta1")),
                                html.Li(html.Span("Data version: 2019.1.1")),
                                html.Li(html.A("Code on GitHub", href='https://github.com/CancerRxGene/gdscmatrixexplorer'), className='mt-3')

                            ])
                        ])

                    ]),
                    dbc.Col(width={'size': 3, 'offset': 3}, children=[
                        html.Div([
                            html.H4("Contact Sanger"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Elizabeth Coker")),
                                html.Li(html.Span("ec18@sanger.ac.uk"))
                            ])
                        ])

                    ]),
                    dbc.Col(width=3, children=[
                        html.Div([
                            html.H4("Contact AZ"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Krishna Bulusu")),
                                html.Li(html.Span("krishna.bulusu@astrazeneca.com"))
                            ])
                        ])

                    ]),
                ])

            ])
        )
