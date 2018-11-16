import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import numpy as np
import pandas as pd
import sqlalchemy as sa
import plotly.graph_objs as go

from app import app
from db import session
from models import MatrixResult, Project, Combination, Drug


def layout(project_slug):
    try:
        project = session.query(Project).filter_by(slug=project_slug).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    metrics = ["HSA_excess", "HSA_excess_syn", "HSA_excess_well_count",
               "HSA_excess_window", "HSA_excess_window_syn", "Bliss_excess",
               "Bliss_excess_syn", "Bliss_excess_well_count", "Bliss_excess_window",
               "Bliss_excess_window_syn"
               ]
    table_columns = ['model_id', 'cmatrix', 'barcode', 'drugset_id'] + metrics

    all_matrices = session.query(MatrixResult)\
        .join(Project)\
        .filter(Project.name == project.name)\
        .all()

    summary = pd.DataFrame([x.to_dict() for x in all_matrices])

    # Get the combination names for the project
    # ....
    def format_combo_links(combo):
        drug1 = session.query(Drug.drug_name).filter(Drug.id == combo.lib1_id).first()
        drug2 = session.query(Drug.drug_name).filter(Drug.id == combo.lib2_id).first()
        combo_string = (f"{drug1[0]} + {drug2[0]}")
        combo_ref = f"/combination/{drug1[0]}+{drug2[0]}"
        return(dcc.Link(combo_string, href=combo_ref))

    combo_links = [format_combo_links(combo) for combo in project.combinations]

    return html.Div([
        html.H2(f"{project.name} Overview"),
        html.Div(
            children=[
                html.Label('y-axis', htmlFor='y-axis-select-boxplot'),
                dcc.Dropdown(
                    options=[{'label': c, 'value': c} for c in metrics],
                    value='Bliss_excess',
                    id='y-axis-select-boxplot'
                )
            ],
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(
            children=[
                dcc.Graph(
                    id='project-boxplot'
                )
            ],
            style={'width': '75%', 'float': 'left'}
        ),
        html.Br(),
        html.H3("Drug combinations screened"),
        html.Div(
            #     Add selection for the combinations here - link to combination page.
            children=[
                html.Div(children =[
                    combo_link,
                    html.Br()])
                for combo_link in combo_links
            ]
        ),
        html.Div(
            children=[
                dt.DataTable(
                    rows=summary.to_dict('records'),
                    columns=table_columns,
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    editable=False,
                    id='datatable1_2'
                )
            ]

        ),
        html.Div(style={"display": "none"}, children=str(project.id),
                 id='project-id')
    ],
    style={'width':'100%'})


@app.callback(
    dash.dependencies.Output('project-boxplot', 'figure'),
    [dash.dependencies.Input('y-axis-select-boxplot', 'value'),
     dash.dependencies.Input('project-id', 'children')]
)
def update_boxplot(y_axis_field, project_id):

    all_matrices_query = session.query(MatrixResult) \
        .filter_by(project_id=int(project_id))

    summary = pd.read_sql(all_matrices_query.statement, all_matrices_query.session.bind)

    ds = []
    cmatrix = []
    lib1 = []
    lib2 = []
    lib_names = []
    cm = []

    for matrix in all_matrices_query.all():
        ds.append(matrix.drugset_id)
        cmatrix.append(matrix.cmatrix)
        lib1.append(matrix.drug_matrix.lib1.drug_name)
        lib2.append(matrix.drug_matrix.lib2.drug_name)
        lib_names.append(f"{matrix.drug_matrix.lib1.drug_name} {matrix.drug_matrix.lib2.drug_name}")
        cm.append(f"{matrix.drugset_id}::{matrix.cmatrix}")

    lib_names_df = pd.DataFrame({
        'drugset_id' : ds,
        'cmatrix' : cmatrix,
        'lib1_name' : lib1,
        'lib2_name' : lib2,
        'lib_names' : lib_names,
        'cm' : cm
    }).drop_duplicates()

    summary = pd.merge(lib_names_df, summary, "right")

    return {
        'data': [
            go.Box(
                # name=str(cm),
                name=np.array2string(summary.query("cm == @cm")['lib_names'].unique()),
                y=summary.query("cm == @cm")[y_axis_field],
                opacity=0.7,
                boxpoints='all',
                jitter=0.3,
                marker=dict(
                    size=4,
                    opacity=0.5
                ),
                customdata=[{"to": f"/matrix/{row.barcode}/{row.cmatrix}"}
                            for row in summary.query("cm == @cm").itertuples(index=False)]
            ) for cm in summary.cm.unique()
        ],
        'layout': go.Layout(
            height=700,
            margin=dict(l=40, r=30, b=80, t=100),
            showlegend=False,
            yaxis={'type': 'log' if 'index' in y_axis_field else 'linear',
                   'title': y_axis_field.replace('_', ' ')}
        )
    }

# @app.callback(
#     dash.dependencies.Output('combos-screened', 'figure'),
#     [dash.dependencies.Input('project-id', 'children')]
# )
# def update_combos_screened(project_id):
#     # Get all the combos for the project
#     return html.Div([
#         dcc.link('foo')
#     ])


if __name__ == '__main__':
    app.run_server(debug=True)
