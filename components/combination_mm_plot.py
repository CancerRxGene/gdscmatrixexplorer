import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash.dependencies
import plotly.figure_factory as ff

from app import app
from utils import url_is_combination_page, get_project_metrics, \
    get_project_from_url, get_combination_results_with_sa, matrix_metrics, \
    get_combination_from_url, matrix_hover_label


def get_plot_data_from_url(url):
    combination = get_combination_from_url(url)
    plot_data = get_combination_results_with_sa(combination)
    return plot_data


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
                dcc.Graph(
                  id='intxn-distn',
                  config={
                      'displayModeBar': False
                  }
                )
            ]),
            dbc.Col(dcc.Graph(id='combo-page-mm-scatter'), width=7)
         ]),
        dbc.Row(
            dbc.Col(dcc.Graph(id='combo-tissue'), width=12, className='py-5')
        )
    ])


@app.callback(
    dash.dependencies.Output('intxn-distn', 'figure'),
    [dash.dependencies.Input('url', 'pathname'),
     dash.dependencies.Input('combo-page-color-scale-select', 'value')])
def update_distn(pathname, colorscale_select):
    if not url_is_combination_page(pathname):
        return None
    plot_data = get_plot_data_from_url(pathname)
    project_metrics = get_project_metrics_from_url(pathname, colorscale_select)

    drug1 = plot_data['lib1_name'].unique()
    drug2 = plot_data['lib2_name'].unique()

    figure = ff.create_distplot([plot_data[colorscale_select].dropna(), project_metrics[colorscale_select].dropna()],
                       group_labels=[f"{drug1[0]}+{drug2[0]}", "All combinations"],
                       show_rug=False,
                       bin_size=round(
                           (project_metrics[colorscale_select].dropna().max() -
                            project_metrics[colorscale_select].dropna().min()) / 20,
                           2)
                       )

    return figure

@app.callback(
    dash.dependencies.Output('combo-page-mm-scatter', 'figure'),
    [dash.dependencies.Input('url', 'pathname'),
     dash.dependencies.Input('combo-page-color-scale-select', 'value')])
def update_scatter(pathname, colorscale_select):
    if not url_is_combination_page(pathname):
        return None
    plot_data = get_plot_data_from_url(pathname)
    project_metrics = get_project_metrics_from_url(pathname, colorscale_select)

    drug1 = plot_data['lib1_name'].unique()
    drug2 = plot_data['lib2_name'].unique()

    # Set colorscale using whole project dataset
    color_min = project_metrics[colorscale_select].min()
    color_max = project_metrics[colorscale_select].max()
    color_zero = abs(0 - color_min / (color_max - color_min))

    return go.Figure({
        'data': [go.Scatter(
            x=plot_data['ic50_lib1'],
            y=plot_data['ic50_lib2'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 8,
                'color': plot_data[colorscale_select],
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
            'title': matrix_metrics[colorscale_select]['description'],
            'xaxis': {'title': f"{drug1[0]} IC50 log µM"},
            'yaxis': {'title': f"{drug2[0]} IC50 log µM"}
        }
    })


@app.callback(
    dash.dependencies.Output('combo-tissue', 'figure'),
    [dash.dependencies.Input('url', 'pathname'),
     dash.dependencies.Input('combo-page-color-scale-select', 'value')
     ])
def update_tissue_plot(url, colorscale_select):
    if not url_is_combination_page(url):
        return None
    plot_data = get_plot_data_from_url(url)

    return go.Figure(
        data=[go.Box(
            name=plot_data.query("tissue == @tissue").tissue.unique()[0],
            y=plot_data.query("tissue == @tissue")[colorscale_select],
            boxpoints="all",
            hoverinfo="y+text",
            hoveron="points",
            jitter=0.3,
            marker={
                'size': 8
            },
            text=matrix_hover_label(plot_data),
            customdata=[(row.barcode, row.cmatrix) for row in
                        plot_data.itertuples(index=False)]
        ) for tissue in plot_data[['tissue', colorscale_select]].
            groupby(by='tissue', as_index=False)
            .median()
            .sort_values(by=colorscale_select, ascending=False)
            .tissue
        ],
        layout= {
            'title': 'Combination interaction effects by tissue type',
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
