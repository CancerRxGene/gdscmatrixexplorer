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

from sqlalchemy.sql.expression import func
from sqlalchemy import and_, or_
import plotly.express as px
from app import app
from db import session
from models import MatrixResult, Project, Combination, Model, Drug, AnchorCombi, AnchorSynergy
from utils import plot_colors,  matrix_metrics, get_all_tissues, get_all_cancer_types, matrix_hover_label


def layout(project_id, celline):
    try:
        project = session.query(Project).get(project_id)
        print(project)
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    # get the data ready
    # models = session.query(Model.tissue).distinct().order_by(Model.tissue).all()
    lib_drugs = session.query(AnchorSynergy.library_id).filter(AnchorSynergy.project_id == project_id).distinct().all()
    anchor_drugs = session.query(AnchorSynergy.anchor_id).filter(
        AnchorSynergy.project_id == project_id).distinct().all()

    # print(lib_drugs)
    # print(anchor_drugs)

    # create list of lib names
    lib_names = []
    for i in lib_drugs:
        ld = session.query(Drug).get(i[0])
        lib_names.append(ld.name)
    print(lib_names)

    # create list of anchor names
    anchor_names = []
    for i in anchor_drugs:
        ad = session.query(Drug).get(i[0])
        anchor_names.append(ad.name)
    print(anchor_names)

    synergy_counts_list = []
    # for lib in lib_drugs:
    #     lib_drug_id = lib[0]

    for anc in anchor_drugs:
        anc_drug_id = anc[0]

        synergy_counts = []
        # for anc in anchor_drugs:
        #     anc_drug_id = anc[0]

        for lib in lib_drugs:
            lib_drug_id = lib[0]
            count_query = session.query(func.count(AnchorSynergy.cell_line_name)).filter(
                AnchorSynergy.library_id == lib_drug_id). \
                filter(AnchorSynergy.anchor_id == anc_drug_id).filter(AnchorSynergy.project_id == project_id).filter(
                AnchorSynergy.synergy == 1)

            synergy_count_df = pd.read_sql(count_query.statement, session.bind)
            synergy_count_per_combi = synergy_count_df.iloc[0, 0]

            # find the total count
            total_count_query = session.query(func.count(AnchorSynergy.cell_line_name)).filter(
                AnchorSynergy.library_id == lib_drug_id). \
                filter(AnchorSynergy.anchor_id == anc_drug_id).filter(AnchorSynergy.project_id == project_id)
            total_count_df = pd.read_sql(total_count_query.statement, session.bind)
            total_count_per_combi = total_count_df.iloc[0,0]

            if (synergy_count_per_combi > 0):
                if(celline == 'count'):
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

