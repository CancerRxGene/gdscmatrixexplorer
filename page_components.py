from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

from app import app

header = html.Div(
    className="navbar navbar-expand-sm navbar-light bg-light",
    children=[
        dcc.Link("GDSC Matrix Explorer", href="/", className="navbar-brand"),
        html.Div(
            html.Ul(className="navbar-nav mr-auto", children=[
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', id="projectsDropdown", role="button", children='Projects', **{'data-toggle': "dropdown"}),
                    html.Div(className='dropdown-menu', id='projectsDropdownMenu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ]),
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', href='#', id="combinationsDropdown", role="button", children='Combinations'),
                    html.Div(className='dropdown-menu', id='combinationsDropdownMenu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ]),
                html.Li(className='nav-item dropdown', children=[
                    html.A(className='nav-link dropdown-toggle', href='#', id="modelsDropdown", role="button", children='Cell Lines'),
                    html.Div(className='dropdown-menu', id='modelsDropdownMenu', children=[
                        dcc.Link(children="Action", className='dropdown-item'),
                        dcc.Link(children="Another Action", className='dropdown-item'),
                        dcc.Link(children="Third Action", className='dropdown-item'),
                    ])
                ])
            ])
        )
    ]
)

@app.callback(
    Output('projectsDropdownMenu', 'style'),
    [Input('projectsDropdown', 'n_clicks_timestamp'),
     Input('combinationsDropdown', 'n_clicks_timestamp'),
     Input('modelsDropdown', 'n_clicks_timestamp')],
    [State('projectsDropdownMenu', 'style')])
def open_projects_dropdown(p_ts, c_ts, m_ts, prev_style):
    if p_ts and (c_ts is None or p_ts > c_ts) and (m_ts is None or p_ts > m_ts):
        return({'display': 'block' if prev_style['display'] == 'none' else 'none'})
    return({'display': 'none'})

@app.callback(
    Output('combinationsDropdownMenu', 'style'),
    [Input('projectsDropdown', 'n_clicks_timestamp'),
     Input('combinationsDropdown', 'n_clicks_timestamp'),
     Input('modelsDropdown', 'n_clicks_timestamp')],
    [State('combinationsDropdownMenu', 'style')])
def open_projects_dropdown(p_ts, c_ts, m_ts, prev_style):
    if c_ts and (p_ts is None or c_ts > p_ts) and (m_ts is None or c_ts > m_ts):
        return({'display': 'block' if prev_style['display'] == 'none' else 'none'})
    return({'display': 'none'})

@app.callback(
    Output('modelsDropdownMenu', 'style'),
    [Input('projectsDropdown', 'n_clicks_timestamp'),
     Input('combinationsDropdown', 'n_clicks_timestamp'),
     Input('modelsDropdown', 'n_clicks_timestamp')],
    [State('modelsDropdownMenu', 'style')])
def open_projects_dropdown(p_ts, c_ts, m_ts, prev_style):
    if m_ts and (c_ts is None or m_ts > c_ts) and (p_ts is None or m_ts > p_ts):
        return({'display': 'block' if prev_style['display'] == 'none' else 'none'})
    return({'display': 'none'})