import dash_html_components as html
import dash_core_components as dcc
import requests

from app import app


def layout(drug1, drug2, combo_details):
    return html.Div(
        children=[
            html.Div(className="row mt-5 mb-3", children=[
                html.Div(className="col-12", children=[
                    dcc.Markdown(f"# **{drug1.drug_name}** + **{drug2.drug_name}** "),
                    html.P("Combination Report", className='lead')
                ])
            ]),
            html.Div(className="row", children=[
                html.Div(className="col-12", children=[
                    html.Div(className="bg-white p-2 my-2 border border-warning ", children=[
                        html.Div(className="row pb-4", children=[
                            html.Div(className="col-3", children=[
                                # html.H2(f"{drug1.drug_name}"),
                                html.Table(children=[
                                    html.Tr(children=[
                                        html.Td(html.Strong("Name")),
                                        html.Td(drug1.drug_name)
                                    ]),
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
                                # html.H2(drug2.drug_name),
                                html.Table(children=[
                                    html.Tr([
                                        html.Td([html.Strong("Name")]),
                                        html.Td([drug2.drug_name])
                                    ]),
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
                ])
            ])
        ]
    )




if __name__ == '__main__':
    app.run_server(debug=True)