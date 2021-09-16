import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

def layout():
    df = pd.read_csv("data/Overall_ANOVA_results_significant_large_effect_results_5_FDR_without_proteomics.csv")

    # add column analysis
    df["Analysis"] = "NaN"

    df.loc[(df["Tissue"] == "all") & (df["Genotype"] == "all"), "Analysis"] = "Pan-tissue"
    df.loc[(df["Tissue"] == "breast") & (df["Genotype"] == "all"), "Analysis"] = "Breast"
    df.loc[(df["Tissue"] == "pancreas") & (df["Genotype"] == "all"), "Analysis"] = "Pancreas"
    df.loc[(df["Tissue"] == "colon") & (df["Genotype"] == "all"), "Analysis"] = "Colon"
    df.loc[(df["Tissue"] == "all") & (df["Genotype"] != "all"), "Analysis"] = "Pan-tissue molecular basket"
    df.loc[(df["Tissue"] != "all") & (df["Genotype"] != "all"), "Analysis"] = "Intra-tissue molecular basket"

    # subset = df.loc[df['Input'] == "delta IC50"]

    # x = subset['FEATURE_delta_MEAN_IC50']
    # y = -np.log10(subset['ANOVA_FEATURE_pval'])
    # Analysis = subset['Analysis']
    # print(Analysis)
    return html.Div([
        #  dcc.Graph(
        #     id='volcano', figure=
        #         go.Figure(
        #             data=px.scatter(
        #                 subset,
        #                 x=x,
        #                 y=y,
        #                 color=Analysis
        #     )
        # )),
         dcc.Graph(
             id='volcano', figure=
                generate_volcano(df,'delta IC50')
         ),
        # dcc.Graph(
        #     id='volcano', figure=
        #     generate_volcano(df, 'combo Emax', Analysis)
        # ),
        # dcc.Graph(
        #     id='volcano', figure=
        #     generate_volcano(df, 'delta Emax', Analysis)
        # ),
        # dcc.Graph(
        #     id='volcano', figure=
        #     generate_volcano(df, 'library IC50')
        # ),

])

def generate_volcano(df,type):
    data = df.loc[df['Input'] == type]

    if(type == 'delta IC50'):
        column = 'FEATURE_delta_MEAN_IC50'
    elif (type == 'library IC50'):
        column = 'FEATURE_IC50_effect_size'

    color_discrete_map = {
        'Breast': 'rgb(249,55,14)',
        'Colon': 'rgb(162,132,126)',
        'Pan-tissue': 'rgb(93,173,226)',
        'Pancreas':'rgb(233,96,160)',
        'Pan-tissue molecular basket':'rgb(52,152,219)',
        'Intra-tissue molecular basket':'rgb(125,206,160)'
    }

    labels = {

    }

    fig = go.Figure(
        data=px.scatter(
            data,
            x=data[column],
            y=-np.log10(data['ANOVA_FEATURE_pval']),
            color=data['Analysis'],
            color_discrete_map = color_discrete_map,
            hover_data=['FEATURE', 'DRUG_NAME','Tissue'],
        ))

    fig.update_layout(
        xaxis={
            'title': 'Effect size'},
        yaxis={
            'title': '-log10 p value'},
        title={
            'text':'Significant molecular associations with delta IC50',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig

