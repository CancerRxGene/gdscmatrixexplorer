from functools import lru_cache

import string
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import sqlalchemy as sa
import plotly.graph_objects as go

import plotly.express as px
from db import session
from models import  Drug, AnchorSynergy
from utils import get_project_from_url

def layout(display_opt,url):
    try:
        project = get_project_from_url(url)
        project_id = project.id

    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    # get the data ready
    anchor_synergy = session.query(AnchorSynergy).filter(AnchorSynergy.project_id == project_id)

    df = pd.read_sql(anchor_synergy.statement, session.bind)
    lib_drugs = df['library_id'].drop_duplicates()
    anchor_drugs = df['anchor_id'].drop_duplicates()

    # create list of lib names
    lib_names = []
    for l in lib_drugs:
        l_drug = session.query(Drug).get(l)
        lib_names.append(l_drug.name)
    print(lib_names)

    # create list of anchor names
    anchor_names = []
    for ac in anchor_drugs:
        an_drug = session.query(Drug).get(ac)
        anchor_names.append(an_drug.name)
    print(anchor_names)

    synergy_counts_list = []

    for anc_drug_id in anchor_drugs:
        synergy_counts = []

        for lib_drug_id in lib_drugs:
            synergy_count_per_combi_df = df.loc[(df['library_id'] == lib_drug_id) & (df['anchor_id'] == anc_drug_id) & (df['synergy'] == 1)]
            total_count_per_combi_df = df.loc[(df['library_id'] == lib_drug_id) & (df['anchor_id'] == anc_drug_id)]

            synergy_count_per_combi = synergy_count_per_combi_df.size
            total_count_per_combi = total_count_per_combi_df.size

            if (total_count_per_combi > 0):
                if(display_opt == 'count'):
                    z_label = '#synergistic cell lines'
                    synergy_counts.append(synergy_count_per_combi)
                else:
                    z_label = '%synergistic cell lines'
                    synergy_counts.append(round((synergy_count_per_combi/total_count_per_combi)*100))
            else:
                synergy_counts.append(None)

        synergy_counts_list.append(synergy_counts)

    fig = px.imshow(synergy_counts_list,
                    # labels=dict(x="Anchor", y="Library", color="#synergistic cell lines",
                    #             color_continuous_scale="sunset"),
                    # x=anchor_names,
                    # y=lib_names
                    labels=dict(x="Library", y="Anchor", color=z_label,
                                color_continuous_scale="sunset"),
                    x=lib_names,
                    y=anchor_names
                    )
    fig.update_xaxes(side="top")

    return fig
    #
    # return {
    #     'data': [
    #         go.Heatmap(
    #             x=lib_names,
    #             y=anchor_names,
    #             z=synergy_counts_list,
    #             # zmax=zmax,
    #             # zmin=zmin,
    #         )
    #     ],
    #      'layout': go.Layout(#title=well_metrics[metric]['label'],
    #                         xaxis={'type': 'category',
    #                                #'title': f"{drug_names[0]} (µM)"
    #                                },
    #                         yaxis={'type': 'category',
    #                                #'title': f"{drug_names[1]} (µM)"
    #                                },
    #                         #margin={'l': 100}
    #                         )
    # }