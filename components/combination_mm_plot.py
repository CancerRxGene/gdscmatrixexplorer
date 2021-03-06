from functools import lru_cache

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash.dependencies
import plotly.figure_factory as ff

from app import app
from utils import url_is_combination_page, get_project_metrics, \
    get_project_from_url, get_combination_results_with_sa, matrix_metrics, \
    get_combination_from_url, matrix_hover_label, get_all_tissues


@lru_cache(maxsize=128)
def get_plot_data_from_url(url):
    combination = get_combination_from_url(url)
    plot_data = get_combination_results_with_sa(combination)
    return plot_data


@lru_cache(maxsize=128)
def get_project_metrics_from_url(url, metric):
    project = get_project_from_url(url)
    return get_project_metrics(project.id, metric)


def layout():
    return html.Div(className='border bg-white pt-3 px-4 pb-3 mb-3 shadow-sm', children=[
        dcc.Location(id='mm-plot-url', refresh=True),
        html.H3("Combination Interaction"),
        html.Hr(),
        dbc.Row([
            dbc.Col(width=5, children=[
                dcc.Dropdown(
                  options=list(matrix_metrics.values()),
                  value='bliss_matrix',
                  id='combo-page-color-scale-select',
                  clearable=False
                ),
                dcc.Loading(className='gdsc-spinner', children=
                    dcc.Graph(
                      id='intxn-distn',
                      config={
                          'displayModeBar': False
                      }
                    )
                )
            ]),
            dbc.Col(dcc.Loading(className='gdsc-spinner', children=dcc.Graph(id='combo-page-mm-scatter')), width=7)
         ]),
        dbc.Row([
            dbc.Col(dcc.Loading(className='gdsc-spinner', children=dcc.Graph(id='combo-tissue')), width=12, className='py-5'),
            dbc.Col(width=4, children=[
                dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                    html.Label('Group by',
                               className="w-25 justify-content-start"),
                    dcc.Dropdown(
                        options=[
                            {'label': 'Tissue', 'value': 'tissue'},
                            {'label': 'Cancer Type', 'value': 'cancer_type'},
                        ],
                        id='grouping-select',
                        value='tissue',
                        clearable=False
                    )
                ]))
            ]),
            dbc.Col(width=4, children=[
                dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                    html.Label('Tissue filter', className="w-25 justify-content-start"),
                    dcc.Dropdown(
                        options=[{'label': c, 'value': c} for c in
                                 get_all_tissues()],
                        id='tissue-select',
                        multi=True,
                    ),
                ])),
            ]),
            dbc.Col(width=4, children=[
                dbc.Form(inline=True, className='mb-2', children=dbc.FormGroup([
                    html.Label('Hide groups smaller than',
                               className="w-50 justify-content-start"),
                    dcc.Dropdown(
                        options=[{'label': i, 'value': i} for i in [1, 2, 3, 4, 5, 10, 15, 20, 25]],
                        id='group-size-select',
                        value=5,
                        clearable=False,
                    )
                ]))
            ]),
        ])
    ])


@app.callback(
    [dash.dependencies.Output('intxn-distn', 'figure'),
     dash.dependencies.Output('combo-page-mm-scatter', 'figure')],
    [dash.dependencies.Input('combo-page-color-scale-select', 'value')],
    [dash.dependencies.State('url', 'pathname')])
@lru_cache(maxsize=1000)
def update_plots(colorscale_select, pathname):
    if not url_is_combination_page(pathname):
        return None
    plot_data = get_plot_data_from_url(pathname)
    project_metrics = get_project_metrics_from_url(pathname, colorscale_select)

    drug1_name = plot_data['lib1_name'].unique()[0]
    drug2_name = plot_data['lib2_name'].unique()[0]

    distplot = generate_distplot(project_metrics, plot_data, colorscale_select, drug1_name, drug2_name)
    mm_scatter = generate_mm_scatter(project_metrics, plot_data, colorscale_select, drug1_name, drug2_name)

    return distplot, mm_scatter


