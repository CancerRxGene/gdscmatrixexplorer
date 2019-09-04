import math
import re
from functools import lru_cache

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import func

from db import session
import models


class Colors:
    LIGHTGREEN = "rgb(117,171,61)"
    LEAFGREEN = "rgb(85,164,112)"
    BROWNORANGE = "rgb(177,150,64)"
    RUST = "rgb(196,118,67)"
    PINKPURPLE = "rgb(194,93,186)"
    PINKPURPLE_LIGHT = "rgb(223,170,218)"
    PINKPURPLE_TRANS = "rgba(194,93,186,0.6)"
    DARKPINK = "rgb(199,89,128)"
    DEEPDARKBLUE = "rgb(117,97,207)"
    DEEPDARKBLUE_LIGHT = "rgb(225, 222, 239)"
    DEEPDARKBLUE_TRANS = "rgba(117,97,207,0.6)"
    DEEPDARKBLUE_ULTRATRANS = "rgba(117,97,207,0.2)"
    FLATDARKBLUE = "rgb(127,128,197)"
    LIGHTBLUE = "rgb(69,176,207)"
    RED = "rgb(208,76,66)"
    RED_LIGHT = "rgb(241,205,203)"
    RED_TRANS = "rgb(208,76,66, 0.6)"
    DARKGREY = "rgb(51,46,44)"
    DARKGREY_LIGHT = "rgb(204,202,202)"
    DARKGREY_TRANS = "rgba(51,46,44,0.6)"
    DARKGREY_SUPERLIGHT = "rgb(222,222,222)"
    DARKGREY_SUPERTRANS = "rgba(51,46,44,0.2)"
    DARKGREY_ULTRALIGHT = "rgb(246, 246, 246)"
    DARKGREY_ULTRATRANS = "rgba(51,46,44,0.05)"


matrix_metrics = {
    'bliss_matrix': {
        'label': 'Bliss Excess',
        'description': 'Average Bliss excess',
        'value': 'bliss_matrix'
    },
    'bliss_matrix_so': {
        'label': 'Bliss excess synergy',
        'description': 'Average Bliss excess synergistic wells',
        'value': 'bliss_matrix_so'
    },
    'bliss_window': {
        'label': 'Bliss excess 3x3 window',
        'description': 'Average Bliss excess of the highest 3x3 window',
        'value': 'bliss_window'
    },
    'bliss_window_so': {
        'label': 'Bliss excess 3x3 window synergy',
        'description': 'Average Bliss excess of highest 3x3 window counting only synergistic wells',
        'value': 'bliss_window_so'
    },
    'hsa_matrix': {
        'label': 'HSA excess',
        'description': 'Average HSA excess',
        'value': 'hsa_matrix'
    },
    'hsa_matrix_so': {
        'label': 'HSA excess synergy',
        'description': 'Average HSA excess eynergistic wells',
        'value': 'hsa_matrix_so'
    },
    'hsa_window': {
        'label': 'HSA excess 3x3 window',
        'description': 'Average HSA Excess of the highest 3x3 window',
        'value': 'hsa_window'
    },
    'hsa_window_so': {
        'label': 'HSA excess 3x3 window synergy',
        'description': 'Average HSA excess of highest 3x3 window counting only synergistic wells',
        'value': 'hsa_window_so'
    },
    'combo_maxe': {
        'label': 'MaxE combination',
        'description': 'Maximum inhibition observed in combination',
        'value': 'combo_maxe'
    },
    'lib1_maxe': {
        'label': 'MaxE drug 1',
        'description': 'Maximum inhibition observed in drug 1',
        'value': 'lib1_maxe'
    },
    'lib2_maxe': {
        'label': 'MaxE drug 2',
        'description': 'Maximum inhibition observed in drug 2',
        'value': 'lib2_maxe'
    },
    'delta_maxe_lib1': {
        'label': 'Delta MaxE drug 1',
        'description': 'MaxE combination minus MaxE drug1',
        'value': 'delta_maxe_lib1'
    },
    'delta_maxe_lib2': {
        'label': 'Delta MaxE drug 2',
        'description': 'MaxE combination minus MaxE drug2',
        'value': 'delta_maxe_lib2'
    },
}

well_metrics = {
    'hsa':
        {'label': "HSA (null model)",
         'value': "hsa"},
    'hsa_excess':
        {'label': "HSA excess",
         'value': "hsa_excess"},
    'bliss_additivity':
        {'label': "Bliss additivity (null model)",
         'value': "bliss_additivity"},
    'bliss_excess':
        {'label': "Bliss excess",
         'value': "bliss_excess"},
}


