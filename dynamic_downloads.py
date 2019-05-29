from flask import abort
import pandas as pd
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from sqlalchemy.orm.exc import NoResultFound
from db import session
from models import Project, MatrixResult, Drug, Model, Combination, WellResult, \
    DoseResponseCurve


def generate_download_file(project_slug, download_type):
    if download_type == 'well_results':
        return generate_well_results(project_slug)
    elif download_type == 'matrix_results':
        return generate_matrix_results(project_slug)


def generate_well_results(project_slug):
    from app import STATIC_PATH

    try:
        session.query(Project).filter_by(slug=project_slug).one()
    except NoResultFound:
        return abort(404)

    query = session.query(Project, MatrixResult, WellResult, Combination, Model) \
        .join(MatrixResult)\
        .join(WellResult).join(Combination, MatrixResult.combination).join(Model) \
        .filter(Project.slug == project_slug)
    df = pd.read_sql(query.statement, session.get_bind())
    df.to_csv(STATIC_PATH + f"/{project_slug}_well_results.csv.gz",
              compression='gzip', index=False)

    return True


def generate_matrix_results(project_slug):
    from app import STATIC_PATH

    try:
        session.query(Project).filter_by(slug=project_slug).one()
    except NoResultFound:
        return abort(404)

    drug_alias = aliased(Drug, name='lib2')
    curve_alias = aliased(DoseResponseCurve, name='drlib2')

    query = session.query(Project, MatrixResult, Model, Drug,
                          drug_alias, DoseResponseCurve, curve_alias)\
        .join(MatrixResult).join(Model) \
        .join(Drug, MatrixResult.lib1_id == Drug.id) \
        .join(drug_alias, MatrixResult.lib2_id == drug_alias.id) \
        .join(DoseResponseCurve, and_(MatrixResult.barcode == DoseResponseCurve.barcode,
                                    MatrixResult.lib1_tag == DoseResponseCurve.tag,
                                    MatrixResult.drugset_id == DoseResponseCurve.drugset_id))\
      .join(curve_alias, and_(MatrixResult.barcode == curve_alias.barcode,
                              MatrixResult.lib1_tag == curve_alias.tag,
                              MatrixResult.drugset_id == curve_alias.drugset_id))\
        .filter(Project.slug == project_slug)\
        .with_entities(MatrixResult.barcode, MatrixResult.drugset_id,
                       MatrixResult.cmatrix, Model.cell_line_name, Model.master_cell_id,
                       Model.cosmic_id, Model.id, Model.tissue, Model.cancer_type,
                       MatrixResult.lib1_tag, MatrixResult.lib1_id, Drug.name,
                       DoseResponseCurve.minc, DoseResponseCurve.maxc,
                       DoseResponseCurve.rmse, DoseResponseCurve.maxe,
                       DoseResponseCurve.ic50, Drug.target, Drug.pathway, Drug.owner,
                       MatrixResult.lib2_tag, MatrixResult.lib2_id, drug_alias.name,
                       curve_alias.minc, curve_alias.maxc, curve_alias.rmse,
                       curve_alias.maxe, curve_alias.ic50, drug_alias.target,
                       drug_alias.pathway, drug_alias.owner,
                       MatrixResult.combo_maxe, MatrixResult.delta_maxe_lib1,
                       MatrixResult.delta_maxe_lib2, MatrixResult.delta_combo_maxe_day1,
                       MatrixResult.bliss_synergistic_wells, MatrixResult.bliss_matrix,
                       MatrixResult.bliss_matrix_so,
                       MatrixResult.bliss_window_size, MatrixResult.bliss_window, MatrixResult.bliss_window_dose1, MatrixResult.bliss_window_dose2,
                       MatrixResult.bliss_window_so, MatrixResult.bliss_window_so_dose1, MatrixResult.bliss_window_so_dose2,
                       MatrixResult.hsa_synergistic_wells, MatrixResult.hsa_matrix, MatrixResult.hsa_matrix_so,
                       MatrixResult.hsa_window, MatrixResult.hsa_window_dose1, MatrixResult.hsa_window_dose2,
                       MatrixResult.hsa_window_so, MatrixResult.hsa_window_so_dose1, MatrixResult.hsa_window_so_dose2,
                       MatrixResult.day1_intensity_mean,
                       MatrixResult.day1_viability_mean,
                       MatrixResult.day1_inhibition_scale, MatrixResult.growth_rate,
                       MatrixResult.doubling_time)
    df = pd.read_sql(query.statement, session.get_bind())

    df.columns = \
        ["BARCODE", "DRUGSET_ID", "cmatrix", "CELL_LINE_NAME", "MASTER_CELL_ID",
         "COSMIC_ID", "SIDM", "TISSUE", "CANCER_TYPE",
         "lib1_tag", "lib1_ID", "lib1_name", "lib1_minc", "lib1_maxc", "lib1_RMSE", "lib1_MaxE",
         "lib1_IC50_ln", "lib1_target", "lib1_pathway", "lib1_owner",
         "lib2_tag", "lib2_ID", "lib2_name", "lib2_minc", "lib2_maxc", "lib2_RMSE", "lib2_MaxE",
         "lib2_IC50_ln", "lib2_target", "lib2_pathway", "lib2_owner",
         "combo_MaxE", "Delta_MaxE_lib1", "Delta_MaxE_lib2", "Delta_combo_MaxE_day1",
         "Bliss_synergistic_wells", "Bliss_matrix", "Bliss_matrix_SO",
         "window_size", "Bliss_window", "Bliss_window_dose1", "Bliss_window_dose2",
         "Bliss_window_SO", "Bliss_window_SO_dose1", "Bliss_window_SO_dose2",
         "HSA_synergistic_wells", "HSA_matrix", "HSA_matrix_SO", "HSA_window", "HSA_window_dose1",
         "HSA_window_dose2", "HSA_window_SO", "HSA_window_SO_dose1",
         "HSA_window_SO_dose2", "day1_intensity_mean", "day1_viability_mean", "day1_inhibition_scale",
         "growth_rate", "doubling_time"]
    df.to_csv(STATIC_PATH + f"/{project_slug}_matrix_results.csv.gz",
              compression='gzip', index=False)

    return True