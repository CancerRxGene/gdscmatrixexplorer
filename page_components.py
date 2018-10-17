import dash_html_components as html
import dash_core_components as dcc

header = html.Div(
    className="navbar navbar-expand-sm navbar-light bg-light",
    children=[
        dcc.Link("GDSC Matrix Explorer", href="/", className="navbar-brand"),
        html.Div(
            html.Ul(className="navbar-nav mr-auto", children=[
                html.Li(dcc.Link("GDSC_007-A Home", href="/GDSC_007-A", className='nav-link'), className='nav-item'),
                html.Li(dcc.Link("GDSC_007-A FlexiScatter", href="/GDSC_007-A/free_scatter", className='nav-link'), className='nav-item'),
                html.Li(dcc.Link("Dose Response Plot", href="/GDSC_007-A/dose_response", className='nav-link'), className='nav-item')
            ])
        )
    ]
)