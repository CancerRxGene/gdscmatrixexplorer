import dash_html_components as html
import dash_core_components as dcc
import requests

from app import app


def layout(drug1, drug2, combo_details):
    return (
        html.Div(className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                 children=[
            # html.Div(className="row", children=[
            #     html.Div(className="col-12", children=[
            #         html.H2(f"{drug1.drug_name} + {drug2.drug_name}")
            #     ])
            # ]),
            html.Div(className="row", children=[
                html.Div(className="col-3", children=[
                    html.H2(f"{drug1.drug_name}"),
                    html.Table(children=[
                        html.Tr(children=[
                            html.Td(html.Strong("Target")),
                            html.Td(drug1.target)
                        ]),
                        html.Tr(children=[
                            html.Td(html.Strong("ID")),
                            html.Td(drug1.id)
                        ]),
                        html.Tr(children=[
                            html.Td(html.Strong("Owner")),
                            html.Td(drug1.owner)
                        ])
                    ], className="table-borderless")
                ]),
                html.Div(className="col-3", children=[
                    html.H2(drug2.drug_name),
                    html.Table(children=[
                        html.Tr([
                            html.Td([html.Strong("Target")]),
                            html.Td([drug2.target])
                        ]),
                        html.Tr([
                            html.Td([html.Strong("ID")]),
                            html.Td(drug2.id)
                        ]),
                        html.Tr([
                            html.Td([html.Strong("Owner")]),
                            html.Td(drug2.owner)
                        ])
                    ], className="table-borderless")
                ]),
                html.Div(className="col-3", children=[
                    html.Br(),
                    html.Br(),
                    html.Table(children=[
                        html.Tr([
                            html.Td(html.Strong("Drugset")),
                            html.Td(combo_details.drugset_id)
                        ]),
                        html.Tr([
                            html.Td([html.Strong("Matrix id")]),
                            html.Td(combo_details.cmatrix)
                        ]),
                        html.Tr([
                            html.Td([html.Strong("Matrix size")]),
                            html.Td(combo_details.matrix_size)
                        ])
                    ], className="table-borderless")
                ])
            ])
        ])
    )




if __name__ == '__main__':
    app.run_server(debug=True)