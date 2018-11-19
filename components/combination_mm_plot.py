import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import dash.dependencies
import pandas as pd

from app import app



def layout(plot_data=None):

    dropdown_options = [
        {'label': 'Bliss excess' , 'value': 'Bliss_excess'},
        {'label': 'Bliss_excess_syn', 'value' : 'Bliss_excess_syn'},
        {'label': 'Bliss_excess_window', 'value' : 'Bliss_excess_window'},
        {'label': 'Bliss_excess_window_syn', 'value': 'Bliss_excess_window_syn'},
        {'label': 'HSA excess', 'value': 'HSA_excess'},
        {'label': 'HSA_excess_syn', 'value': 'HSA_excess_syn'},
        {'label': 'HSA_excess_syn', 'value': 'HSA_excess_syn'},
        {'label': 'HSA_excess_window', 'value': 'HSA_excess_window'},
        {'label': 'HSA_excess_window_syn', 'value': 'HSA_excess_window_syn'}]

    return html.Div(className='row', children=[
        html.Div(className='col-4',
            children=[
                html.Label('Combination interaction'),
                dcc.Dropdown(
                    options=dropdown_options,
                    value='HSA_excess',
                    id='color-scale-select',
                    clearable=False
                )
            ],
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(className='col-8',
            children=[
                dcc.Graph(
                    id='mm-scatter'
                )
            ],
            style={'width': '100%', 'float': 'left'}
        ),
        html.Div(style={"display": "none"},
                 children=plot_data.to_json(date_format='iso', orient='split'),
                 id='plot-data')
    ],
        style={'width':'100%'}
    )

@app.callback(
    dash.dependencies.Output('mm-scatter', 'figure'),
    [dash.dependencies.Input('color-scale-select', 'value'),
     dash.dependencies.Input('plot-data', 'children')])
def update_scatter(colorscale_select, plot_data):

    plot_data = pd.read_json(plot_data, orient='split')
    drug1 = plot_data['lib1_name'].unique()
    drug2 = plot_data['lib2_name'].unique()

    return {
        'data': [go.Scatter(
            x=plot_data['lib1_ic50'],
            y=plot_data['lib2_ic50'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 8,
                'color': plot_data[colorscale_select],
                'showscale': True
            }
        )
        ],
        'layout': {
            'title': colorscale_select,
            'xaxis': {'title': f"{drug1[0]} IC50 log µM"},
            'yaxis': {'title': f"{drug2[0]} IC50 log µM"}
        }
    }
