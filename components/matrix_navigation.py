import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from db import session
from models import MatrixResult, Model, Combination


def replicate_links(matrix):

    link_text = lambda x: f"Barcode {x.barcode} ({x.project.name}) {'*' if x.HSA_excess > 0 else ''}"

    children = []
    for rep in sorted(matrix.all_replicates, key=lambda x: x.barcode):
        if rep != matrix:
            children.append(dcc.Link(link_text(rep), href=f"/matrix/{rep.barcode}/{rep.cmatrix}"))
            children.append((html.Br()))
        else:
            children.append(html.Span(link_text(rep)))
            children.append((html.Br()))

    return html.Div( className="mb-4", children=
        [html.H5('Replicates')] +
        children
    )


def links_to_other_models(matrix):

    other_model_matrices_query = session.query(MatrixResult.barcode, MatrixResult.cmatrix, MatrixResult.model_id, Model.name, Model.tissue)\
        .filter(MatrixResult.model_id == Model.id)\
        .filter(MatrixResult.model_id != matrix.model_id)\
        .filter_by(drugset_id=matrix.drugset_id, cmatrix=matrix.cmatrix)

    df_matrices = pd.read_sql(other_model_matrices_query.statement,
                              con=session.bind)\
        .sort_values('barcode')\
        .drop_duplicates(subset=['model_id'])\
        .sort_values('name')

    return html.Div(
        className='mb-4',
        children=[
            html.H5("Other models", className='mb-1'),
            html.Span("(for the same combination)"),
            dcc.Dropdown(options=[
                {'label': f"{m.name} ({m.tissue if len(m.tissue) < 10 else m.tissue[:8] + '...'})",
                 'value': f"{m.barcode}__{m.cmatrix}"}
                for m in df_matrices.itertuples()
            ], id='dropdown-models')

        ])


def links_to_other_combos(matrix):

    other_combos = session.query(MatrixResult)\
        .filter(MatrixResult.model_id == matrix.model_id)\
        .order_by(MatrixResult.barcode.desc())\
        .all()

    dropdown_items = {f"{c.combination.lib1.drug_name} + {c.combination.lib2.drug_name}": f"{c.barcode}__{c.cmatrix}"
                      for c in other_combos if c not in matrix.all_replicates}

    return html.Div(
        className='mb-4',
        children=[
            html.H5("Other Combinations", className='mb-1'),
            html.Span("(for the same cell line)"),
            dcc.Dropdown(options=[
                {'label': k,
                 'value': v}
                for k, v in dropdown_items.items()
            ], id='dropdown-combos')

        ])

