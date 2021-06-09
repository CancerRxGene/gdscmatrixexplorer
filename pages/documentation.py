from components.matrix_doc import layout as matrix_doc
from components.anchor_doc import layout as anchor_doc
import dash_html_components as html
import dash_bootstrap_components as dbc
from components.breadcrumbs import breadcrumb_generator as crumbs

def layout(*args, **kwargs):
    return html.Div([
        crumbs([("Home", "/"),("/documentation",)]),
       # matrix_doc(),
        anchor_doc()
    ])