plot_colors = ["rgb(215,150,209)", "rgb(164,250,201)", "rgb(245,167,221)",
               "rgb(124,191,134)", "rgb(220,173,241)", "rgb(168,199,127)",
               "rgb(195,186,255)", "rgb(201,176,105)", "rgb(39,200,238)",
               "rgb(241,169,124)", "rgb(101,231,214)", "rgb(255,193,233)",
               "rgb(163,255,221)", "rgb(212,162,112)", "rgb(109,180,217)",
               "rgb(252,209,141)", "rgb(56,189,186)", "rgb(255,194,162)",
               "rgb(177,249,255)", "rgb(204,162,160)", "rgb(214,255,202)",
               "rgb(222,206,255)", "rgb(122,185,149)", "rgb(255,209,192)",
               "rgb(172,168,198)", "rgb(255,250,203)", "rgb(196,166,142)",
               "rgb(197,237,225)", "rgb(170,175,138)", "rgb(255,235,208)"]

synergy_colorscale = [
                [0.0, 'rgb(0, 0, 255)'],
                [0.1, 'rgb(51, 51, 255)'],
                [0.2, 'rgb(102,102,255)'],
                [0.3, 'rgb(153, 153, 255)'],
                [0.4, 'rgb(204, 204, 255)'],
                [0.5, 'rgb(255, 255, 255)'],
                [0.6, 'rgb(255, 204, 204)'],
                [0.7, 'rgb(255, 153, 153)'],
                [0.8, 'rgb(255, 102, 102)'],
                [0.9, 'rgb(255, 51, 51)'],
                [1.0, 'rgb(230, 0, 0)']
    ]

inhibition_colorscale = [
    [0.0, 'rgb(0,0,255)'],
    [0.1, 'rgb(90,0,237)'],
    [0.2, 'rgb(127,0,217)'],
    [0.3, 'rgb(155,0,194)'],
    [0.4, 'rgb(177,0,170)'],
    [0.5,'rgb(186,0,158)'],
    [0.6, 'rgb(196,0,144)'],
    [0.7, 'rgb(213,0,118)'],
    [0.8, 'rgb(229,0,87)'],
    [0.9, 'rgb(243,0,53)'],
    [1.0, 'rgb(255,0,0)'],
]

viability_colorscale = [
    [0.0, 'rgb(255,0,0)'],
    [0.1, 'rgb(243,0,53)'],
    [0.2, 'rgb(229,0,87)'],
    [0.3, 'rgb(213,0,118)'],
    [0.4, 'rgb(196,0,144)'],
    [0.5, 'rgb(186,0,158)'],
    [0.6, 'rgb(177,0,170)'],
    [0.7, 'rgb(155,0,194)'],
    [0.8, 'rgb(127,0,217)'],
    [0.9, 'rgb(90,0,237)'],
    [1.0, 'rgb(0,0,255)'],
]

@lru_cache(20)
def get_metric_min_max(metric):
    return session.query(
        func.min(getattr(models.WellResult, metric)).label('min_val'),
        func.max(getattr(models.WellResult, metric)).label('max_val'))\
        .one()


def get_metric_axis_range(metric):
    min_val, max_val = get_metric_min_max(metric)
    try:
        return math.floor(min_val * 10) / 10, math.ceil(max_val * 10) / 10
    except OverflowError:
        return -1 if 'Loewe' not in metric else 0, 1


def url_is_combination_page(url):
    return url_parser(url) == 'combination'


def url_parser(url):
    if re.fullmatch("/project/[a-zA-Z0-9\-]*/combination/[0-9]*\+[0-g]*", url):
        return 'combination'
    elif re.fullmatch("/project/[a-zA-Z0-9\-]*", url):
        return 'project'
    elif re.fullmatch("/matrix/\d*/\d*", url):
        return 'matrix'
    elif re.fullmatch("/documentation", url):
        return 'documentation'
    elif re.fullmatch('/downloads', url):
        return 'downloads'
    elif re.fullmatch("/", url):
        return 'home'


@lru_cache()
def get_project_metrics(project_id, metric):
    project_matrix_metrics_query = session\
        .query(
            getattr(models.MatrixResult, metric))\
        .filter(models.MatrixResult.project_id == project_id)

    project_matrix_metrics = pd.read_sql(
        project_matrix_metrics_query.statement, session.bind)
    return project_matrix_metrics


@lru_cache()
def get_matrix_from_url(url):
    if not url.startswith("/matrix"):
        return None

    segments = url.split("/")
    if len(segments) < 4:
        return None

    barcode = segments[2]
    cmatrix = segments[3]

    try:
        matrix = session.query(models.MatrixResult) \
            .filter_by(barcode=barcode, cmatrix=cmatrix).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Matrix not found")
    return matrix


@lru_cache()
def get_project_from_url(url):
    if not url.startswith("/project"):
        return None

    segments = url.split("/")
    project_slug = segments[2]

    try:
        project = session.query(models.Project).filter_by(slug=project_slug).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")
    return project


