import dash_html_components as html

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
        intro(my_matrix),
        viability(my_matrix),
        synergy(my_matrix),
        table(my_matrix)
    ])