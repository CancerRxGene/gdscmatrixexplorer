from functools import lru_cache

import dash_html_components as html
import pandas as pd

from db import session


def get_badge_classname(value, context, metric):
    if value < context.loc["33%", metric]:
        return 'badge-primary'
    elif value < context.loc["50%", metric]:
        return 'badge-danger'
    else:
        return 'badge-success'


# This is only cached for an individual request as the 'matrix'-object is different for each request.
# A more elegant solution would cache the context for any combination
@lru_cache()
def get_context(matrix):
    return pd.read_sql(matrix.combination.matrices.statement,
                          session.get_bind()) \
        .describe(percentiles=[0.33, 0.67])


def get_pill(matrix, metric):
    context = get_context(matrix)
    value = round(getattr(matrix, metric), 3)
    badge_cls = get_badge_classname(value, context, metric)
    return html.Span(f"{value}", className="badge badge-pill " + badge_cls)


def infoblock_matrix(matrix_result):

    return html.Div([
        html.Div(className='card mb-3', children=[
            html.Div(className='card-body', children=[
                html.H4(className='card-title', children=[
                    "Bliss Excess"
                ]),
                html.P(className='card-text', children=[
                    "Color indicates percentile bracket for this combination", html.Br(),
                    html.Strong("Top 33% ", className='badge badge-success'), html.Span(" "),
                    html.Strong("Middle 33% ", className='badge badge-danger'), html.Span(" "),
                    html.Strong("Bottom 33% ", className='badge badge-primary'), html.Span(" "),
                ])
            ]),
            html.Ul(className='list-group list-group-flush', children=[
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Matrix average"),
                    get_pill(matrix_result, 'Bliss_excess')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Matrix average synergistic wells"),
                    get_pill(matrix_result, 'Bliss_excess_syn')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Highest window"),
                    get_pill(matrix_result, 'Bliss_excess_window')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Highest window synergistic wells"),
                    get_pill(matrix_result, 'Bliss_excess_window_syn')
                ])
            ])
        ]),
        html.Div(className='card mb-3', children=[
            html.Div(className='card-body', children=[
                html.H4(className='card-title', children=[
                    "HSA Excess"
                ]),
                html.P(className='card-text', children=[
                    "Average excess over the highest single agent in the matrix or 3x3 window."
                ])
            ]),
            html.Ul(className='list-group list-group-flush', children=[
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Matrix average"),
                        get_pill(matrix_result, 'HSA_excess')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Matrix average synergistic wells"),
                        get_pill(matrix_result, 'HSA_excess_syn')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Highest window"),
                        get_pill(matrix_result, 'HSA_excess_window')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Highest window synergistic wells"),
                        get_pill(matrix_result, 'HSA_excess_window_syn')
                    ])
            ])
        ])
    ])
    # return html.Div([
    #     html.Div([
    #         html.H5(["Maximum inhibitory effect"]),
    #         html.Table([
    #             html.Tbody([
    #                 html.Tr([
    #                     html.Td([html.Strong("Combination")]),
    #                     html.Td(f"{round(matrix_result.combo_max_effect * 100, 1)}% cell kill")
    #                 ], className="colspan-2"),
    #                 html.Tr([
    #                     html.Td([html.Strong("lib1 max effect")]),
    #                     html.Td(f"{round(matrix_result.lib1_max_effect * 100, 1)}% cell kill")
    #                 ]),
    #                 html.Tr([
    #                     html.Td([html.Strong("lib2 max effect")]),
    #                     html.Td(f"{round(matrix_result.lib2_max_effect * 100, 1)}% cell kill")
    #                 ])
    #             ])
    #             # html.Strong("lib1_delta_max_effect"), round(matrix_result.lib1_delta_max_effect, 3), html.Br(),
    #             #  html.Strong("lib2_delta_max_effect"), round(matrix_result.lib2_delta_max_effect, 3), html.Br()
    #         ], className="table-borderless")
    #     ], className="pb-4"),
    #     html.Div([
    #         html.H5(["Highest single agent effect (HSA)"]),
    #         html.Table([
    #             html.Tr([
    #                 html.Td([html.Strong("Matrix average excess ")]),
    #                 html.Td([html.Span(round(matrix_result.HSA_excess, 3), className="text-left")]),
    #             ]),
    #             html.Tr([
    #                 html.Td([html.Strong(f"Average in {matrix_result.HSA_excess_well_count} wells with excess > 0")]),
    #                 html.Td([html.Span(round(matrix_result.HSA_excess_syn, 3))])
    #             ]) if matrix_result.HSA_excess_syn else ''
    #         ])
    #     ], className="pb-4"),
    #     html.Div([
    #         html.H5(["Bliss additivity"]),
    #         html.Table([
    #             html.Tr([
    #                 html.Td([html.Strong("Matrix average excess ")]),
    #                 html.Td([html.Span(round(matrix_result.Bliss_excess, 3))])
    #             ]),
    #             html.Tr([
    #                 html.Td([html.Span(
    #                     html.Strong(f"Average in {matrix_result.Bliss_excess_well_count} wells with excess > 0"))]),
    #                 html.Td([html.Span(round(matrix_result.Bliss_excess_syn, 3))])
    #             ]) if matrix_result.Bliss_excess_syn else ''
    #         ])
    #     ], className="pl-0, pb-2"),
    #
    #     html.Hr(),
    #     html.Div([
    #         html.H6("Best scoring windows in matrix"),
    #         html.Table([
    #             html.Tr([
    #                 html.Td([
    #                     html.Strong("Window size "), matrix_result.window_size, html.Br(),
    #                     html.Strong("HSA excess "), round(matrix_result.HSA_excess_window, 3), html.Br(),
    #                     html.Strong("HSA dose lib1 "), matrix_result.HSA_excess_window_dose_lib1,
    #                     html.Br(),
    #                     html.Strong("HSA dose lib2 "), matrix_result.HSA_excess_window_dose_lib2,
    #                     html.Br(),
    #                     html.Strong("HSA with excess > 0  "), round(matrix_result.HSA_excess_window_syn, 3), html.Br(),
    #                     html.Strong("dose lib1 "), matrix_result.HSA_excess_window_syn_dose_lib1,
    #                     html.Br(),
    #                     html.Strong("dose lib2 "), matrix_result.HSA_excess_window_syn_dose_lib2,
    #                     html.Br(),
    #                     html.Strong("Bliss excess  "), round(matrix_result.Bliss_excess_window, 3), html.Br(),
    #                     html.Strong("dose lib1 "), matrix_result.Bliss_excess_window_dose_lib1,
    #                     html.Br(),
    #                     html.Strong("dose lib2 "), matrix_result.Bliss_excess_window_dose_lib2,
    #                     html.Br(),
    #                     html.Strong("Bliss with excess > 0"), round(matrix_result.Bliss_excess_window_syn, 3),
    #                     html.Br(),
    #                     html.Strong("dose lib1 "),
    #                     matrix_result.Bliss_excess_window_syn_dose_lib1, html.Br(),
    #                     html.Strong("dose lib2 "),
    #                     matrix_result.Bliss_excess_window_syn_dose_lib2, html.Br()
    #                 ], className="pl-0")
    #
    #             ])
    #         ])
    #     ])
    #
    # ])


    #
    # ], className="flex-grow-1")
