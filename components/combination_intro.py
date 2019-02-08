import dash_bootstrap_components as dbc
import dash_html_components as html

from components.navigation.dropdowns import model_links_from_combo


def layout(combination):

    single_agent_curves = combination.matrices[0].single_agent_curves

    if single_agent_curves[0].drug_id_lib == combination.lib1_id:
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
            dbc.Row(className="mt-5 mb-3", children=
                dbc.Col(width=12, children=[
                    html.H1([
                        html.Strong(f"{combination.lib1.drug_name}"), " + ",
                        html.Strong(f"{combination.lib2.drug_name}")
                    ]),
                    html.P("Combination Report", className='lead')
                ])
            ),
            dbc.Row([
                dbc.Col(width=6, children=[
                    html.Div(className="bg-white pt-3 px-4 pb-2 mb-3 border border-info shadow-sm", children=[
                        html.H3("Drug information"),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(width=6, children=
                                dbc.Table(borderless=True, size='sm', children=[
                                    html.Tr([
                                        html.Td(html.Strong("Name")),
                                        html.Td(combination.lib1.drug_name)
                                    ]),
                                    html.Tr([
                                        html.Td(html.Strong("Target")),
                                        html.Td(combination.lib1.target)
                                    ]),
                                    html.Tr([
                                        html.Td(html.Strong("ID")),
                                        html.Td(combination.lib1.id)
                                    ]),
                                    html.Tr([
                                        html.Td(html.Strong("Owner")),
                                        html.Td(combination.lib1.owner)
                                    ]),
                                    html.Tr([
                                        html.Td(html.Strong("Min. conc.")),
                                        html.Td(f"{lib1_minc} µM")
                                    ]),
                                    html.Tr([
                                        html.Td(html.Strong("Max. conc.")),
                                        html.Td(f"{lib1_maxc} µM")
                                    ])
                                ])
                            ),
                            dbc.Col(width=6, children=
                                dbc.Table(borderless=True, size='sm', children=[
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
                                ])
                            )
                        ])
                    ])
                ]),
                dbc.Col(
                    width=6,
                    className='d-print-none',
                    children=
                    html.Div(
                        className="bg-white pt-3 px-4 pb-2 mb-3 border border-warning shadow-sm",
                        children=[
                            html.H3("View combination in cell line"),
                            html.Hr(),
                            dbc.Row(
                                className="pb-4",
                                children=dbc.Col(
                                    width=12,
                                    children=model_links_from_combo(combination)
                                ),
                            )
                        ],
                    )
                )
            ])
        ]
    )
