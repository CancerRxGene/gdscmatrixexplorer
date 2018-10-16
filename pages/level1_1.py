import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from scipy.stats import pearsonr

from db import session
from app import app
from models import MatrixResult


metrics = ["HSA_excess", "HSA_excess_syn", "HSA_excess_well_count",
           "HSA_excess_window", "HSA_excess_window_syn", "Bliss_excess",
           "Bliss_excess_syn", "Bliss_excess_well_count", "Bliss_excess_window",
           "Bliss_excess_window_syn"]
table_columns = ['model_id', 'cmatrix', 'barcode', 'drugset_id'] + metrics

summary = pd.DataFrame([x.to_dict() for x in session.query(MatrixResult).all()])

layout = html.Div([
    html.H2("GDSC_007-A Overview"),
    html.Div(
        children=[
            html.Label('x-axis'),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in metrics],
                value='HSA_excess',
                id='x-axis-select'
            ),
            html.Label('y-axis'),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in metrics],
                value='Bliss_excess',
                id='y-axis-select'
            )
        ],
        style={'width': '20%', 'float': 'left'}
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='project-scatter'
            ),
            html.Div(id='correlation'),
            html.Div(id='tst')
        ],
        style={'width': '75%', 'float': 'left'}
    ),
    html.Div(
        dt.DataTable(
            rows=summary.to_dict('records'),
            columns=table_columns,
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='datatable'
        ),
        style={'width': '90%'}
    )
    ],
    style={'width':'100%'}
)


@app.callback(
    dash.dependencies.Output('project-scatter', 'figure'),
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value'),
     dash.dependencies.Input('datatable', 'rows')])
def update_scatter(x_axis_field, y_axis_field, rows):

    fig_data = pd.DataFrame(rows)
    # fig_data = summary
    return {
        'data': [
            go.Scatter(
                x=fig_data[x_axis_field],
                y=fig_data[y_axis_field],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 4,
                    'color':[ord(x) for x in fig_data.model_id.str[0]]
                },
                text=[f"drug1 - drug2<br />Cell line: {s.model_id}"  # TODO: Fill in real drug names
                      for s in fig_data.itertuples()],
                customdata=[row for row in fig_data[['model_id']].itertuples(index=False)]
            )
        ],
        'layout': go.Layout(
            height=700,
            hovermode='closest',
            xaxis={'type': 'log' if 'index' in x_axis_field else 'linear',
                   'title': x_axis_field.replace('_', ' ')},
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': y_axis_field.replace('_', ' ')}
        )
    }

@app.callback(
    dash.dependencies.Output('correlation', 'children'),
    [dash.dependencies.Input('x-axis-select', 'value'),
     dash.dependencies.Input('y-axis-select', 'value')])
def update_correlation(x_axis_field, y_axis_field):
    corr = pearsonr(
        np.log(summary[x_axis_field]) if 'index' in x_axis_field else summary[x_axis_field],
        np.log(summary[y_axis_field]) if 'index' in y_axis_field else summary[y_axis_field])
    return f"Correlation: {round(corr[0], 3)}"

@app.callback(
    dash.dependencies.Output('url', 'pathname'),
    [dash.dependencies.Input('project-scatter', 'clickData')])
def go_to_dot(clicked):
    if clicked:
        p = clicked['points'][0]['customdata']
        return f"/GDSC_007-A/matrix/{p[2]}/{p[0]}/{p[1]}"
    else:
        return "/GDSC_007-A/free_scatter"

if __name__ == '__main__':
    app.run_server(debug=True)
