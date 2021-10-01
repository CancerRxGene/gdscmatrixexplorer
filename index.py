import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output
import dash_auth
import os

from app import app
from components.navigation.header import generate_header
from components.navigation.footer import footer
from pages import project, home, matrix, combinations, documentation, downloads, volcano
from utils import url_parser

user = os.getenv('MATRIXEXPLORER_USER')
password = os.getenv('MATRIXEXPLORER_PASSWD')
# user = ''
# password = ''

auth = dash_auth.BasicAuth(app, [[user, password]])

app.layout = html.Div([
        # dcc.Location(id='url', refresh=True),
        dcc.Location(id='url', refresh=False),
        generate_header(),
        dbc.Container(
            id='wrapper',
            children=[
                dbc.Row(dbc.Col(id='page-content', width=12))
            ],
            className='pb-5'
        ),
        footer
])

server = app.server

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print('page path:' + pathname)
    if pathname is None:
        return ""

    page_type = url_parser(pathname)
    print('page type: ' + page_type)
    if page_type == 'home':
        return home.layout(pathname)
    elif page_type == 'project':
        return project.layout(pathname)
    elif page_type == 'combination':
        return combinations.layout(pathname)
    elif page_type == 'matrix':
        return matrix.layout(pathname)
    elif page_type == 'documentation':
        return documentation.layout(pathname)
    elif page_type == 'downloads':
        return downloads.layout(pathname)
    elif page_type == 'volcano':
        return volcano.layout()

    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(debug=False)
