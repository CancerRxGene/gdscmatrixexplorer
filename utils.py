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
    'Bliss_excess': {
        'label': 'Bliss Excess',
        'description': 'Average Bliss excess',
        'value': 'Bliss_excess'
    },
    'Bliss_excess_syn': {
        'label': 'Bliss excess synergy',
        'description': 'Average Bliss excess synergistic wells',
        'value': 'Bliss_excess_syn'
    },
    'Bliss_excess_window': {
        'label': 'Bliss excess 3x3 window',
        'description': 'Average Bliss excess of the highest 3x3 window',
        'value': 'Bliss_excess_window'
    },
    'Bliss_excess_window_syn': {
        'label': 'Bliss excess 3x3 window synergy',
        'description': 'Average Bliss excess of highest 3x3 window counting only synergistic wells',
        'value': 'Bliss_excess_window_syn'
    },
    'HSA_excess': {
        'label': 'HSA excess',
        'description': 'Average HSA excess',
        'value': 'HSA_excess'
    },
    'HSA_excess_syn': {
        'label': 'HSA excess synergy',
        'description': 'Average HSA excess eynergistic wells',
        'value': 'HSA_excess_syn'
    },
    'HSA_excess_window': {
        'label': 'HSA excess 3x3 window',
        'description': 'Average HSA Excess of the highest 3x3 window',
        'value': 'HSA_excess_window'
    },
    'HSA_excess_window_syn': {
        'label': 'HSA excess 3x3 window synergy',
        'description': 'Average HSA excess of highest 3x3 window counting only synergistic wells',
        'value': 'HSA_excess_window_syn'
    },
    'combo_max_effect': {
        'label': 'Max effect combination',
        'description': 'Maximum inhibition observed in combination',
        'value': 'combo_max_effect'
    },
    'lib1_max_effect': {
        'label': 'Max effect drug 1',
        'description': 'Maximum inhibition observed in drug 1',
        'value': 'lib1_max_effect'
    },
    'lib2_max_effect': {
        'label': 'Max effect drug 2',
        'description': 'Maximum inhibition observed in drug 2',
        'value': 'lib2_max_effect'
    },
    'lib1_delta_max_effect': {
        'label': 'Delta max effect drug 1',
        'description': 'Max effect combination minus max effect drug1',
        'value': 'lib1_delta_max_effect'
    },
    'lib2_delta_max_effect': {
        'label': 'Delta max effect drug 2',
        'description': 'Max effect combination minus max effect drug2',
        'value': 'lib2_delta_max_effect'
    },
}

well_metrics = {
    'HSA':
        {'label': "HSA",
         'value': "HSA"},
    'HSA_excess':
        {'label': "HSA excess",
         'value': "HSA_excess"},
    'Bliss_additivity':
        {'label': "Bliss additivity",
         'value': "Bliss_additivity"},
    'Bliss_index':
        {'label': "Bliss index",
         'value': "Bliss_index"},
    'Bliss_excess':
        {'label': "Bliss excess",
         'value': "Bliss_excess"},
    'Loewe_index':
        {'label': "Loewe index",
         'value': "Loewe_index"}
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
    text = f"{combination.lib1.drug_name} + {combination.lib2.drug_name}"
    return dcc.Link(text, href=combination.url)


@lru_cache()
def get_combination_results_with_sa(combination):
    all_cell_models = pd.read_sql_table('models', session.bind)

    # We need the single agent IC50s for the MM plot
    dr_curves_query = session.query(
        models.DoseResponseCurve.drug_id_lib,
        models.DoseResponseCurve.tag,
        models.DoseResponseCurve.ic50,
        models.DoseResponseCurve.barcode,
        models.DoseResponseCurve.minc,
        models.DoseResponseCurve.maxc
    ) \
        .filter(models.DoseResponseCurve.project_id == combination.project_id) \
        .filter(sa.or_(models.DoseResponseCurve.drug_id_lib == combination.lib1_id,
                       models.DoseResponseCurve.drug_id_lib == combination.lib2_id)
                )
    all_dr_curves = pd.read_sql(dr_curves_query.statement, session.bind).rename(
        columns={'lib1_id': 'drug_id'})

    combo_matrices = pd.read_sql(combination.matrices.statement, session.bind) \
        .assign(**{'lib1_name': combination.lib1.drug_name,
                   'lib2_name': combination.lib2.drug_name}) \
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
