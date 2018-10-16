import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import pandas as pd
import plotly.graph_objs as go

from app import app
from db import session
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
            html.Label('y-axis', htmlFor='y-axis-select-boxplot'),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in metrics],
                value='Bliss_excess',
                id='y-axis-select-boxplot'
            )
        ],
        style={'width': '20%', 'float': 'left'}
    ),
    html.Div(
        children=[
            dcc.Graph(
                id='project-boxplot'
            )
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
            editable=False,
            id='datatable1_2'
        ),
        style={'width': '95%'}
    )
],
style={'width':'100%'})


@app.callback(
    dash.dependencies.Output('project-boxplot', 'figure'),
    [dash.dependencies.Input('y-axis-select-boxplot', 'value')]
)
def update_boxplot(y_axis_field):

    fig_data = summary
    return {
        'data': [
            go.Box(
                name=str(cm),
                y=np.exp(fig_data.query("cmatrix == @cm")[y_axis_field]) if y_axis_field == 'Bliss_additivity' else fig_data.query("cmatrix == @cm")[y_axis_field],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=2,
                    opacity=0.5
                ),
            ) for cm in fig_data.cmatrix.unique()
        ],
        'layout': go.Layout(
            height=700,
            margin=dict(l=40, r=30, b=80, t=100),
            showlegend=False,
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': y_axis_field.replace('_', ' ')}
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
