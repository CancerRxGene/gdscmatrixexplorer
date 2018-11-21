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
            DoseResponseCurve.dosed_tag,
            DoseResponseCurve.ic50,
            DoseResponseCurve.barcode) \
        .filter(
            DoseResponseCurve.treatment_type == 'S',
            DoseResponseCurve.dosed_tag.in_([
                combination.lib1_tag,
                combination.lib2_tag]),
            DoseResponseCurve.drugset_id == combination.drugset_id
        )

    all_dr_curves = pd.read_sql(dr_curves_query.statement, session.bind)

    all_matrices = pd.read_sql(combination.matrices.statement, session.bind)\
        .assign(**{'lib1_tag': combination.lib1_tag,
                   'lib2_tag': combination.lib2_tag,
                   'lib1_name': combination.lib1.drug_name,
                   'lib2_name': combination.lib2.drug_name})\
        .merge(all_dr_curves, left_on=['barcode', 'lib1_tag'],
               right_on=['barcode', 'dosed_tag'])\
        .merge(all_dr_curves, left_on=['barcode', 'lib2_tag'],
               right_on=['barcode', 'dosed_tag'], suffixes=['_lib1', '_lib2'])\
        .merge(all_cell_models, left_on=['model_id'], right_on=['id'])

    return html.Div([
        crumbs([("Home", "/"), (project.name, f"/project/{project.slug}"),
                (f"{combination.lib1.drug_name} + {combination.lib2.drug_name}",)]),
        intro(combination),
        mm_plot(all_matrices)
    ])




