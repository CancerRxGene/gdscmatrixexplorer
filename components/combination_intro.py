import dash_html_components as html
import dash_core_components as dcc


def layout(combination):

    single_agent_curves = combination.matrices[0].single_agent_curves

    if single_agent_curves[0].lib1_id == combination.lib1_id:
        lib1_minc, lib1_maxc = single_agent_curves[0].minc, single_agent_curves[0].maxc
        lib2_minc, lib2_maxc = single_agent_curves[1].minc, single_agent_curves[1].maxc
    else:
        lib2_minc, lib2_maxc = single_agent_curves[0].minc, single_agent_curves[0].maxc
        lib1_minc, lib1_maxc = single_agent_curves[1].minc, single_agent_curves[1].maxc


    lib1_minc = '{:.3e}'.format(lib1_minc)
    lib2_minc = '{:.3e}'.format(lib2_minc)
    lib1_maxc = '{:.3e}'.format(lib1_maxc)
    lib2_maxc = '{:.3e}'.format(lib2_maxc)

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
                        ])
                    ])
                ])
            ])
        ]
    )
