#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time

import pandas as pd
import requests
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from db import engine, Base
from models import Model, Drug, Combination, MatrixResult, WellResult, \
    DoseResponseCurve, SingleAgentWellResult, Project

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


def upload_project(combo_matrix_stats_path: str,
                   combo_well_stats_path: str,
                   nlme_stats_path: str,
                   project_name: str):

    combo_matrix_stats = pd.read_csv(combo_matrix_stats_path)
    combo_well_stats = pd.read_csv(combo_well_stats_path)
    nlme_stats = pd.read_csv(nlme_stats_path)


    project = get_project(project_name)

    models = get_models_with_sidm(combo_matrix_stats)
    if models is not None and not models.empty:
        models_to_db(models)

    drugs = extract_drugs(combo_matrix_stats)
    drugs_to_db(drugs)

    drug_matrices = extract_drug_matrices(combo_matrix_stats)
    drug_matrices_to_db(drug_matrices)

    matrix_results = extract_matrix_results(combo_matrix_stats)
    matrix_results = add_model_id(matrix_results, models, 'cosmic_id')
    matrix_results = add_project_id(matrix_results, project)
    matrix_results_to_db(matrix_results)

    well_results = extract_well_results(combo_well_stats)
    well_results_to_db(well_results)

    dr_curves = extract_dose_response_curves(nlme_stats)
    dr_curves_to_db(dr_curves)

    sa_wells = extract_single_agent_wells(nlme_stats)
    sa_wells_to_db(sa_wells)


def get_project(project_name):
    db_p = session.query(Project).filter_by(name=project_name).first()
    if not db_p:
        db_p = Project(name=project_name)
        session.add(db_p)
        session.commit()
    return db_p


def get_models_with_sidm(combo_matrix_stats):
    models = extract_models(combo_matrix_stats)
    models = add_sidms(models)
    return models


def extract_models(combo_matrix_stats):
    models = combo_matrix_stats[["CELL_LINE_NAME"]].copy()

    for c in ["TISSUE", "CANCER_TYPE", 'MASTER_CELL_ID', 'COSMIC_ID']:
        if c in combo_matrix_stats.columns:
            models[c] = combo_matrix_stats[c]

    models = models.rename(columns={"CELL_LINE_NAME": "name"})
    models.columns = [c.lower() for c in models.columns]

    return models.drop_duplicates()


def get_new(model, df):
    db_models = pd.read_sql(session.query(model).statement, session.bind)
    if not db_models.empty:
        db_models = db_models[df.columns]

    # Make sure the column types match
    for col in db_models.columns:
        if col in df.columns:
            df[col] = df[col].astype(db_models[col].dtype)

    # new as in 'not yet in database'
    new = pd.concat([df, db_models, db_models], ignore_index=True, sort=True)\
        .drop_duplicates(keep=False)[df.columns]

    return new


def add_sidms(models: int, verbose: bool=False) -> pd.DataFrame:
    if verbose:
        print("Adding Sanger IDs from Passports...")
    models = models.copy()
    sidms = []
    pbar = tqdm(total=len(models))
    for m in models.itertuples():
        pbar.set_description(f"Processing {m.cosmic_id}")
        pbar.update(1)
        sidms.append(get_sidm(m.cosmic_id))

    del pbar
    models['id'] = sidms

    return models


def get_sidm(cosmic_id: int, retries: int = 3):
    attempt = 1
    while attempt < retries:
        resp = requests.get(
            f"https://api.cellmodelpassports.sanger.ac.uk/models/COSMIC_ID/"
            f"{cosmic_id}?fields[model]=id")
        attempt += 1

        if resp.status_code == 200:
            try:
                return resp.json()['data']['id']
            except json.decoder.JSONDecodeError as e:
                print(f"Error parsing {cosmic_id}'s response")
                continue
        elif resp.status_code == 404:
            print(f"{cosmic_id} not found")
            return None
        else:
            time.sleep(1)
            continue

    print(f"Max retries exceeded for {cosmic_id}")
    return None


def models_to_db(models):
    models = models.where((pd.notnull(models)), None)
    to_db(Model, models, append=True)


def to_db(model, df, append=False):
    print(f"Uploading {model.__tablename__}")

    df = get_new(model, df) if append else df
    engine.execute(
        model.__table__.insert(),
        df.drop_duplicates().to_dict('records')
    )
    return


def extract_drugs(combo_matrix_stats):
    l1 = get_drug_details(combo_matrix_stats, 'lib1')
    l2 = get_drug_details(combo_matrix_stats, 'lib2')
    return l1.append(l2).drop_duplicates()


def get_drug_details(cms, lib):
    lib_cols = [lib + '_drug_id', lib + '_drug_name', lib + '_target', lib + '_owner']
    return cms[lib_cols]\
        .drop_duplicates()\
        .rename(columns={c: c.lower()[len(lib) + 1:] for c in lib_cols})\
        .rename(columns={"drug_id": "id"})


def drugs_to_db(drugs):
    to_db(Drug, drugs, append=True)


def extract_drug_matrices(combo_matrix_stats):
    drug_matrix = combo_matrix_stats[["DRUGSET_ID", "cmatrix", "lib1",
                                      "lib1_drug_id", "lib2", "lib2_drug_id",
                                      "matrix_size"]]
    drug_matrix.columns = ["drugset_id", "cmatrix", "lib1_tag", "lib1_id",
                           "lib2_tag", "lib2_id", "matrix_size"]
    return drug_matrix.drop_duplicates()


