import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc

from utils import Colors as C


class DoseResponsePlot:

    def __init__(self, curve,
                 display_datapoints=True,
                 display_screening_range=True,
                 mark_auc=True,
                 label_auc=True,
                 mark_ic50=True,
                 label_ic50=True,
                 mark_emax=True,
                 label_emax=True,
                 label_rmse=True,
                 style=None):
        self.curve = curve

        self.plot_data = pd.DataFrame({'xfit': np.linspace(-10, 30, 25)})
        self.plot_data['conc_fit'] = curve.x_to_conc(self.plot_data.xfit)
        self.plot_data['nlme_model'] = curve.nlme_model(self.plot_data.xfit)

        self.datapoints = pd.DataFrame(
            [w.to_dict() for w in curve.single_agent_well_results]
        )
        self.id = f'dose-response-{curve.id}'
        self.display_datapoints = display_datapoints
        self.display_screening_range = display_screening_range
        self.mark_auc = mark_auc
        self.label_auc = label_auc
        self.mark_ic50 = mark_ic50
        self.label_ic50 = label_ic50
        self.mark_emax = mark_emax
        self.label_emax = label_emax
        self.label_rmse = label_rmse
        self.style = style

    def plot(self):
        return dcc.Graph(id=self.id, figure=self.figure, style=self.style)

    def __call__(self, *args, **kwargs):
        return self.plot()

    @property
    def figure(self):
        return dict(
            id=self.id,
            data=self.figure_data,
            layout=self.figure_layout
        )

    @property
    def figure_data(self):
        traces = []
        traces.extend([self.auc_area] if self.mark_auc else [])
        traces.extend([self.datapoint_markers] if self.display_datapoints else [])
        traces.append(self.fitted_curve)

        return traces

    @property
    def auc_area(self):
        auc_data = pd.DataFrame({
            'xfit': np.linspace(
                self.curve.conc_to_x(self.curve.maxc / 1000000000),
                self.curve.conc_to_x(self.curve.maxc / 1000000),
                15)
        })
        auc_data['conc_fit'] = self.curve.x_to_conc(auc_data.xfit)
        auc_data['nlme_model'] = self.curve.nlme_model(auc_data.xfit)

        return go.Scatter(
            x=auc_data.conc_fit,
            y=auc_data.nlme_model,
            mode='lines',
            name="AUC",
            line=dict(shape='spline', color=C.DEEPDARKBLUE),
            fill='tozeroy',
            hoverinfo='none',
            fillcolor=C.DEEPDARKBLUE_ULTRATRANS
        )

    @property
    def fitted_curve(self):
        return go.Scatter(
            x=self.plot_data.conc_fit,
            y=self.plot_data.nlme_model,
            mode='lines',
            name="Fitted Curve",
            line=dict(shape='spline', color=C.DEEPDARKBLUE),
            hoverinfo='none'
        )

    @property
    def datapoint_markers(self):
        return go.Scatter(
            x=self.datapoints.conc / 1000000,
            y=self.datapoints.viability,
            mode='markers',
            name="measurement",
            marker=dict(
                symbol=4,
                color=C.LIGHTGREEN,
                size=10,
                line={"width": 1, "color": 'white'}),
        )

    @property
    def figure_layout(self):

        return go.Layout(
                # title=f'Single Agent Response for {drug.drug_name}',
                xaxis={'type': 'log', 'title': 'Log Concentration (M)',
                       'range': np.log10([self.curve.x_to_conc(-10),
                                          self.curve.x_to_conc(20)])},
                yaxis={'title': 'Viability'},
                shapes=self.shapes,
                margin=go.layout.Margin(l=50, r=20, b=80, t=0, pad=10),
                showlegend=False,
                annotations=self.annotations
            )

    @property
    def shapes(self):
        shapes = []
        shapes.extend([self.emax_line] if self.mark_emax else [])
        shapes.extend([self.ic50_line] if self.mark_ic50 else [])
        shapes.extend([self.screening_range] if self.display_screening_range else [])
        return shapes


    @property
    def screening_range(self):
        return {
            'type': 'rect',
            'x0': self.curve.maxc / 1000000000,
            'y0': 0,
            'x1': self.curve.maxc / 1000000,
            'y1': 1,
            'line': {
                'color': C.DARKGREY_SUPERTRANS,
                'width': 2,
            },
            'fillcolor': C.DARKGREY_ULTRATRANS,
        }

    @property
    def emax_line(self):
        return {
            'type': 'line',
            'x0': self.curve.x_to_conc(-10),
            'y0': 1 - self.curve.emax,
            'x1': self.curve.maxc / 1000000,
            'y1': 1 - self.curve.emax,
            'line': {
                'color': C.PINKPURPLE,
                'width': 2,
                'dash': "dot"
            },
        }

    @property
    def ic50_line(self):
        return {
            'type': 'line',
            'x0': self.curve.x_to_conc(self.curve.xmid),
            'y0': 0,
            'x1': self.curve.x_to_conc(self.curve.xmid),
            'y1': self.curve.y_hat(self.curve.xmid),
            'line': {
                'color': C.RED,
                'width': 2,
                'dash': "dashdot"
            },
        }

    @property
    def annotations(self):
        annotations = []
        annotations.extend([self.auc_label] if self.label_auc else [])
        annotations.extend([self.ic50_label] if self.label_ic50 else [])
        annotations.extend([self.emax_label] if self.label_emax else [])
        annotations.extend([self.rmse_label] if self.label_rmse else [])
        return annotations

    @property
    def emax_label(self):
        return dict(
            x=np.log10(self.curve.maxc / 1000000),
            y=1 - self.curve.emax,
            xref='x',
            yref='y',
            text=f'<b>Emax</b> {round(1 - self.curve.emax, 3)}',
            showarrow=True,
            arrowhead=6,
            ax=30,
            ay=30,
            xanchor="left",
            bgcolor=C.DARKGREY_ULTRALIGHT,
            bordercolor=C.PINKPURPLE_TRANS,
            borderpad=2,
            font={"size": 12}
        )

    @property
    def ic50_label(self):
        return dict(
            x=np.log10(self.curve.x_to_conc(self.curve.xmid)),
            y=self.curve.y_hat(self.curve.xmid),
            xref='x',
            yref='y',
            text=f'<b>IC50</b> {round(self.curve.x_to_conc(self.curve.xmid) * 1000000, 3)}µM',
            showarrow=True,
            arrowhead=6,
            ax=-40,
            ay=-20,
            xanchor="right",
            bgcolor=C.DARKGREY_ULTRALIGHT,
            bordercolor=C.RED_TRANS,
            borderpad=2,
            font={"size": 12}
        )

    @property
    def auc_label(self):
        return dict(
            x=np.log10(self.curve.maxc / 500000000),
            y=0.15,
            xref='x',
            yref='y',
            text=f'<b>AUC</b> {round(self.curve.auc, 3)}',
            showarrow=True,
            arrowhead=0,
            ax=-20,
            ay=-20,
            xanchor="right",
            bgcolor=C.DARKGREY_ULTRALIGHT,
            bordercolor=C.DEEPDARKBLUE_TRANS,
            borderpad=2,
            font={"size": 12}
        )
    @property
    def rmse_label(self):
        return dict(
            x=1,
            y=0.95,
            xref='paper',
            yref='paper',
            text=f'<b>RMSE</b> {round(self.curve.rmse, 3)}',
            showarrow=False,
            xanchor="right",
            yanchor="top",
            bgcolor=C.DARKGREY_ULTRALIGHT,
            bordercolor=C.DARKGREY_LIGHT,
            borderpad=2,
            font={"size": 12}
        )

def dose_response_plot(drug, curve, display_auc_area=True):
    plot_data = pd.DataFrame({'xfit': np.linspace(-10, 30, 25)})
    plot_data['conc_fit'] = curve.x_to_conc(plot_data.xfit)
    plot_data['nlme_model'] = curve.nlme_model(plot_data.xfit)





    return dcc.Graph(
        id=f'dose-response-{drug.id}',
        figure={
            "data": [
                auc_area(curve) if display_auc_area else None,
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
