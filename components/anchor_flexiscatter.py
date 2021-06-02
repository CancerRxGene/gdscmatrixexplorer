from functools import lru_cache
from db import session
import plotly.graph_objs as go
import plotly_express as px
import plotly.io as pio
pio.templates.default = "plotly_white"
import pandas as pd
from models import AnchorCombi, Model
from utils import anchor_metrics, anchor_metrics_labels
from utils import plot_colors, anchor_hover_label,get_all_cancer_types

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
                                 AnchorCombi.anchor_target,
                                 AnchorCombi.sidm
                                 ).filter(AnchorCombi.project_id == int(project_id))

    #anchor_combi = session.query(AnchorCombi).filter(AnchorCombi.project_id == int(project_id))

    filtered_df = pd.read_sql(anchor_combi.statement, session.bind)

    if (combintation):
        # add a new column in the dataframe
        #new_column = [str(l)+" + "+str(a) for l, a in zip(filtered_df['library_id'].tolist(), filtered_df['anchor_id'].tolist())]
        new_column = [str(a) + " + " + str(l) for a, l in
                      zip(filtered_df['anchor_id'].tolist(), filtered_df['library_id'].tolist())]

        filtered_df['combination'] = new_column

        #filter using new column
        filtered_df = filtered_df[filtered_df.combination.isin(combintation)]

    else:
        if (library):
            filtered_df = filtered_df[filtered_df.library_id.isin(library)]
        if (anchor):
            filtered_df = filtered_df[filtered_df.anchor_id.isin(anchor)]

    if (tissue):
        filtered_df = filtered_df[filtered_df.tissue.isin(tissue)]
    if (cancertype):
        filtered_df = filtered_df[filtered_df.cancer_type.isin(cancertype)]

    # if (tissue):
    #     print(tissue)
    #     cancer_type_options = [
    #         ct[0]
    #         for ct in session.query(Model.cancer_type)
    #             .filter(Model.tissue.in_(tissue))\
    #            # .filter(Model.tissue == tissue) \
    #             .distinct()\
    #             .all()]
    # else:
    #     cancer_type_options = get_all_cancer_types()
    #
    # ct_options = [{'label': c, 'value': c} for c in sorted(cancer_type_options)]
    # print(ct_options)
    # add combo_id column to df for color by combination use
    #filtered_df['combo_id'] = filtered_df.project_id.astype(str) + "::" + filtered_df.anchor_id.astype(str) + "::" + filtered_df.library_id.astype(str)
    filtered_df['combo_name'] = filtered_df.anchor_name.astype(str) + " + " + filtered_df.library_name.astype(str)

    return layout(filtered_df,color,xaxis,yaxis)
   #           ct_options)


def layout(filtered_df,color,xaxis,yaxis):
    xaxis_data = filtered_df[xaxis]
    yaxis_data =  filtered_df[yaxis]

    x_title = anchor_metrics[xaxis]['label']
    y_title = anchor_metrics[yaxis]['label']

    # Change viability metrics to a scale 0-100 %
    viability_values = ['synergy_obs_emax','library_emax','anchor_viability']

    if(xaxis in viability_values):
        filtered_df[xaxis] = filtered_df[xaxis].apply(lambda x: "{:.2%}".format(x))
        x_title = x_title + " %"

    if(yaxis in viability_values):
        filtered_df[yaxis] = filtered_df[yaxis].apply(lambda x: "{:.2%}".format(x))
        y_title = y_title + " %"

    color_values = {}

    for i, v in enumerate(filtered_df[color].unique()):
        color_values[v] = plot_colors[i % len(plot_colors)]

    fig = go.Figure(
        #data=go.Scatter(
        data = px.scatter(
            filtered_df,
            x = xaxis,
            y = yaxis,
            color = color,

            labels= anchor_metrics_labels,
            hover_data=['tissue', 'cancer_type','cell_line_name','sidm'],
    ))

    fig.update_layout(
        xaxis={
               'title': x_title },
        yaxis={
               'title': y_title},
        height=900,
        width=1000,
    )
    return fig


