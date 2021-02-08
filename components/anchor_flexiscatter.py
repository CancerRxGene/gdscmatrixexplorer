import plotly.graph_objs as go
from utils import anchor_metrics
from utils import get_project_from_url, anchor_hover_label

def layout(tissue,cancertype,library,anchor,combintation,xaxis,yaxis,url,df):
    project = get_project_from_url(url)

    filtered_df = df[(df.project_id == project.id)]

    if(combintation):
        drug = combintation.split(" + ")
        lib_id = int(drug[0])
        anchor_id = int(drug[1])
        filtered_df = filtered_df[(filtered_df.library_id == lib_id) & (filtered_df.anchor_id == anchor_id)]

    else:
        if(library):
            filtered_df = filtered_df[filtered_df.library_id == library]
        if(anchor):
            filtered_df = filtered_df[filtered_df.anchor_id == anchor]

    if(tissue):
        filtered_df = filtered_df[filtered_df.tissue ==  tissue ]
    if(cancertype):
        filtered_df = filtered_df[filtered_df.cancer_type ==  cancertype ]

    print(anchor_hover_label(filtered_df))
    xaxis_data = filtered_df[xaxis]
    yaxis_data =  filtered_df[yaxis]
    x_title = anchor_metrics[xaxis]['label']
    y_title = anchor_metrics[yaxis]['label']

    fig = go.Figure(
        data=go.Scatter(
        x = xaxis_data,
        y = yaxis_data,
        mode='markers',
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

