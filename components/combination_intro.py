import dash_html_components as html
import dash_core_components as dcc


def layout(combination, conc_ranges):

    lib1_minc = conc_ranges.query('drug_id == @combination.lib1_id').minc.item()
    lib2_minc = conc_ranges.query('drug_id == @combination.lib2_id').minc.item()

    lib1_maxc = conc_ranges.query('drug_id == @combination.lib1_id').maxc.item()
    lib2_maxc = conc_ranges.query('drug_id == @combination.lib2_id').maxc.item()

    lib1_minc = '{:.3e}'.format(lib1_minc)
    lib2_minc = '{:.3e}'.format(lib2_minc)
    lib1_maxc = '{:.3e}'.format(lib1_maxc)
    lib2_maxc = '{:.3e}'.format(lib2_maxc)

    print(lib1_minc)
    print(lib2_minc)
    print(lib1_maxc)
    print(lib2_maxc)

    return html.Div(
        children=[
            html.Div(className="row mt-5 mb-3", children=[
                html.Div(className="col-12", children=[
                    dcc.Markdown(f"# **{combination.lib1.drug_name}** + **{combination.lib2.drug_name}** "),
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
                                        html.Td(combination.lib1.drug_name)
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Target")),
                                        html.Td(combination.lib1.target)
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("ID")),
                                        html.Td(combination.lib1.id)
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Owner")),
                                        html.Td(combination.lib1.owner)
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Min. conc.")),
                                        html.Td(f"{lib1_minc} µM")
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Max. conc.")),
                                        html.Td(f"{lib1_maxc} µM")
                                    ])
                                ], className="table-borderless")
                            ]),
                            html.Div(className="col-3", children=[
                                # html.H2(drug2.drug_name),
                                html.Table(children=[
                                    html.Tr([
                                        html.Td([html.Strong("Name")]),
                                        html.Td([combination.lib2.drug_name])
                                    ]),
                                    html.Tr([
                                        html.Td([html.Strong("Target")]),
                                        html.Td([combination.lib2.target])
                                    ]),
                                    html.Tr([
                                        html.Td([html.Strong("ID")]),
                                        html.Td(combination.lib2.id)
                                    ]),
                                    html.Tr([
                                        html.Td([html.Strong("Owner")]),
                                        html.Td(combination.lib2.owner)
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Min. conc.")),
                                        html.Td(f"{lib2_minc} µM")
                                    ]),
                                    html.Tr(children=[
                                        html.Td(html.Strong("Max. conc.")),
                                        html.Td(f"{lib2_maxc} µM")
                                    ])
                                ], className="table-borderless")
                            ]),
                            html.Div(className="col-3", children=[
                                # html.Table(children=[
                                #     html.Tr([
                                #         html.Td(html.Strong("Drugset")),
                                #         html.Td(combination.drugset_id)
                                #     ]),
                                #     html.Tr([
                                #         html.Td([html.Strong("Matrix id")]),
                                #         html.Td(combination.cmatrix)
                                #     ]),
                                #     html.Tr([
                                #         html.Td([html.Strong("Matrix size")]),
                                #         html.Td(combination.matrix_size)
                                #     ])
                                # ], className="table-borderless")
                            ])
                        ])
                    ])
                ])
            ])
        ]
    )
