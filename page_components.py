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
                    dbc.NavbarBrand(children=html.Img(src="assets/sanger_logo.png", height='50rem'), href="https://sanger.ac.uk"),

                ]),
                dbc.Col(width=2, children=[
                    dbc.NavbarBrand(children=html.Img(src="assets/logo_white.svg", height='40rem'), href="/"),
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