def generate_distplot(project_metrics, plot_data, plot_metric, drug1_name, drug2_name):

    figure = ff.create_distplot(
        [plot_data[plot_metric].dropna(), project_metrics[plot_metric].dropna()],
        group_labels=[f"{drug1_name} + {drug2_name}", "All combinations"],
        show_rug=False,
        bin_size=round(
           (project_metrics[plot_metric].dropna().max() -
            project_metrics[plot_metric].dropna().min()) / 20,
           2)
)

    return figure


def generate_mm_scatter(project_metrics, plot_data, plot_metric, drug1_name, drug2_name):

    # Set colorscale using whole project dataset
    color_min = project_metrics[plot_metric].min()
    color_max = project_metrics[plot_metric].max()
    color_zero = abs(0 - color_min / (color_max - color_min))

    return go.Figure({
        'data': [go.Scatter(
            x=plot_data['ic50_lib1'],
            y=plot_data['ic50_lib2'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 8,
                'color': plot_data[plot_metric],
                'colorscale': [
                    [0, 'rgb(0, 0, 255)'],
                    [color_zero, 'rgb(255, 255, 255)'],
                    [1.0, 'rgb(255, 0, 0)']],
                'cmin': color_min,
                'cmax': color_max,
                'cauto': False,
                'showscale': True
            },
            text=matrix_hover_label(plot_data),
            hoverinfo='text',
            customdata=[(row.barcode, row.cmatrix) for row in plot_data.itertuples(index=False)]
        )
        ],
        'layout': {
            'title': matrix_metrics[plot_metric]['description'],
            'xaxis': {'title': f"{drug1_name} IC50 log µM"},
            'yaxis': {'title': f"{drug2_name} IC50 log µM"}
        }
    })


@app.callback(
    dash.dependencies.Output('combo-tissue', 'figure'),
    [
        dash.dependencies.Input('combo-page-color-scale-select', 'value'),
        dash.dependencies.Input('grouping-select', 'value'),
        dash.dependencies.Input('tissue-select', 'value'),
        dash.dependencies.Input('group-size-select', 'value'),
    ],
    [dash.dependencies.State('url', 'pathname')])
def update_combo_boxplot(colorscale_select, grouping_select, tissue_select, min_group_size, pathname):
    if not url_is_combination_page(pathname):
        return None

    if isinstance(tissue_select, list):
        tissue_select = tuple(tissue_select)

    return generate_combo_tissues(colorscale_select, grouping_select, tissue_select, min_group_size, pathname)


@lru_cache(maxsize=1000)
def generate_combo_tissues(colorscale_select, grouping_select, tissue_select, min_group_size, pathname):

    plot_data = get_plot_data_from_url(pathname)

    if tissue_select:
        plot_data = plot_data[plot_data.tissue.isin(tissue_select)]

    combo_tissues = generate_combo_tissue_plot(
        plot_data, colorscale_select, grouping_select, min_group_size
    )
    return combo_tissues


def generate_combo_tissue_plot(plot_data, plot_metric, grouping_var, min_group_size):

    boxes = []

    groups = (plot_data[[grouping_var, plot_metric]]
              .groupby(by=grouping_var, as_index=False)
              .median()
              .sort_values(by=plot_metric, ascending=False))[grouping_var]


    for group in groups:
        box_data = plot_data[plot_data[grouping_var] == group]
        if len(box_data.model_id.unique()) < min_group_size:
            continue
        boxes.append(
            go.Box(
                name=group,
                y=box_data[plot_metric],
                boxpoints="all",
                hoverinfo="y+text",
                hoveron="points",
                jitter=0.3,
                marker={
                    'size': 8
                },
                text=matrix_hover_label(box_data),
                customdata=[(row.barcode, row.cmatrix) for row in
                            box_data.itertuples(index=False)]
            )
        )

    return go.Figure(
        data=boxes,
        layout={
            'title': f'Combination interaction effects by {grouping_var}'.replace("_", " "),
            'showlegend': False
        }
    )


@app.callback(
    dash.dependencies.Output('mm-plot-url', 'pathname'),
    [dash.dependencies.Input('combo-page-mm-scatter', 'clickData'),
     dash.dependencies.Input('combo-tissue', 'clickData')])
def go_to_dot(p1, p2):
    clicked_points = p1 or p2
    if clicked_points:
        p = clicked_points['points'][0]['customdata']
        return f"/matrix/{p[0]}/{p[1]}"
