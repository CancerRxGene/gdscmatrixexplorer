import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table_experiments as dt

from app import app
from pages import level1_1, level1_2, home, matrix, dr_single_agent
from page_components import header

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(
        id='wrapper',
        className="container-fluid",
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
        return home.layout
    elif pathname == '/GDSC_007-A':
        return level1_2.layout
    elif pathname == '/GDSC_007-A/free_scatter':
        return level1_1.layout
    elif pathname == '/GDSC_007-A/dose_response':
        return dr_single_agent.layout
    elif isinstance(pathname, str) and pathname.startswith('/GDSC_007-A/matrix'):
        segments = pathname.split("/")
        return matrix.layout(*segments[3:])
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)