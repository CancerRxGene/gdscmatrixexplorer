import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash.dependencies
import plotly.figure_factory as ff
import sqlalchemy as sa

from app import app
from models import Combination
from utils import url_is_combination_page, get_project_metrics, \
    get_project_from_url, get_combination_results_with_sa, matrix_metrics


def get_drug_ids_from_url(url):
    segments = url.split("/")
    if len(segments) < 5:
        return None, None
    drug_ids = segments[4]
    drug1_id, drug2_id = drug_ids.split("+")

    return int(drug1_id), int(drug2_id)


def get_combination(project_id, lib1_id, lib2_id):
    try:
        combination = Combination.get(project_id, lib1_id, lib2_id)
    except sa.orm.exc.NoResultFound:
        return html.Div("Combination not found")
    except sa.orm.exc.MultipleResultsFound:
        return html.Div("Multiple results found for this combination - cannot display")

    return combination


def get_plot_data_from_url(url):
    project = get_project_from_url(url)
    drug1_id, drug2_id = get_drug_ids_from_url(url)
    combination = get_combination(project.id, drug1_id, drug2_id)
    plot_data = get_combination_results_with_sa(combination)
    return plot_data


def get_project_metrics_from_url(url, metric):
    project = get_project_from_url(url)
    return get_project_metrics(project.id, metric)


def layout():
    return html.Div(className='border bg-white pt-3 px-4 pb-3 mb-3', children=[
        html.H3("Combination Interaction"),
        html.Hr(),
        html.Div(className='row',
                 children=[
                     html.Div(className='col-5',
                              children=[
                                  dcc.Dropdown(
                                      options=list(matrix_metrics.values()),
                                      value='HSA_excess',
                                      id='combo-page-color-scale-select',
                                      clearable=False
                                  ),
                                  dcc.Graph(
                                      id='intxn-distn',
                                      config={
                                          'displayModeBar': False
                                      }
                                  )
                              ],
                              style={'width': '20%', 'float': 'left'}
                              ),
                     html.Div(className='col-7',
                              children=[
                                  dcc.Graph(
                                      id='combo-page-mm-scatter'
                                  )
                              ],
                              style={'width': '100%', 'float': 'left'}
                              )
                 ]),
        html.Div(className='row pt-5 pb-5', children=[
            html.Div(className='col-12', children=[
                dcc.Graph(id='combo-tissue')
            ])
        ])

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
        data=[ go.Box(
            name=plot_data.query("tissue == @tissue").tissue.unique()[0],
            y=plot_data.query("tissue == @tissue")[colorscale_select],
            boxpoints="all",
            hoverinfo="all",
            hoveron="points",
            jitter=0.3,
            marker={
                'size': 8
            }
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
    dash.dependencies.Output('url', 'pathname'),
    [dash.dependencies.Input('combo-page-mm-scatter', 'clickData')])
def go_to_dot(clicked_points):
    print("Click!")
    if clicked_points:
        p = clicked_points['points'][0]['customdata']
        print(p)
        return f"/matrix/{p[0]}/{p[1]}"
