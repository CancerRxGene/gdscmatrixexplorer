import numpy as np
import dash_html_components as html


def infoblock(drug):

    return html.Div([
        html.H3([
            "Drug ",
            html.Strong(drug.drug_name),
            " (single agent)"
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

def infoblock_curve(drug, curve):

    return html.Div([
        html.H3([
            "Drug ",
            html.Strong(drug.drug_name),
            " (single agent)"
        ]),
        html.Table(
            html.Tr([
                html.Td([
                    html.Strong("Target "), drug.target, html.Br(),
                    html.Strong("Drug ID "), drug.id, html.Br(),
                    html.Strong("Owner "), drug.owner, html.Br(),
                ], className="pl-0"),
                html.Td([
                    html.Strong("IC50 "),
                    html.Span(round(np.exp(curve.ic50), 3)),
                    " µM",
                    html.Br(),
                    html.Strong("AUC "), html.Span(round(curve.auc, 3)),
                    html.Br(),
                    html.Strong("Emax "), html.Span(round(1 - curve.emax, 3)),
                    html.Br(),
                    html.Strong("RMSE "), html.Span(round(curve.rmse, 3)),
                    html.Br()
                ])

            ]),
            className="table"
        )
    ])