import numpy as np
import dash_html_components as html


def infoblock_matrix(matrix_result):
    return html.Div([
        html.Div([
            html.H5(["Maximum inhibitory effect"]),
            html.Table([
                html.Tbody([
                    html.Tr([
                        html.Td([html.Strong("Combination")]),
                        html.Td([round(matrix_result.combo_max_effect, 3)])
                    ], className="colspan-2"),
                    html.Tr([
                        html.Td([html.Strong("lib1 max effect")]),
                        html.Td([round(matrix_result.lib1_max_effect, 3)])
                    ]),
                    html.Tr([
                        html.Td([html.Strong("lib2 max effect")]),
                        html.Td([round(matrix_result.lib2_max_effect, 3)])
                    ])
                ])
                # html.Strong("lib1_delta_max_effect"), round(matrix_result.lib1_delta_max_effect, 3), html.Br(),
                #  html.Strong("lib2_delta_max_effect"), round(matrix_result.lib2_delta_max_effect, 3), html.Br()
            ], className="table-borderless")
        ], className="pb-2"),
        html.Div([
            html.H5(["Highest single agent effect (HSA)"]),
            html.Table([
                html.Tr([
                    html.Td([html.Strong("Matrix average excess ")]),
                    html.Td([html.Span(round(matrix_result.HSA_excess, 3), className="text-left")]),
                ]),
                html.Tr([
                    html.Td([html.Strong(f"Average in {matrix_result.HSA_excess_well_count} wells with excess > 0")]),
                    html.Td([html.Span(round(matrix_result.HSA_excess_syn, 3))])
                ]) if matrix_result.HSA_excess_syn else ''
            ])
        ], className="pb-2"),
        html.Div([
            html.H5(["Bliss additivity"]),
            html.Table([
                html.Tr([
                    html.Td([html.Strong("Matrix average excess ")]),
                    html.Td([html.Span(round(matrix_result.Bliss_excess, 3))])
                ]),
                html.Tr([
                    html.Td([html.Span(
                        html.Strong(f"Average in {matrix_result.Bliss_excess_well_count} wells with excess > 0"))]),
                    html.Td([html.Span(round(matrix_result.Bliss_excess_syn, 3))])
                ]) if matrix_result.Bliss_excess_syn else ''
            ])
        ], className="pl-0, pb-2"),

        html.Hr(),
        html.Div([
            html.H6("Best scoring windows in matrix"),
            html.Table([
                html.Tr([
                    html.Td([
                        html.Strong("Window size "), matrix_result.window_size, html.Br(),
                        html.Strong("HSA excess"), round(matrix_result.HSA_excess_window, 3), html.Br(),
                        html.Strong("HSA dose lib1 "), matrix_result.HSA_excess_window_dose_lib1,
                        html.Br(),
                        html.Strong("HSA dose lib2 "), matrix_result.HSA_excess_window_dose_lib2,
                        html.Br(),
                        html.Strong("HSA with excess > 0  "), round(matrix_result.HSA_excess_window_syn, 3), html.Br(),
                        html.Strong("dose lib1 "), matrix_result.HSA_excess_window_syn_dose_lib1,
                        html.Br(),
                        html.Strong("dose lib2 "), matrix_result.HSA_excess_window_syn_dose_lib2,
                        html.Br(),
                        html.Strong("Bliss excess  "), round(matrix_result.Bliss_excess_window, 3), html.Br(),
                        html.Strong("dose lib1 "), matrix_result.Bliss_excess_window_dose_lib1,
                        html.Br(),
                        html.Strong("dose lib2 "), matrix_result.Bliss_excess_window_dose_lib2,
                        html.Br(),
                        html.Strong("Bliss with excess > 0"), round(matrix_result.Bliss_excess_window_syn, 3),
                        html.Br(),
                        html.Strong("dose lib1"),
                        matrix_result.Bliss_excess_window_syn_dose_lib1, html.Br(),
                        html.Strong("dose lib2"),
                        matrix_result.Bliss_excess_window_syn_dose_lib2, html.Br()
                    ], className="pl-0")

                ])
            ])
        ])

    ])


    #
    # ], className="flex-grow-1")
