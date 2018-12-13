import dash_html_components as html
import pandas as pd
import sqlalchemy as sa
from db import session

from models import Combination, Project, DoseResponseCurve
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
        DoseResponseCurve.ic50,
        DoseResponseCurve.barcode)\
        .filter(DoseResponseCurve.treatment_type == 'S', DoseResponseCurve.project_id == combination.project_id)\
        .filter(sa.or_(DoseResponseCurve.lib1_id == combination.lib1_id, DoseResponseCurve.lib1_id == combination.lib2_id)
                )

    all_dr_curves = pd.read_sql(dr_curves_query.statement, session.bind).rename(columns={'lib1_id' : 'drug_id'})

    all_matrices = pd.read_sql(combination.matrices.statement, session.bind) \
        .assign(**{'lib1_name': combination.lib1.drug_name,
                   'lib2_name': combination.lib2.drug_name}) \
        .merge(right=all_dr_curves, left_on=['barcode', 'lib1_id'], right_on=['barcode', 'drug_id']) \
        .merge(right=all_dr_curves, how='left', left_on=['barcode', 'lib2_id'], right_on=['barcode', 'drug_id'], suffixes=['_lib1', '_lib2']) \
        .merge(all_cell_models, left_on=['model_id'], right_on=['id'])\
        .drop(columns=['drug_id_lib1', 'drug_id_lib2'])

    return html.Div([
        crumbs([("Home", "/"), (project.name, f"/project/{project.slug}"),
                (f"{combination.lib1.drug_name} + {combination.lib2.drug_name}",)]),
        intro(combination),
        mm_plot(all_matrices)
    ])




