import dash_bootstrap_components as dbc
from db import session
from models import Project

all_projects = session.query(Project).all()

header = dbc.NavbarSimple(
    children=[
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
        ),
    ],
    brand="GDSC Matrix Explorer",
    brand_href='/',
    className='shadow-sm'
)
