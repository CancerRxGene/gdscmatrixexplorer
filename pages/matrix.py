import dash_html_components as html
import dash_core_components as dcc

from models import MatrixResult
from components.matrix_intro import layout as intro
from components.matrix_viability import layout as viability
from components.matrix_synergy import layout as synergy
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_matrix_from_url


def layout(url):

    my_matrix = get_matrix_from_url(url)
    if not isinstance(my_matrix, MatrixResult):
        return my_matrix

    p = my_matrix.project
    c = my_matrix.combination

    return html.Div([
        dcc.Location(id='matrix-url', refresh=True),
        crumbs([("Home", "/"), (p.name, f"/project/{p.slug}"),
                (f"{c.lib1.drug_name} + {c.lib2.drug_name}", f"/project/{p.slug}/combination/{c.lib1_id}+{c.lib2_id}"),
                (f"{my_matrix.model.name}",)]),
        intro(my_matrix),
        viability(my_matrix),
        synergy(my_matrix),
        # table(my_matrix)
    ])