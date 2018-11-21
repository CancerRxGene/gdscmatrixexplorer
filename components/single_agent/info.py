import numpy as np
import dash_html_components as html


def infoblock(drug):

    return html.Div([
        html.H3([
            html.Strong(drug.drug_name),
            html.Span(f" ({drug.target})")
        ]),
        html.P("Monotherapy response"),
        html.Hr()
    ])