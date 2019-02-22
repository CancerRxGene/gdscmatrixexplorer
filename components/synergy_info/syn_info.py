from functools import lru_cache

import dash_html_components as html

from utils import get_combination_matrices_summary


def get_badge_classname(value, context, metric):
    if value < context.loc["33%", metric]:
        return 'badge-danger'
    elif value < context.loc["50%", metric]:
        return 'badge-warning'
    else:
        return 'badge-success'


@lru_cache()
def get_context(matrix):
    return get_combination_matrices_summary(
        matrix.project_id, matrix.lib1_id, matrix.lib2_id,
        percentiles=(0.33, 0.67))


def get_pill(matrix, metric):
    context = get_context(matrix)
    value = getattr(matrix, metric)
    if value is None:
        return ''
    value = round(value, 3)
    badge_cls = get_badge_classname(value, context, metric)
    return html.Span(f"{value}", className="badge badge-pill " + badge_cls)


def infoblock_matrix(matrix_result):

    return html.Div([
        html.Div(className='card mb-3 matrix-metric', children=[
            html.Div(className='card-body', children=[
                html.H4(className='card-title', children=[
                    "MaxE"
                ]),
                html.P(className='card-text', children=[
                    "Color indicates combination percentile bracket",
                    html.Br(),
                    html.Strong("Top 33% ", className='badge badge-success'),
                    html.Span(" "),
                    html.Strong("Middle 33% ", className='badge badge-warning'),
                    html.Span(" "),
                    html.Strong("Bottom 33% ", className='badge badge-danger'),
                    html.Span(" "),
                ])
            ]),
            html.Ul(className='list-group list-group-flush', children=[
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Strong("Combination"),
                        get_pill(matrix_result, 'combo_maxe')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span(f"{matrix_result.combination.lib1.name}"),
                        get_pill(matrix_result, 'lib1_maxe')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span(
                            f"∆ {matrix_result.combination.lib1.name}"),
                        get_pill(matrix_result, 'delta_maxe_lib1')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span(f"{matrix_result.combination.lib2.name}"),
                        get_pill(matrix_result, 'lib2_maxe')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span(
                            f"∆ {matrix_result.combination.lib2.name}"),
                        get_pill(matrix_result, 'delta_maxe_lib2')
                    ]),
            ])
        ]),
        html.Div(className='card mb-3 matrix-metric', children=[
            html.Div(className='card-body', children=[
                html.H4(className='card-title', children=[
                    "Bliss Excess"
                ])
            ]),
            html.Ul(className='list-group list-group-flush', children=[
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Matrix average"),
                    get_pill(matrix_result, 'bliss_matrix')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Matrix average synergistic wells"),
                    get_pill(matrix_result, 'bliss_matrix_so')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Highest window"),
                    get_pill(matrix_result, 'bliss_window')
                ]),
                html.Li(className='list-group-item d-flex justify-content-between align-items-center', children=[
                    html.Span("Highest window synergistic wells"),
                    get_pill(matrix_result, 'bliss_window_so')
                ])
            ])
        ]),
        html.Div(className='card mb-3 matrix-metric', children=[
            html.Div(className='card-body', children=[
                html.H4(className='card-title', children=[
                    "HSA Excess"
                ]),
            ]),
            html.Ul(className='list-group list-group-flush', children=[
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Matrix average"),
                        get_pill(matrix_result, 'hsa_matrix')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Matrix average synergistic wells"),
                        get_pill(matrix_result, 'hsa_matrix_so')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Highest window"),
                        get_pill(matrix_result, 'hsa_window')
                    ]),
                html.Li(
                    className='list-group-item d-flex justify-content-between align-items-center',
                    children=[
                        html.Span("Highest window synergistic wells"),
                        get_pill(matrix_result, 'hsa_window_so')
                    ])
            ])
        ])
    ])
