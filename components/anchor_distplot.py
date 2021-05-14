import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from db import session
from models import AnchorCombi
import pandas as pd
import plotly.figure_factory as ff
from utils import anchor_metrics

def layout(project,combination):
    query = session.query(AnchorCombi.synergy_delta_emax,
                          AnchorCombi.synergy_delta_xmid,
                          AnchorCombi.synergy_obs_emax,
                          AnchorCombi.anchor_conc,
                          AnchorCombi.library_id,
                          AnchorCombi.anchor_id
                          ).filter(AnchorCombi.project_id == project.id)

    all_combo_df = pd.read_sql(query.statement, session.bind)

    return html.Div(
        children=[
            dbc.Row(className='d-flex', children=[
                dbc.Col(width=12, children=[
                    html.Div(className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                             children=[
                                html.H3("Key metric distributions compared to all combos in project"),
                                html.Hr(),
                                dbc.Row([  # row
                                    dbc.Col(width=4, children=[
                                        dcc.Loading(className='gdsc-spinner', children=
                                        dcc.Graph(
                                            id='dist1',
                                            figure=generate_dist(all_combo_df, combination, 'synergy_delta_emax')
                                            )
                                        )
                                    ]),
                                    dbc.Col(width=4, children=[
                                        dcc.Loading(className='gdsc-spinner', children=
                                        dcc.Graph(
                                            id='dist1',
                                            figure=generate_dist(all_combo_df, combination, 'synergy_delta_xmid')
                                            )
                                        )
                                    ]),
                                    dbc.Col(width=4, children=[
                                        dcc.Loading(className='gdsc-spinner', children=
                                        dcc.Graph(
                                            id='dist1',
                                            figure=generate_dist(all_combo_df, combination, 'synergy_obs_emax')
                                            )
                                        )
                                    ]),
                                 ]) # row
                            ]), # html.Div
                ]), # col
            ]) #row
        ])

def generate_dist(df,combination,type):
    this_combo_df = df.loc[
        (df['library_id'] == combination.lib1.id) & (df['anchor_id'] == combination.lib2.id)]

    anc_conc = this_combo_df['anchor_conc'].drop_duplicates().sort_values()

    anc_low = anc_conc.iat[0]
    anc_high = anc_conc.iat[1]

    if(anc_conc.iat[0] > anc_conc.iat[1]):
        anc_low = anc_conc.iat[1]
        anc_high = anc_conc.iat[0]

    anc_high_df = this_combo_df.loc[this_combo_df['anchor_conc'] == anc_high]
    anc_low_df = this_combo_df.loc[this_combo_df['anchor_conc'] == anc_low ]

    fig = ff.create_distplot(
        [df[type], anc_high_df[type], anc_low_df[type]],
        ['All Combinations', 'Anchor High', 'Anchor Low'],
        show_hist=False,
        show_rug= False,
        curve_type = 'normal',
        bin_size = .2,

    )
    fig.update_layout(
                      xaxis=dict(title=anchor_metrics[type]['label']),
                      yaxis = dict(title='Frequency')
                      )

    if(type == 'synergy_delta_emax'):
        fig.add_shape(type="line",x0=0.2,y0=0,x1=0.2,y1=5,
                  line=dict(color="LightGrey", width=3))
        fig.add_annotation(x=0.2,y=5,
                           text="Synergy threshold",
                           showarrow=True,
                           arrowhead=1)

    if (type == 'synergy_delta_xmid'):
        fig.add_shape(type="line", x0=3, y0=0, x1=3, y1=0.2,
                      line=dict(color="LightGrey", width=3),
                      )
        fig.add_annotation(x=3, y=0.2,
                           text="Synergy threshold",
                           showarrow=True,
                           arrowhead=1)
    return fig