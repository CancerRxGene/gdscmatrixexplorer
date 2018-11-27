import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app
from pages import project, home, matrix, combinations
from components import project_scatter
from page_components import header

app.layout = html.Div([
        dcc.Location(id='url', refresh=True),
        html.Div(
            id='wrapper',
            className="container",
            children=[
                header,
                html.Div(
                    className='row',
                    children=[
                        html.Div(
                            id='page-content',
                            className="col-12",
                            children=[
                                html.Div(className="d-none", children=dt.DataTable(rows=[{}], id='dummy_table'))
                        ]),
                ])
        ])

    ])

server = app.server

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return ""
    elif pathname == '/':
        return home.layout()
    elif pathname.startswith('/project'):
        segments = pathname.split("/")
        if len(segments) == 3:
            return project.layout(segments[2])
        elif len(segments) == 4 and segments[-1] == "scatter":
            return project_scatter.layout(segments[-2])
        elif len(segments) == 5 and segments[3] == "combination":
            return combinations.layout(segments[2], segments[4])
    elif isinstance(pathname, str) and pathname.startswith('/matrix'):
        segments = pathname.split("/")
        return matrix.layout(*segments[2:])
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True, port=8080, host='0.0.0.0')
