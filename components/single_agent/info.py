import numpy as np
import dash_html_components as html


def infoblock(drug):

    return html.Div([
        html.H3([
            "Drug ",
            html.Strong(drug.drug_name)
        ]),
        html.Table(
            html.Tr([
                html.Td([
                    html.Strong("Target "), drug.target
                ], className="pl-0"),
                html.Td([
                    html.Strong("Drug ID "), drug.id
                ]),
                html.Td([
                    html.Strong("Owner "), drug.owner
                ])
            ]),
            className="table"
        )
    ])