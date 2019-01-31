import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

from app import app
from db import session
from models import MatrixResult, Model


def generate_model_dropdown(model_list: pd.DataFrame,
                            title="Other models",
                            subtitle="(for the same combination)",
                            max_tissue_width=10):
    return html.Div(
        className='mb-4',
        children=[
            dcc.Location('models-dropdown-url'),
            html.H5(title, className='mb-1'),
            html.Span(subtitle),
            dcc.Dropdown(options=[
                {'label': f"{m.name} ({m.tissue if len(m.tissue) < max_tissue_width else m.tissue[:max_tissue_width - 2] + '...'})",
                 'value': f"{m.barcode}__{m.cmatrix}"}
                for m in model_list.itertuples()
            ], id='dropdown-models', className='mt-2')

        ])


def generate_combos_dropdown(combos: dict):
    return html.Div(
        className='mb-4',
        children=[
            dcc.Location('combos-dropdown-url'),
            html.H5("Other Combinations", className='mb-1'),
            html.Span("(for the same cell line)"),
            dcc.Dropdown(options=[
                {'label': k,
                 'value': v}
                for k, v in combos.items()
            ], id='dropdown-combos', className='mt-2')

        ])


def model_links_from_matrix(matrix):

    other_model_matrices_query = session.query(MatrixResult.barcode, MatrixResult.cmatrix, MatrixResult.model_id, Model.name, Model.tissue)\
        .filter(MatrixResult.model_id == Model.id)\
        .filter(MatrixResult.model_id != matrix.model_id)\
        .filter_by(drugset_id=matrix.drugset_id, cmatrix=matrix.cmatrix)

    unique_models = get_unique_models_from_matrices_query(other_model_matrices_query)
    return generate_model_dropdown(unique_models)


def model_links_from_combo(combination):
    model_matrices_query = combination.matrices.join(Model)\
        .with_entities(MatrixResult.barcode, MatrixResult.cmatrix,
                       MatrixResult.model_id, Model.name, Model.tissue)
    unique_models = get_unique_models_from_matrices_query(model_matrices_query)
    return generate_model_dropdown(unique_models, title="Select cell line",
                                   subtitle='(Navigates to most recent replicate)',
                                   max_tissue_width=50)


def get_unique_models_from_matrices_query(matrices_query):

    return pd.read_sql(matrices_query.statement,
                              con=session.bind)\
        .sort_values('barcode', ascending=False)\
        .drop_duplicates(subset=['model_id'])\
        .sort_values('name')


def combo_links_from_matrix(matrix):

    other_combos = session.query(MatrixResult)\
        .filter(MatrixResult.model_id == matrix.model_id)\
        .order_by(MatrixResult.barcode.desc())\
        .all()

    dropdown_items = {f"{c.combination.lib1.drug_name} + {c.combination.lib2.drug_name}": f"{c.barcode}__{c.cmatrix}"
                      for c in other_combos if c not in matrix.all_replicates}

    return generate_combos_dropdown(dropdown_items)


def url_from_dropdown_value(value):
    barcode, cmatrix = value.split('__')
    return f"/matrix/{barcode}/{cmatrix}"


@app.callback(dash.dependencies.Output('models-dropdown-url', 'pathname'),
              [dash.dependencies.Input('dropdown-models', 'value')])
def dropdown_handler(dropdown_models_value):
    return url_from_dropdown_value(dropdown_models_value)


@app.callback(dash.dependencies.Output('combos-dropdown-url', 'pathname'),
              [dash.dependencies.Input('dropdown-combos', 'value')])
def dropdown_handler(dropdown_combos_value):
    return url_from_dropdown_value(dropdown_combos_value)
