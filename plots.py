import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
from utils import viability_curve, x_to_conc


def dose_response_plot(drug, curve):
    plot_data = pd.DataFrame({'xfit': np.linspace(-10, 20, 25)})
    plot_data['conc_fit'] = x_to_conc(plot_data.xfit, float(curve.maxc))
    plot_data['nlme_model'] = viability_curve(plot_data['xfit'],
                                              curve.xmid,
                                              curve.scal)

    return dcc.Graph(
        id=f'dose-response-{drug.id}',
        figure={
            "data": [go.Scatter(
                x=plot_data.conc_fit,
                y=plot_data.nlme_model,
                mode='lines',
                name="Fitted Curve",
                line=dict(
                    shape='spline'
                )
            ),
                go.Scatter(
                    x=(x_to_conc(curve.xmid, float(curve.maxc)),),
                    y=(viability_curve(curve.xmid, curve.xmid, curve.scal),),
                    mode='markers',
                    name="IC50",
                )
            ],
            "layout": go.Layout(
                title=f'Single Agent Response for {drug.drug_name}',
                xaxis={'type': 'log', 'title': 'Log Concentration (M)'},
                shapes=[{
                    'type': 'rect',
                    'x0': float(curve.maxc) / 1000000000,
                    'y0': 0,
                    'x1': float(curve.maxc) / 1000000,
                    'y1': 1,
                    'line': {
                        'color': 'rgba(51,46,44, 0.6)',
                        'width': 2,
                    },
                    'fillcolor': 'rgba(51,46,44, 0.2)',
                }],
                margin=go.layout.Margin(l=20, r=0, b=200, t=50, pad=0),
                legend=dict(orientation="h")
            )

        }
    )