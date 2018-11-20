import dash_html_components as html
import dash_core_components as dcc

from db import session

from models import MatrixResult
from components.matrix_intro import layout as intro
from components.matrix_table import layout as table
from components.matrix_viability import layout as viability
from components.matrix_synergy import layout as synergy


def layout(barcode=None, cmatrix=None):
    my_matrix = session.query(MatrixResult) \
        .filter_by(barcode=barcode, cmatrix=cmatrix).one()

    return html.Div([
        dcc.Location(id='matrix-url', refresh=True),
        intro(my_matrix),
        viability(my_matrix),
        synergy(my_matrix),
        # table(my_matrix)
    ])