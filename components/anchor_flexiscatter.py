from functools import lru_cache
from db import session
import dash_html_components as html
import sqlalchemy as sa
import plotly.graph_objs as go
import pandas as pd
from models import Drug, AnchorCombi, Project, Model
from utils import anchor_metrics, get_all_cancer_types
from utils import plot_colors, anchor_hover_label

@lru_cache(maxsize=1000)
def cached_update_scatter(tissue,cancertype,library,anchor,combintation,color,xaxis,yaxis, project_id):
    # get the data frame
    anchor_combi = session.query(AnchorCombi.project_id, AnchorCombi.library_id,
                                 AnchorCombi.anchor_id, AnchorCombi.anchor_viability,
                                 AnchorCombi.library_emax, AnchorCombi.library_xmid,
                                 AnchorCombi.synergy_xmid, AnchorCombi.synergy_obs_emax,
                                 AnchorCombi.synergy_exp_emax,
                                 AnchorCombi.synergy_delta_xmid, AnchorCombi.synergy_delta_emax,
                                 AnchorCombi.tissue, AnchorCombi.cancer_type,
                                 AnchorCombi.cell_line_name,
                                 AnchorCombi.library_name,
                                 AnchorCombi.anchor_name,
                                 AnchorCombi.library_target,
                                 AnchorCombi.anchor_target
                                 ).filter(AnchorCombi.project_id == int(project_id))

    filtered_df = pd.read_sql(anchor_combi.statement, session.bind)
    #filtered_df = df[(df.project_id == project_id)]

    if (combintation):
        drug = combintation.split(" + ")
        lib_id = int(drug[0])
        anchor_id = int(drug[1])
        filtered_df = filtered_df[(filtered_df.library_id == lib_id) & (filtered_df.anchor_id == anchor_id)]

    else:
        if (library):
            filtered_df = filtered_df[filtered_df.library_id == library]
        if (anchor):
            filtered_df = filtered_df[filtered_df.anchor_id == anchor]

    if (tissue):
        filtered_df = filtered_df[filtered_df.tissue == tissue]
    if (cancertype):
        filtered_df = filtered_df[filtered_df.cancer_type == cancertype]
    #
    # if (tissue):
    #     cancer_type_options = [
    #         ct[0]
    #         for ct in session.query(Model.cancer_type)
    #            # .filter(Model.tissue.in_(tissues))\
    #             .filter(Model.tissue == tissue) \
    #             .distinct()\
    #             .all()]
    # else:
    #     cancer_type_options = get_all_cancer_types()
    #
    # ct_options = [{'label': c, 'value': c} for c in sorted(cancer_type_options)]

    return layout(filtered_df,color,xaxis,yaxis)
             # ct_options)


def layout(filtered_df,color,xaxis,yaxis):
    xaxis_data = filtered_df[xaxis]
    yaxis_data =  filtered_df[yaxis]
    x_title = anchor_metrics[xaxis]['label']
    y_title = anchor_metrics[yaxis]['label']

    color_values = {}

    for i, v in enumerate(filtered_df[color].unique()):
        color_values[v] = plot_colors[i % len(plot_colors)]

    fig = go.Figure(
        data=go.Scatter(
        x = xaxis_data,
        y = yaxis_data,
        mode='markers',
        marker={
                'size': 4,
                'color': [color_values[x] for x in filtered_df[color]]
            },
        text=anchor_hover_label(filtered_df),
        opacity=0.7,
    ))

    fig.update_layout(
        xaxis={
               'title': x_title },
        yaxis={
               'title': y_title}
    )

    return fig

