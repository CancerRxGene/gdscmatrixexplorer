import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from db import session
from models import Project
from utils import url_parser
from app import app



header = dbc.Navbar(
    children=[

    ],
    dark=True,
    className='shadow-sm'
)


def generate_header():
    return dbc.Navbar(
        dark=True,
        className='shadow-sm',
        id='main-navbar'
    )


def generate_navitem(link_text, link_href, link_page_type, current_page_type):
    return dbc.NavItem(
        dbc.NavLink(
            link_text,
            href=link_href,
            className='active' if link_page_type == current_page_type else ''
        )
    )


def generate_default_navitem(link_text, current_page_type):
    link_href = "/" + link_text.lower()
    link_page_type = link_text.lower()
    return generate_navitem(link_text, link_href, link_page_type, current_page_type)


@app.callback(dash.dependencies.Output('main-navbar', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def dropdown_handler(pathname):
    if pathname is None:
        return ''
    page_type = url_parser(pathname)
    all_projects = session.query(Project).all()

    return dbc.Container([
        dbc.Row(className='w-100 align-items-center', children=[
            dbc.Col(width=2, children=[
                dbc.NavbarBrand(children=html.Img(src="/assets/sanger_logo.png",
                                                  height='50rem'),
                                href="https://sanger.ac.uk"),

            ]),
            dbc.Col(width=2, children=[
                dbc.NavbarBrand(children=html.Img(src="/assets/logo_white.svg",
                                                  height='40rem'), href="/"),
            ]),
            dbc.Col(width=8,
                className="d-flex align-items-center justify-content-end",
                children=[
                    dbc.Nav([
                        generate_navitem("Home", "/", "home", page_type),
                        dbc.DropdownMenu(
                            children=
                            [dbc.DropdownMenuItem(f"{p.name}",
                                                  href=f"/project/{p.slug}")
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
                                for c in sorted(p.combinations, key=lambda
                                    x: f"{x.lib1.drug_name}_{x.lib2.drug_name}")],
                            nav=True,
                            in_navbar=True,
                            label="Combinations",
                            className="dropdown-combinations"
                        ),
                        generate_default_navitem("Documentation",
                                                 page_type),
                        generate_default_navitem("Downloads", page_type)
                    ])
                ]
            )
        ])

    ])
