import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash.dependencies
import pandas as pd
import plotly.figure_factory as ff

from app import app


def layout(plot_data=None, project_metrics=None):
    dropdown_options = [
        {'label': 'Bliss excess', 'value': 'Bliss_excess'},
        {'label': 'Bliss excess synergy only', 'value': 'Bliss_excess_syn'},
        {'label': 'Bliss excess 3x3', 'value': 'Bliss_excess_window'},
        {'label': 'Bliss excess 3x3 synergy only', 'value': 'Bliss_excess_window_syn'},
        {'label': 'HSA excess', 'value': 'HSA_excess'},
        {'label': 'HSA excess synergy only', 'value': 'HSA_excess_syn'},
        {'label': 'HSA excess 3x3', 'value': 'HSA_excess_window'},
        {'label': 'HSA excess 3x3 synergy only', 'value': 'HSA_excess_window_syn'},
        {'label': 'Combo max. inhibition', 'value': 'combo_max_effect'},
        {'label': 'lib1 max. inhibition', 'value': 'lib1_max_effect'},
        {'label': 'lib2 max. inhibition', 'value': 'lib2_max_effect'}
    ]

    return html.Div(className='border bg-white p-2 my-2', children=[
        dcc.Location(id='combo-url', refresh=True),
        html.Div(className='row',
                 children=[
                     html.Div(className='col-5',
                              children=[
                                  html.Label('Combination interaction'),
                                  dcc.Dropdown(
                                      options=dropdown_options,
                                      value='HSA_excess',
                                      id='color-scale-select',
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
                                      id='mm-scatter'
                                  )
                              ],
                              style={'width': '100%', 'float': 'left'}
                              )
                 ]),
        html.Div(className='row pt-5 pb-5', children=[
            html.Div(className='col-12', children=[
                dcc.Graph(id='combo-tissue')
            ])
        ]),
        html.Div(style={"display": "none"},
                 children=plot_data.to_json(date_format='iso', orient='split'),
                 id='plot-data'
                 ),
        html.Div(style={"display": "none"},
                 children=project_metrics.to_json(date_format='iso', orient='split'),
                 id='project-metrics'
                 ),

    ])

@app.callback(
    dash.dependencies.Output('intxn-distn', 'figure'),
    [dash.dependencies.Input('plot-data', 'children'),
     dash.dependencies.Input('project-metrics', 'children'),
     dash.dependencies.Input('color-scale-select', 'value')])
def update_distn(plot_data, project_metrics, colorscale_select):

    plot_data = pd.read_json(plot_data, orient='split')
    project_metrics = pd.read_json(project_metrics, orient='split')

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
    dash.dependencies.Output('mm-scatter', 'figure'),
    [dash.dependencies.Input('plot-data', 'children'),
     dash.dependencies.Input('project-metrics', 'children'),
     dash.dependencies.Input('color-scale-select', 'value')])
def update_scatter(plot_data, project_metrics, colorscale_select):

    plot_data = pd.read_json(plot_data, orient='split')
    project_metrics = pd.read_json(project_metrics, orient='split')

    drug1 = plot_data['lib1_name'].unique()
    drug2 = plot_data['lib2_name'].unique()

    # Set colorscale using whole project dataset
    color_zero = abs(0 - min(project_metrics[colorscale_select]) / (max(project_metrics[colorscale_select]) - min(project_metrics[colorscale_select])))
    color_min = project_metrics[colorscale_select].min()
    color_max = project_metrics[colorscale_select].max()

    return {
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
            'title': colorscale_select,
            'xaxis': {'title': f"{drug1[0]} IC50 log µM"},
            'yaxis': {'title': f"{drug2[0]} IC50 log µM"}
        }
    }

@app.callback(
    dash.dependencies.Output('combo-tissue', 'figure'),
    [dash.dependencies.Input('plot-data', 'children'),
     dash.dependencies.Input('color-scale-select', 'value')])
def update_tissue_plot(plot_data, colorscale_select):

    plot_data = pd.read_json(plot_data, orient='split')


    return {
        'data': [ go.Box(
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
        'layout': {
            'title': 'Combination interaction effects by tissue type',
            'showlegend': False
        }
    }


@app.callback(
    dash.dependencies.Output('combo-url', 'pathname'),
    [dash.dependencies.Input('mm-scatter', 'clickData')])
def go_to_dot(clicked_points):
    print("Click!")
    if clicked_points:
        p = clicked_points['points'][0]['customdata']
        print(p)
        return f"/matrix/{p[0]}/{p[1]}"