import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc


def dose_response_plot(drug, curve):
    plot_data = pd.DataFrame({'xfit': np.linspace(-10, 30, 25)})
    plot_data['conc_fit'] = curve.x_to_conc(plot_data.xfit)
    plot_data['nlme_model'] = curve.nlme_model(plot_data.xfit)

    auc_data = pd.DataFrame({'xfit': np.linspace(curve.conc_to_x(curve.maxc / 1000000000) ,
                                                 curve.conc_to_x(curve.maxc / 1000000),
                                                 15)})
    auc_data['conc_fit'] = curve.x_to_conc(auc_data.xfit)
    auc_data['nlme_model'] = curve.nlme_model(auc_data.xfit)

    points = pd.DataFrame([w.to_dict() for w in curve.single_agent_well_results])

    return dcc.Graph(
        id=f'dose-response-{drug.id}',
        figure={
            "data": [
                go.Scatter(
                    x=auc_data.conc_fit,
                    y=auc_data.nlme_model,
                    mode='lines',
                    name="AUC",
                    line=dict(shape='spline', color='rgb(117,97,207)'),
                    fill='tozeroy',
                    hoverinfo='none',
                    fillcolor='rgba(117,97,207, 0.2)'
                ),
                go.Scatter(
                    x=plot_data.conc_fit,
                    y=plot_data.nlme_model,
                    mode='lines',
                    name="Fitted Curve",
                    line=dict(shape='spline', color='rgb(117,97,207)'),
                    hoverinfo='none'
                ),
                go.Scatter(
                    x=points.conc / 1000000,
                    y=points.viability,
                    mode='markers',
                    name="measurement",
                    marker=dict(symbol=4, color='rgb(117,171,61)',
                                size=10,
                                line={"width": 1, "color": 'white'}),
                ),
                go.Scatter(
                    x=(curve.x_to_conc(curve.xmid),),
                    y=(curve.y_hat(curve.xmid),),
                    mode='markers',
                    name="IC50",
                    marker=dict(color='rgba(208,76,66, 0.5)', size=10),
                    hoverinfo='none'
                ),
                go.Scatter(
                    x=(curve.maxc / 1000000,),
                    y=(curve.y_hat(curve.conc_to_x(curve.maxc / 1000000)),),
                    mode='markers',
                    name="Emax",
                    marker=dict(color='rgb(194,93,186)', size=10),
                    hoverinfo='none'
                ),


            ],
            "layout": go.Layout(
                # title=f'Single Agent Response for {drug.drug_name}',
                xaxis={'type': 'log', 'title': 'Log Concentration (M)',
                       'range': np.log10([curve.x_to_conc(-10), curve.x_to_conc(20)])},
                yaxis={'title': 'Viability'},
                shapes=[{
                        'type': 'rect',
                        'x0': curve.maxc / 1000000000,
                        'y0': 0,
                        'x1': curve.maxc / 1000000,
                        'y1': 1,
                        'line': {
                            'color': 'rgba(51,46,44, 0.3)',
                            'width': 2,
                        },
                        'fillcolor': 'rgba(51,46,44, 0.05)',
                    },
                    {
                        'type': 'line',
                        'x0': curve.x_to_conc(-10),
                        'y0': 1 - curve.emax,
                        'x1': curve.maxc / 1000000,
                        'y1': 1 - curve.emax,
                        'line': {
                            'color': 'rgb(194,93,186)',
                            'width': 2,
                            'dash': "dot"
                        },
                    },
                    {
                        'type': 'line',
                        'x0': curve.x_to_conc(curve.xmid),
                        'y0': 0,
                        'x1': curve.x_to_conc(curve.xmid),
                        'y1': curve.y_hat(curve.xmid),
                        'line': {
                            'color': 'rgb(208,76,66)',
                            'width': 2,
                            'dash': "dashdot"
                        },
                    }
                ],
                margin=go.layout.Margin(l=50, r=20, b=80, t=0, pad=10),
                showlegend=False,
                annotations=[
                    dict(
                        x=np.log10(curve.maxc / 1000000),
                        y=1 - curve.emax,
                        xref='x',
                        yref='y',
                        text=f'<b>Emax</b> {round(1 - curve.emax, 3)}',
                        showarrow=True,
                        arrowhead=6,
                        ax=40,
                        ay=10,
                        xanchor="left",
                        bgcolor="rgb(251, 248, 251)",
                        bordercolor="rgba(194,93,186, 0.6)",
                        borderpad=3,
                        font={"size": 14}
                    ),
                    dict(
                        x=np.log10(curve.x_to_conc(curve.xmid)),
                        y=curve.y_hat(curve.xmid),
                        xref='x',
                        yref='y',
                        text=f'<b>IC50</b> {round(curve.x_to_conc(curve.xmid) * 1000000, 3)}µM',
                        showarrow=True,
                        arrowhead=6,
                        ax=-60,
                        ay=-10,
                        xanchor="right",
                        bgcolor="rgb(252, 247, 247)",
                        bordercolor="rgba(208,76,66, 0.6)",
                        borderpad=3,
                        font={"size": 14}
                    ),
                    dict(
                        x=np.log10(curve.maxc / 500000000),
                        y=0.15,
                        xref='x',
                        yref='y',
                        text=f'<b>AUC</b> {round(curve.auc, 3)}',
                        showarrow=True,
                        arrowhead=0,
                        ax=-40,
                        ay=-40,
                        xanchor="right",
                        bgcolor="rgb(249, 248, 252)",
                        bordercolor="rgba(117,97,207, 0.6)",
                        borderpad=3,
                        font={"size": 14}
                    ),
                    dict(
                        x=1,
                        y=0.95,
                        xref='paper',
                        yref='paper',
                        text=f'<b>RMSE</b> {round(curve.rmse, 3)}',
                        showarrow=False,
                        xanchor="right",
                        yanchor="top",
                        bgcolor="rgb(246, 247, 246)",
                        bordercolor="rgba(51,46,44, 0.3)",
                        borderpad=3,
                        font={"size": 14}
                    ),
                ]
            )

        }
    )

# rgb(117,171,61) lightgreen
# rgb(117,97,207) deepdarkblue
# rgb(177,150,64) brown/orange
# rgb(194,93,186) pinkpurple
# rgb(85,164,112) leafgreen
# rgb(208,76,66) warm red
# rgb(69,176,207) lightblue
# rgb(196,118,67) rust
# rgb(127,128,197) flatdarkblue
# rgb(199,89,128) darkpink