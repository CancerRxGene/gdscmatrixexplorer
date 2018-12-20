import dash_html_components as html
import pandas as pd
import sqlalchemy as sa
from db import session

from models import Combination, Project, DoseResponseCurve, MatrixResult
from components.combination_intro import layout as intro
from components.combination_mm_plot import layout as mm_plot
from components.breadcrumbs import breadcrumb_generator as crumbs


def layout(project_slug, combination_drug_ids=None):

    drug1_id, drug2_id = combination_drug_ids.split("+")
    try:
        combination = session.query(Combination)\
            .join('matrices', 'project')\
            .filter(Combination.lib1_id == drug1_id,
                    Combination.lib2_id == drug2_id)\
            .filter(Project.slug == project_slug)\
            .one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Combination not found")
    except sa.orm.exc.MultipleResultsFound:
        return html.Div("Multiple results found for this combination - cannot display")

    try:
        project = session.query(Project).filter_by(slug=project_slug).one()
    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    all_cell_models = pd.read_sql_table('models', session.bind)

    # We need the single agent IC50s for the MM plot
    dr_curves_query = session.query(
        DoseResponseCurve.lib1_id,
        DoseResponseCurve.dosed_tag,
        DoseResponseCurve.ic50,
        DoseResponseCurve.barcode)\
        .filter(DoseResponseCurve.treatment_type == 'S', DoseResponseCurve.project_id == combination.project_id)\
        .filter(sa.or_(DoseResponseCurve.lib1_id == combination.lib1_id,
                       DoseResponseCurve.lib1_id == combination.lib2_id)
                )

    all_dr_curves = pd.read_sql(dr_curves_query.statement, session.bind).rename(columns={'lib1_id' : 'drug_id'})

    combo_matrices = pd.read_sql(combination.matrices.statement, session.bind) \
        .assign(**{'lib1_name': combination.lib1.drug_name,
                   'lib2_name': combination.lib2.drug_name}) \
        .merge(right=all_dr_curves, left_on=['barcode', 'lib1_tag'], right_on=['barcode', 'dosed_tag']) \
        .merge(right=all_dr_curves, how='left', left_on=['barcode', 'lib2_tag'], right_on=['barcode', 'dosed_tag'], suffixes=['_lib1', '_lib2']) \
        .merge(all_cell_models, left_on=['model_id'], right_on=['id'])\
        .drop(columns=['dosed_tag_lib1', 'dosed_tag_lib2'])

    project_matrix_metrics = session.query(MatrixResult.Bliss_excess,
                                 MatrixResult.Bliss_excess_syn,
                                 MatrixResult.Bliss_excess_window,
                                 MatrixResult.Bliss_excess_window_syn,
                                 MatrixResult.HSA_excess,
                                 MatrixResult.HSA_excess_syn,
                                 MatrixResult.HSA_excess_window,
                                 MatrixResult.HSA_excess_window_syn,
                                 MatrixResult.combo_max_effect,
                                 MatrixResult.lib1_max_effect,
                                 MatrixResult.lib2_max_effect).filter(MatrixResult.project_id == combination.project_id)

    project_matrix_metrics = pd.read_sql(project_matrix_metrics.statement, session.bind)

    return html.Div([
        crumbs([("Home", "/"), (project.name, f"/project/{project.slug}"),
                (f"{combination.lib1.drug_name} + {combination.lib2.drug_name}",)]),
        intro(combination),
        mm_plot(combo_matrices, project_matrix_metrics)
    ])