@lru_cache()
def get_combination_from_url(url):
    if not url.startswith("/project"):
        return None

    search = re.search("/project/([a-zA-Z0-9\-]*)/combination/([0-9]*)\+([0-g]*)", url)
    if search:
        project_slug, drug1_id, drug2_id = search.groups()

    try:
        combination = session.query(models.Combination)\
            .join(models.Project)\
            .filter(models.Project.slug == project_slug)\
            .filter(models.Combination.lib1_id == drug1_id)\
            .filter(models.Combination.lib2_id == drug2_id)\
            .one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Combination not found")
    except sa.orm.exc.MultipleResultsFound:
        return html.Div("Multiple results found for this combination - cannot display")

    return combination


def get_combination_link(combination):
    text = f"{combination.lib1.name} + {combination.lib2.name}"
    return dcc.Link(text, href=combination.url)


@lru_cache()
def get_combination_results_with_sa(combination):
    all_cell_models = pd.read_sql_table('models', session.bind)\
        .rename(columns={'cell_line_name': 'model_name'})

    # We need the single agent IC50s for the MM plot
    dr_curves_query = session.query(
        models.DoseResponseCurve.drug_id_lib,
        models.DoseResponseCurve.tag,
        models.DoseResponseCurve.ic50,
        models.DoseResponseCurve.barcode,
        models.DoseResponseCurve.minc,
        models.DoseResponseCurve.maxc,
        models.Drug.name,
        models.Drug.target
    ) \
        .filter(models.Drug.id == models.DoseResponseCurve.drug_id_lib) \
        .filter(models.DoseResponseCurve.project_id == combination.project_id) \
        .filter(sa.or_(models.DoseResponseCurve.drug_id_lib == combination.lib1_id,
                       models.DoseResponseCurve.drug_id_lib == combination.lib2_id)
                )
    all_dr_curves = pd.read_sql(dr_curves_query.statement, session.bind).rename(
        columns={'lib1_id': 'drug_id'})

    combo_matrices = pd.read_sql(combination.matrices.statement, session.bind) \
        .assign(**{'lib1_name': combination.lib1.name,
                   'lib2_name': combination.lib2.name}) \
        .merge(right=all_dr_curves, left_on=['barcode', 'lib1_tag'],
               right_on=['barcode', 'tag']) \
        .merge(right=all_dr_curves, how='left', left_on=['barcode', 'lib2_tag'],
               right_on=['barcode', 'tag'], suffixes=['_lib1', '_lib2']) \
        .merge(all_cell_models, left_on=['model_id'], right_on=['id']) \
        .drop(columns=['tag_lib1', 'tag_lib2'])

    return combo_matrices


@lru_cache()
def get_combination_matrices_summary(project_id, lib1_id, lib2_id, percentiles):
    percentiles = list(percentiles)
    query = session.query(models.MatrixResult) \
        .filter(models.MatrixResult.project_id == project_id) \
        .filter(models.MatrixResult.lib1_id == lib1_id) \
        .filter(models.MatrixResult.lib2_id == lib2_id)
    return pd.read_sql(query.statement, session.get_bind())\
        .describe(percentiles=percentiles)


def get_all_tissues():
    return [s[0] for s in session.query(models.Model.tissue).distinct().order_by(models.Model.tissue).all()]


def get_all_cancer_types():
    return [s[0] for s in session.query(models.Model.cancer_type).distinct().order_by(models.Model.cancer_type).all()]



def matrix_hover_label_from_obj(m):
    return f"{m.combination.lib1.name} ({m.combination.lib1.target}) + {m.combination.lib2.name} ({m.combination.lib2.target})<br />" \
        f"Cell line: {m.model.cell_line_name}<br />"\
        f"Tissue: {m.model.tissue}"


def matrix_hover_label_from_tuple(s):
    return f"{s.name_lib1} ({s.target_lib1}) - {s.name_lib2} ({s.target_lib2})<br />"\
    f"Cell line: {s.model_name}<br />"\
    f"Tissue: {s.tissue}"


def matrix_hover_label(matrix):
    if isinstance(matrix, models.MatrixResult):
        return matrix_hover_label_from_obj(matrix)
    elif isinstance(matrix, tuple):
        return matrix_hover_label_from_tuple(matrix)
    elif isinstance(matrix, list):
        return [matrix_hover_label(m) for m in matrix]
    elif isinstance(matrix, pd.DataFrame):
        return [matrix_hover_label(m) for m in matrix.itertuples()]


def add_label_vars(plot_data):
    all_drugs = pd.read_sql_table('drugs', session.bind)
    all_models = pd.read_sql_table('models', session.bind)\
        .rename(columns={'cell_line_name': 'model_name'})

    plot_data = plot_data.merge(all_drugs, left_on='lib1_id', right_on='id') \
        .merge(all_drugs, left_on='lib2_id', right_on='id',
               suffixes=['_lib1', '_lib2']) \
        .merge(all_models, left_on='model_id', right_on='id')

    return plot_data

float_formatter = lambda x: f"{x:.3e}"
