from components.matrix_doc import layout as matrix_doc
from components.anchor_doc import layout as anchor_doc
import dash_html_components as html
import dash_bootstrap_components as dbc
from components.breadcrumbs import breadcrumb_generator as crumbs

def layout(*args, **kwargs):
    return html.Div([
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    html.Div([
                        crumbs([("Home", "/"), ("/documentation",)]),
                       # html.H4(html.Strong("Documentation"), className='display-4 text-center my-4'),
                    ])
                )
            ),
            dbc.Row(children=[
                matrix_doc(),
                html.Br(),
                html.Br(),
                anchor_doc()
            #         dbc.Col(width=3,children=
            #                 dbc.Nav(
            #                     [
            #                         dbc.NavItem(dbc.NavLink("Matrix data", href="#matrix")),
            #                         dbc.NavItem(dbc.NavLink("Anchor data", href="#anchor"))
            #                     ],
            #                     vertical=True
            #                 )
            #                 ),
            #         dbc.Col(width=9,children=[
            #             dbc.Row(children=
            #                 dbc.Col([
            #                     matrix_doc(),
            #                     html.Br(),
            #                     html.Br()
            #                 ])
            #             ),
            #             dbc.Row(children=
            #                 dbc.Col(
            #                     anchor_doc()
            #                 )
            #             )
            #         ])
            ]
            )
        ])
    ])
