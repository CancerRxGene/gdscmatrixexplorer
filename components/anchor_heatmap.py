from functools import lru_cache

import string
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import sqlalchemy as sa
from sqlalchemy.sql.expression import func
from sqlalchemy import and_, or_
import plotly.express as px
from app import app
from db import session
from models import MatrixResult, Project, Combination, Model, Drug, AnchorCombi, AnchorSynergy
from utils import plot_colors,  matrix_metrics, get_all_tissues, get_all_cancer_types, matrix_hover_label

def layout(project_id):
    try:
        project = session.query(Project).get(project_id)
        print(project)
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    # get the data ready
    print(project_id)
    models = session.query(Model.tissue).distinct().order_by(Model.tissue).all()
    lib_drugs = session.query(AnchorSynergy.library_id).filter(AnchorSynergy.project_id == project_id).distinct().all()
    anchor_drugs = session.query(AnchorSynergy.anchor_id).filter(AnchorSynergy.project_id == project_id).distinct().all()

    print(lib_drugs)
    print(anchor_drugs)

    # create list of lib names
    lib_names = []
    for i in lib_drugs:
        ld = session.query(Drug).get(i[0])
        lib_names.append(ld.name)
    print(lib_names)
    #create list of anchor names
    anchor_names = []
    for i in anchor_drugs:
        ad = session.query(Drug).get(i[0])
        anchor_names.append(ad.name)
    print(anchor_names)

    a_c = 0
    total_cl_counts = []
    for anc_d in anchor_drugs:
        a_c = a_c + 1;
        l_c = 0
        cl_count_per_anc = []
        for lib_d in lib_drugs:
            print("anc id:" , anc_d[0])
            print("lib id:" , lib_d[0])
            l_c = l_c +1

            count_query = session.query(func.count(AnchorSynergy.cell_line_name)).filter(AnchorSynergy.library_id == lib_d[0]).\
                 filter(AnchorSynergy.anchor_id == anc_d[0]).filter(AnchorSynergy.project_id == project_id).filter(AnchorSynergy.synergy==1)

            f = pd.read_sql(count_query.statement, session.bind)

            print("cl.count:", f.iloc[0,0])
            if(f.iloc[0,0]>0):
                cl_count_per_anc.append(f.iloc[0,0])
            else:
                cl_count_per_anc.append('NA')
            print("------")

        total_cl_counts.append(cl_count_per_anc)

        print("----")
    print("total cell line count:\n", total_cl_counts)
    print("-------\n\n", [str(l[0]) for l in lib_drugs])
    print([str(a[0]) for a in anchor_drugs])

    fig = px.imshow(total_cl_counts,
                    labels=dict(x="library", y="Anchor", color="#synergistic cell lines",color_continuous_scale="sunset"),
                    x=lib_names,
                    y=anchor_names)



    return fig


