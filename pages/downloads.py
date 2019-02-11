import dash_html_components as html


def layout(*args, **kwargs):
    return html.Div([
        html.H1("Downloads", className='display-4 text-center mt-5 mb-3'),
        html.P("To follow soon", className='lead')
    ])