def drug_matrices_to_db(drug_matrices):
    to_db(Combination, drug_matrices)


def extract_matrix_results(combo_matrix_stats):
    hsa_wells = [c for c in combo_matrix_stats.columns if c.startswith("HSA")]
    bliss_wells = [c for c in combo_matrix_stats.columns if c.startswith("Bliss")]

    matrix_results = combo_matrix_stats[
        ["COSMIC_ID", "DRUGSET_ID", "cmatrix", "BARCODE", 'combo_max_effect',
         'lib1_max_effect', 'lib2_max_effect'] + hsa_wells + bliss_wells]

    matrix_results = matrix_results.rename(
        columns={
            "COSMIC_ID": "cosmic_id",
            "DRUGSET_ID": "drugset_id",
            "BARCODE": "barcode",
            "HSA_excess_matrix": "HSA_excess",
            "HSA_excess_matrix_synergy_only": "HSA_excess_syn",
            "HSA_excess_synergistic_wells": "HSA_excess_well_count",
            "Bliss_excess_matrix": "Bliss_excess",
            "Bliss_excess_matrix_synergy_only": "Bliss_excess_syn",
            "Bliss_excess_synergistic_wells": "Bliss_excess_well_count",
            "HSA_window_excess": "HSA_excess_window",
            "HSA_window_dose1": "HSA_excess_window_dose_lib1",
            "HSA_window_dose2": "HSA_excess_window_dose_lib2",
            "HSA_so_window_excess": "HSA_excess_window_syn",
            "HSA_so_window_dose1": "HSA_excess_window_syn_dose_lib1",
            "HSA_so_window_dose2": "HSA_excess_window_syn_dose_lib2",
            "Bliss_window_excess": "Bliss_excess_window",
            "Bliss_window_dose1": "Bliss_excess_window_dose_lib1",
            "Bliss_window_dose2": "Bliss_excess_window_dose_lib2",
            "Bliss_so_window_excess": "Bliss_excess_window_syn",
            "Bliss_so_window_dose1": "Bliss_excess_window_syn_dose_lib1",
            "Bliss_so_window_dose2": "Bliss_excess_window_syn_dose_lib2",
            "HSA_window_size": "window_size"
        }
    )

    del matrix_results['Bliss_window_size']
    del matrix_results['Bliss_so_window_size']
    del matrix_results['HSA_so_window_size']

    return matrix_results


def add_model_id(df, models, model_id_field='cosmic_id'):
    res = df.merge(models[['id', model_id_field]], on=model_id_field)\
        .rename(columns={"id": "model_id"})
    del res[model_id_field]
    return res


def add_project_id(df, project):
    df['project_id'] = project.id
    return df


def matrix_results_to_db(matrix_results):
    to_db(MatrixResult, matrix_results)


def extract_well_results(combo_well_stats):

    columns = ['DRUGSET_ID', 'cmatrix', 'BARCODE', 'POSITION', 'lib1', 'lib1_dose',
               'lib1_conc', 'lib2','lib2_dose', 'lib2_conc', 'combo_viability', 'HSA',
               'HSA_excess', 'Bliss_additivity', 'Bliss_index', 'Bliss_excess',
               'lib1_equiv_dose', 'lib2_equiv_dose', 'Loewe_index']
    well_results = combo_well_stats[columns]\
        .rename(columns={
            "DRUGSET_ID": "drugset_id",
            "BARCODE": 'barcode',
            "POSITION": "position",
            "combo_viability": "viability",
            "lib1": "lib1_tag",
            "lib2": "lib2_tag"
        })

    return well_results


def well_results_to_db(well_results):
    to_db(WellResult, well_results)


def extract_dose_response_curves(nlme_stats):
    dr_curves = nlme_stats[
        ['fitted_treatment', 'treatment_type', 'BARCODE', 'cmatrix',
         'DRUGSET_ID', 'xmid', 'scal', 'RMSE', 'IC50', 'auc', 'Emax', 'maxc']
    ]\
        .drop_duplicates()
    dr_curves[['fixed_tag', 'fixed_dose', 'dosed_tag']] = \
        dr_curves.fitted_treatment.str.extract(
            '(?:(?P<fixed_tag>[A-Z][0-9]+)(?P<fixed_dose>D[0-9]+)-)?(?P<dosed_tag>[A-Z][0-9]+)$',
            expand=True)
    del dr_curves['fitted_treatment']

    dr_curves.columns = [c.lower() for c in dr_curves.columns]

    return dr_curves


def dr_curves_to_db(dr_curves):
    to_db(DoseResponseCurve, dr_curves)


def extract_single_agent_wells(nlme_stats):
    wells = nlme_stats.query("treatment_type == 'S'")[
        ['DRUGSET_ID', 'lib_drug', 'BARCODE', 'POSITION', 'dose', 'CONC',
         'viability']
    ]\
        .drop_duplicates()

    wells.columns = [c.lower() for c in wells.columns]

    assert len(wells) > 0, "No Single Agent Wells found in NLME Stats"
    return wells


def sa_wells_to_db(wells):
    to_db(SingleAgentWellResult, wells)


if __name__ == '__main__':

    combo_matrix_stats = "data/combo_matrix_statistics_GDSC_007-A_22Oct18_2049.csv"
    combo_well_stats = "data/combo_well_statistics_GDSC_007-A_22Oct18_1534.csv"
    nlme_stats = "data/nlme_stats_matrix_fit_GDSC_007-A_28Sep18_1543.csv.bz2"

    upload_project(combo_matrix_stats, combo_well_stats, nlme_stats, "GDSC_007")