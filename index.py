import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app, cpr
from pages import project_scatter, project_home, home, matrix, combinations
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


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home.layout()
    elif pathname.startswith('/project'):
        segments = pathname.split("/")
        if len(segments) == 3:
            return project_home.layout(segments[2])
        elif len(segments) == 4 and segments[-1] == "scatter":
            return project_scatter.layout(segments[-2])
    elif isinstance(pathname, str) and pathname.startswith('/combination'):
        segments = pathname.split("/")
        return combinations.layout(segments[2])
    elif isinstance(pathname, str) and pathname.startswith('/matrix'):
        segments = pathname.split("/")
        return matrix.layout(*segments[2:])
    else:
        return '404'


@app.callback(
    Output('url', 'pathname'),
    [Input(plot_id, 'clickData') for plot_id in cpr.plot_ids()])
def go_to_dot(*args):
    print("Click!")
    print(args)
    clicked = next(x for x in args if x)
    if clicked:
        p = clicked['points'][0]['customdata']
        print(p)
        return p['to']
    else:
        return "/"


if __name__ == '__main__':
    app.run_server(debug=True)
