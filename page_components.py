from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

from app import app
from db import session
from models import Project

all_projects = session.query(Project).all()

header = html.Div(
    className="navbar navbar-expand-sm navbar-light bg-light",
    children=[
        dcc.Link("GDSC Matrix Explorer", href="/", className="navbar-brand"),
        html.Div(
            html.Ul(className="navbar-nav mr-auto", children=[
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', id="projectsDropdown", role="button", children='Projects', **{'data-toggle': "dropdown"}),
                    html.Div(className='dropdown-menu', id='projectsDropdownMenu', children=
                        [dcc.Link(children=f"{p.name}", href=f"/project/{p.slug}", className='dropdown-item') for p in all_projects]
                    )
                ]),
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', id="combinationsDropdown", role="button", children='Combinations'),
                    html.Div(className='dropdown-menu', id='combinationsDropdownMenu', children=
                    [dcc.Link(
                        children=f"{c.lib1.drug_name} + {c.lib2.drug_name} ({p.name})",
                        href=f"/project/{p.slug}/combination/{c.lib1_id}+{c.lib2_id}",
                        className='dropdown-item')
                     for p in all_projects
                     for c in sorted(p.combinations, key=lambda x: f"{x.lib1.drug_name}_{x.lib2.drug_name}")])
                ])
            ])
        )
    ]
)

@app.callback(
    Output('projectsDropdownMenu', 'style'),
    [Input('projectsDropdown', 'n_clicks_timestamp'),
     Input('combinationsDropdown', 'n_clicks_timestamp')],
    [State('projectsDropdownMenu', 'style')])
def open_projects_dropdown(p_ts, c_ts, prev_style):
    if p_ts and (c_ts is None or p_ts > c_ts):
        return({'display': 'block' if prev_style['display'] == 'none' else 'none'})
    return({'display': 'none'})

@app.callback(
    Output('combinationsDropdownMenu', 'style'),
    [Input('projectsDropdown', 'n_clicks_timestamp'),
     Input('combinationsDropdown', 'n_clicks_timestamp')],
    [State('combinationsDropdownMenu', 'style')])
def open_projects_dropdown(p_ts, c_ts, prev_style):
    if c_ts and (p_ts is None or c_ts > p_ts):
        return({'display': 'block' if prev_style['display'] == 'none' else 'none'})
    return({'display': 'none'})
