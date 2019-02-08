import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html

from utils import Colors as C


class DoseResponsePlot:

    def __init__(self, curve,
                 display_datapoints=True,
                 display_screening_range=True,
                 display_day1_viab=True,
                 mark_auc=True,
                 label_auc=True,
                 mark_ic50=True,
                 label_ic50=True,
                 mark_emax=True,
                 label_emax=True,
                 label_rmse=True,
                 label_day1=True,
                 style={},
                 width=None,
                 height=None):
        self.curve = curve

        self.plot_data = pd.DataFrame({'xfit': np.linspace(-10, 30, 25)})
        self.plot_data['conc_fit'] = curve.x_to_conc(self.plot_data.xfit)
        self.plot_data['nlme_model'] = curve.nlme_model(self.plot_data.xfit)

        self.datapoints = pd.DataFrame(
            [w.to_dict() for w in curve.well_results]
        )
        self.id = f'dose-response-{curve.id}'
        self.display_datapoints = display_datapoints
        self.display_screening_range = display_screening_range
        self.display_day1_viab = display_day1_viab
        self.mark_auc = mark_auc
        self.label_auc = label_auc
        self.mark_ic50 = mark_ic50
        self.label_ic50 = label_ic50
        self.mark_emax = mark_emax
        self.label_emax = label_emax
        self.label_rmse = label_rmse
        self.label_day1 = label_day1
        self.style = style
        self.width = width
        self.height = height

    def plot(self):

        graph = dcc.Graph(id=self.id,
                         figure=self.figure,
                         style=self.style,
                         config={'displayModeBar': False}
                         )
        if self.curve.rmse > 0.3:
            return html.Div(graph, style={'borderTop': '5px solid red'})
        else:
            return graph

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
                self.curve.conc_to_x(self.curve.minc / 1000000),
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

        if hasattr(self.datapoints, 'conc'):
            x = self.datapoints.conc
        elif self.datapoints.lib1_conc.nunique() > 1:
            x = self.datapoints.lib1_conc
        elif self.datapoints.lib2_conc.nunique() > 1:
            x = self.datapoints.lib2_conc
        else:
            x = (0,)
        return go.Scatter(
            x=x / 1000000,
            y=self.datapoints.viability,
            mode='markers',
            name="measurement",
            marker=dict(
                symbol="x-thin-open",
                color=C.DARKGREY,
                size=7
                ),
        )

    @property
    def figure_layout(self):

        return go.Layout(
                # title=f'Single Agent Response for {drug.drug_name}',
                width=self.width,
                height=self.height,
                xaxis={'type': 'log', 'title': 'Concentration (M)',
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
        shapes.extend([self.day1_line] if self.display_day1_viab else [])
        return shapes


    @property
    def screening_range(self):
        return {
            'type': 'rect',
            'x0': self.curve.minc / 1000000,
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
    def day1_line(self):
        return {
            'type': 'line',
            'x0': self.curve.maxc / 1000000000,
            'y0': self.curve.matrix_result.day1_viability_mean,
            'x1': self.curve.maxc / 1000000,
            'y1': self.curve.matrix_result.day1_viability_mean,
            'line': {
                'color': C.PINKPURPLE,
                'width': 2,
                'dash': "dot"
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
            bgcolor=C.DARKGREY_ULTRALIGHT if self.curve.rmse < 0.3 else C.RED,
            bordercolor=C.DARKGREY_LIGHT,
            borderpad=2,
            font={"size": 12, 'color': C.DARKGREY if self.curve.rmse < 0.3 else 'white'}
        )
