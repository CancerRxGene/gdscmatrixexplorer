from typing import Any, Union

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from pandas import DataFrame
from pandas.io.parsers import TextFileReader

labels = {
        "y": "-log10 p value",
        "FEATURE_delta_MEAN_IC50": "Effect size",
        "DRUG_NAME":"Drug Name",
        "ANOVA_FEATURE_pval": "P Value"
    }

color_discrete_map = {
    'Breast': 'rgb(247, 95, 57)',
    'Colon': 'rgb(218, 166, 94)',
    'Pan-tissue': 'rgb(93,173,226)',
    'Pancreas': 'rgb(233,96,160)',
    'Pan-tissue molecular basket': 'rgb(10, 147, 247)',
    'Intra-tissue molecular basket': 'rgb(55, 186, 41)'
}


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

    return html.Div([
         dcc.Graph(
             id='volcano', figure=
                generate_volcano(df,'delta IC50')
         ),
        dcc.Graph(
            id='volcano', figure=
                generate_volcano(df, 'combo Emax')
        ),
        dcc.Graph(
            id='volcano', figure=
                generate_volcano(df, 'delta Emax')
        ),
        dcc.Graph(
            id='volcano', figure=generate_lib_volcano()
        ),

])

def generate_volcano(df,type):
    data = df.loc[df['Input'] == type]

    column = 'FEATURE_delta_MEAN_IC50'

    fig = go.Figure(
        data=px.scatter(
            data,
            x=data[column],
            y=-np.log10(data['ANOVA_FEATURE_pval']),
            color=data['Analysis'],
            color_discrete_map = color_discrete_map,
            hover_data=['Analysis', 'ANOVA_FEATURE_pval','Tissue','Genotype', 'DRUG_NAME', 'FEATURE'],
            labels = labels
        ))

    fig.update_layout(
        xaxis={
            'title': 'Effect size'},
        yaxis={
            'title': '-log10 p value'},
        title={
            'text':'Significant molecular associations with ' + type,
            'font': {
                'size': 20,
                'color': 'black'
            },
        }
    )

    return fig

def generate_lib_volcano():
    df_lib: Union[Union[TextFileReader, DataFrame], Any] = pd.read_csv("data/Lib_IC50_sign_large_effect_results_for_Wendy.csv")

    df_lib['DRUG_NAME_ANCHOR'], df_lib['DRUG_NAME_LIB'] = map(list, zip(*(s.split("_") for s in df_lib['DRUG_NAME'])))

    # add column label
    df_lib['Label'] = 'NaN'

    df_lib.loc[(df_lib['DRUG_NAME_LIB'] == 'Dabrafenib') & (df_lib['FEATURE'] == 'BRAFmut'), 'Label'] = "BRAF mutation and dabrafenib sensitivity"
    df_lib.loc[(df_lib['DRUG_NAME_LIB'] == "Nutlin-3a (-)") & (df_lib['FEATURE'] == "TP53_mut"), 'Label'] = "TP53 mutation and nutlin-3a resistance"
    df_lib.loc[(df_lib['DRUG_NAME_LIB'] == "Taselisib") & (df_lib['FEATURE'] == "PIK3CA_mut"), 'Label'] = "PIK3CA mutation and taselisib sensitivity"
    df_lib.loc[(df_lib['DRUG_NAME_LIB'] == "Afatinib") & (df_lib['FEATURE'] == "gain:cnaPANCAN301 (CDK12,ERBB2,MED24)"), 'Label'] = "ERBB2 amplification and afatinib sensitivity"

    #print(df_lib[['DRUG_NAME', 'DRUG_NAME_ANCHOR','DRUG_NAME_LIB','FEATURE','Label']])
    column = 'FEATURE_delta_MEAN_IC50'
    color_map = {
        'BRAF mutation and dabrafenib sensitivity': 'rgb(158,67,162)',
        'TP53 mutation and nutlin-3a resistance': 'rgb(255, 215, 0)',
        'PIK3CA mutation and taselisib sensitivity': 'rgb(241, 168, 120)',
        'ERBB2 amplification and afatinib sensitivity': 'rgb(32,178,170)',
        'NaN':'rgb(211,211,211)'
    }

    fig = go.Figure(
        data=px.scatter(
            df_lib,
            x=df_lib[column],
            y=-np.log10(df_lib['ANOVA_FEATURE_pval']),
            color=df_lib['Label'],
            color_discrete_map=color_map,
            hover_data=[ 'ANOVA_FEATURE_pval', 'Tissue', 'Genotype', 'DRUG_NAME', 'FEATURE'],
            labels=labels
        ))

    fig.update_layout(
        xaxis={
            'title': 'Effect size'},
        yaxis={
            'title': '-log10 p value'},
        title={
            'text': 'Significant molecular associations with library IC50',
            'font':{
                'size':20,
                'color': 'black'
            },
            'pad':{'t': 10}
        },

    )

    return fig

