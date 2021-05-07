#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
!!! Run this program using gdscmatrixexplorer/cli.py !!!
'''

import json
import re
import time

import pandas as pd
import requests
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from db import engine, Base
from models import Model, Drug, Combination, MatrixResult, WellResult, \
    DoseResponseCurve, SingleAgentWellResult, Project, AnchorCombi, AnchorSynergy

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

    project = get_project(project_name,'matrix')

    add_new_models(combo_matrix_stats)
    models = pd.read_sql(session.query(Model).statement, session.bind)

    add_new_drugs(combo_matrix_stats)

    drug_matrices = extract_drug_matrices(combo_matrix_stats)
    drug_matrices = add_project_id(drug_matrices, project)

    drug_matrices_to_db(drug_matrices)
    matrix_results = extract_matrix_results(combo_matrix_stats, 'MASTER_CELL_ID')
    matrix_results = add_model_id(matrix_results, models, 'master_cell_id')
    matrix_results = add_project_id(matrix_results, project)
    matrix_results_to_db(matrix_results)

    valid_barcodes = set(matrix_results.barcode)

    well_results = extract_well_results(combo_well_stats)
    well_results = well_results[well_results.barcode.isin(valid_barcodes)]
    well_results_to_db(well_results)

    dr_curves = extract_dose_response_curves(combo_matrix_stats, nlme_stats)
    dr_curves = dr_curves[dr_curves.barcode.isin(valid_barcodes)]
    dr_curves = add_project_id(dr_curves, project)
    dr_curves_to_db(dr_curves)

    sa_wells = extract_single_agent_wells(nlme_stats)
    sa_wells = sa_wells[sa_wells.barcode.isin(valid_barcodes)]
    sa_wells_to_db(sa_wells)


def get_project(project_name, project_type):
    db_p = session.query(Project).filter_by(name=project_name).first()
    if not db_p:
        slug = '-'.join([c.lower() for c in re.split("[, \-!?:_]+", project_name)])
        db_p = Project(name=project_name, slug=slug, combination_type = project_type)
        session.add(db_p)
        session.commit()
    return db_p


def add_new_models(combo_matrix_stats):
    models = extract_models(combo_matrix_stats)
    new_models = get_new(Model, models)
    new_models = add_sidms(new_models, 'MASTER_CELL_ID', 'master_cell_id')
    new_models = new_models[pd.notna(new_models.id)]
    if not new_models.empty:
        models_to_db(new_models)

def extract_models(combo_matrix_stats):
    models = combo_matrix_stats[["CELL_LINE_NAME"]].copy()

    for c in ["TISSUE", "CANCER_TYPE", 'MASTER_CELL_ID', 'COSMIC_ID']:
        if c in combo_matrix_stats.columns:
            if c.endswith("ID"):
                models[c] = combo_matrix_stats[c].astype(int)
            else:
                models[c] = combo_matrix_stats[c]

    models.columns = [c.lower() for c in models.columns]

    return models.drop_duplicates()


def get_new(model, df):
    db_models = pd.read_sql(session.query(model).statement, session.bind)
    if not db_models.empty:
        db_models = db_models[df.columns].copy()

    # Make sure the column types match
    for col in db_models.columns:
        if col in df.columns:
            if db_models[col].dtype == 'object':
                df[col] = df[col].astype(str)
            else:
                df[col] = df[col].astype(db_models[col].dtype)

    # new as in 'not yet in database'
    new = pd.concat([db_models, db_models, df], ignore_index=True, sort=False)\
        .drop_duplicates(keep=False)[df.columns]

    return new


def add_sidms(models: pd.DataFrame, identifier_type: str, identifier_column: str, verbose: bool=False) -> pd.DataFrame:
    if verbose:
        print("Adding Sanger IDs from Passports...")
    models = models.copy()
    sidms = []
    pbar = tqdm(total=len(models))
    for m in models.itertuples():
        pbar.set_description(f"Processing {getattr(m, identifier_column):>10}")
        pbar.update(1)
        sidms.append(get_sidm(getattr(m, identifier_column), identifier_type))

    del pbar
    models['id'] = sidms

    return models


def get_sidm(identifier: int, identifier_type:str, retries: int = 3):
    if identifier is None:
        return None

    attempt = 1
    while attempt < retries:
        resp = requests.get(
            f"https://api.cellmodelpassports.sanger.ac.uk/models/{identifier_type}/"
            f"{identifier}?fields[model]=id")
        attempt += 1

        if resp.status_code == 200:
            try:
                return resp.json()['data']['id']
            except json.decoder.JSONDecodeError as e:
                print(f"Error parsing {identifier}'s response")
                continue
        elif resp.status_code == 404:
            print(f"{identifier} not found")
            return None
        else:
            time.sleep(1)
            continue

    print(f"Max retries exceeded for {identifier}")
    return None


def models_to_db(models):
    models = models.where((pd.notnull(models)), None)
    upsert(Model, models)


def upsert(model, df):
    assert 'id' in df.columns, "Upsert requires an 'id'-column in df"
    print(f"Updating {model.__tablename__}")
    for row in df.itertuples():
        in_db = session.query(model).get(row.id)
        if not in_db:
            in_db = model()
            in_db.id = row.id
            session.add(in_db)
        for column in model.__table__.columns:
            try:
                setattr(in_db, column.key, getattr(row, column.key))
            except AttributeError:
                continue
    session.commit()


def upsert_new(model, df):
    assert 'id' in df.columns, "Upsert requires an 'id'-column in df"
    print(f"Updating {model.__tablename__}")
    for row in df.itertuples():
        in_db = model(**row._asdict())
        session.merge(in_db)


def add_new_drugs(combo_matrix_stats):
    drugs = extract_drugs(combo_matrix_stats)
    new_drugs = get_new(Drug, drugs)
    upsert(Drug, new_drugs)


def extract_drugs(combo_matrix_stats):
    l1 = get_drug_details(combo_matrix_stats, 'lib1')
    l2 = get_drug_details(combo_matrix_stats, 'lib2')
    return l1.append(l2).drop_duplicates()


def get_drug_details(cms, lib):
    lib_cols = [lib + '_ID', lib + '_name', lib + '_target', lib + '_pathway', lib + '_owner']
    return cms[lib_cols]\
        .drop_duplicates()\
        .rename(columns={c: c.lower()[len(lib) + 1:] for c in lib_cols})\
        .rename(columns={"drug_id": "id"})


def extract_drug_matrices(combo_matrix_stats):
    drug_matrix = combo_matrix_stats[["lib1", "lib1_ID", "lib2", "lib2_ID", "matrix_size"]]
    drug_matrix.columns = ["lib1_tag", "lib1_id", "lib2_tag", "lib2_id", "matrix_size"]
    return drug_matrix.drop_duplicates()


def drug_matrices_to_db(drug_matrices):
    to_db(Combination, drug_matrices)


def to_db(model, df, append=False):
    print(f"Uploading {model.__tablename__}")

    df.columns = [c.lower() for c in df.columns]

    df = get_new(model, df) if append else df
    engine.execute(
        model.__table__.insert(),
        df.drop_duplicates().to_dict('records')
    )
    session.commit()
    return

def extract_matrix_results(combo_matrix_stats, id_mapper):
    hsa_cols = [c for c in combo_matrix_stats.columns if c.startswith("HSA")]
    bliss_cols = [c for c in combo_matrix_stats.columns if c.startswith("Bliss")]
    max_effect_cols = [c for c in combo_matrix_stats.columns if c.endswith("MaxE")]
    day1_cols = [c for c in combo_matrix_stats.columns if c.startswith("day1")]

    matrix_results = combo_matrix_stats[
        [id_mapper, "DRUGSET_ID", "cmatrix", "BARCODE",
         'lib1_ID', 'lib2_ID',
         'lib1', 'lib2',
         'Delta_MaxE_lib1', 'Delta_MaxE_lib2'] +
        max_effect_cols +
        hsa_cols +
        bliss_cols +
        day1_cols +
        ["growth_rate", "doubling_time", "Delta_combo_MaxE_day1"]
    ].copy()

    matrix_results.columns = [c.lower() for c in matrix_results.columns]
    matrix_results.rename(columns={'lib1': 'lib1_tag', 'lib2': 'lib2_tag'}, inplace=True)

    return matrix_results

def add_model_id(df, models, model_id_field='cosmic_id'):
    res = df.merge(models[['id', model_id_field]], on=model_id_field, how='inner')\
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
               'lib1_conc', 'lib2', 'lib2_dose', 'lib2_conc', 'inhibition', 'HSA',
               'HSA_excess', 'Bliss_additivity', 'Bliss_excess']
    well_results = combo_well_stats[columns]\
        .rename(columns={
            "lib1": "lib1_tag",
            "lib2": "lib2_tag",
        })
    well_results.columns = [c.lower() for c in well_results.columns]
    return well_results


def well_results_to_db(well_results):
    to_db(WellResult, well_results)


def extract_dose_response_curves(matrix_stats, nlme_stats):

    lib1_details = matrix_stats[['BARCODE', 'DRUGSET_ID', 'lib1', 'lib1_ID', 'lib1_MaxE']].drop_duplicates()
    lib1_details.columns = ['BARCODE', 'DRUGSET_ID', 'tag', 'drug_id_lib', 'maxe']

    lib2_details = matrix_stats[
        ['BARCODE', 'DRUGSET_ID', 'lib2', 'lib2_ID', 'lib2_MaxE']].drop_duplicates()
    lib2_details.columns = ['BARCODE', 'DRUGSET_ID', 'tag', 'drug_id_lib', 'maxe']

    drug_details = lib1_details.append(lib2_details, sort=False).drop_duplicates()

    dr_curves = nlme_stats[
        ['BARCODE', 'DRUGSET_ID', 'xmid', 'scal', 'RMSE', 'IC50', 'auc', 'maxc', 'lib_drug'] # STILL NEED MINC
    ]\
        .drop_duplicates()\
        .rename(columns={'lib_drug': 'tag'})\
        .merge(drug_details, on=['BARCODE', 'DRUGSET_ID', 'tag'])

    dr_curves['minc'] = dr_curves.maxc / 1000  # TODO: resolve temporary minc fix

    dr_curves.columns = [c.lower() for c in dr_curves.columns]

    return dr_curves


def dr_curves_to_db(dr_curves):
    to_db(DoseResponseCurve, dr_curves)


def extract_single_agent_wells(nlme_stats):
    wells = nlme_stats[['DRUGSET_ID', 'lib_drug', 'BARCODE', 'POSITION', 'y', 'x_micromol']]\
        .rename(columns={"y": "inhibition", "x_micromol": "conc"})\
        .drop_duplicates()

    wells.columns = [c.lower() for c in wells.columns]

    assert len(wells) > 0, "No Single Agent Wells found in NLME Stats"
    return wells


def sa_wells_to_db(wells):
    to_db(SingleAgentWellResult, wells)

def upload_anchor(anchor_combi_path: str, anchor_synergy_path: str, project_name: str):
    anchor_combi = pd.read_csv(anchor_combi_path)
    anchor_synergy = pd.read_csv(anchor_synergy_path)
    project = get_project(project_name, 'anchor')

    upload_anchor_new_models(anchor_combi)
    upload_anchor_new_drugs(anchor_combi)
    upload_combinations(anchor_combi, project.id)

    #add proejct id to anchor combi df
    anchor_combi['project_id'] = project.id
    upload_anchor_combi(anchor_combi)

    #add project id to synergy df
    anchor_synergy['project_id'] = project.id
    upload_anchor_synergy(anchor_synergy)

def upload_anchor_new_models(anchor_combi_df):
    print(f"Uploading models")
    # get all the models from input, only need relevant columns
    models_details = anchor_combi_df[
        ['CELL_LINE_NAME', 'MASTER_CELL_ID', 'COSMIC_ID', 'SIDM', 'tissue', 'cancer_type']].drop_duplicates()

    # get models in db
    model_q = session.query(Model)
    model_df = pd.read_sql(model_q.statement, session.bind)
    models_in_db = model_df['id']

    count = 0
    for m in models_details['SIDM']:
        if (m not in models_in_db.values):
            count = count + 1
            model = models_details[models_details.SIDM == m]

            # for integer, it is numpy.int64,  need to convert into standard int, add .item() at the end
            # e.g cosmic id = model.COSMIC_ID.iat[0].item()
            new_model = Model(id=model.SIDM.iat[0], master_cell_id=model.MASTER_CELL_ID.iat[0].item(),
                              cosmic_id=model.COSMIC_ID.iat[0].item(), tissue=model.tissue.iat[0],
                              cancer_type=model.cancer_type.iat[0], cell_line_name=model.CELL_LINE_NAME.iat[0])
            session.add(new_model)
            session.commit()

    print('There are ' + str(count) + ' new models')

def upload_anchor_new_drugs(anchor_combi_df):
    print(f"Uploading drugs")
    lib_drugs = anchor_combi_df[['LIBRARY_ID','LIBRARY_NAME','LIBRARY_TARGET','LIBRARY_TARGET_PATHWAY']].drop_duplicates()

    # inplace=True to keep the new columns in the df
    lib_drugs.rename(columns={"LIBRARY_ID":"id",
                                 "LIBRARY_NAME":"name",
                                 "LIBRARY_TARGET":"target",
                                 "LIBRARY_TARGET_PATHWAY":"pathway"
                                 }
                        , inplace=True)

    anchor_drugs = anchor_combi_df[['ANCHOR_ID',
                                    'ANCHOR_NAME',
	                                'ANCHOR_TARGET',
                                    'ANCHOR_TARGET_PATHWAY']].drop_duplicates()

    anchor_drugs.rename(columns={ "ANCHOR_ID":"id",
                                  "ANCHOR_NAME": "name",
                                  "ANCHOR_TARGET":"target",
                                  "ANCHOR_TARGET_PATHWAY":"pathway"
                                  }, inplace=True)

    all_drugs = lib_drugs.append(anchor_drugs).drop_duplicates()

    new_drugs = get_new(Drug, all_drugs)

    upsert(Drug, new_drugs)

def upload_combinations(anchor_combi_df, project_id):
    print(f"Uploading combinations")
    combinations  = anchor_combi_df[['LIBRARY_ID','ANCHOR_ID']].drop_duplicates()
    combinations.rename(columns={
                    "LIBRARY_ID":"lib1_id",
                    "ANCHOR_ID":"lib2_id"
    }, inplace=True)

    combinations['project_id'] = project_id

    for c in combinations.itertuples():
        new_combination = Combination(
            project_id = c.project_id,
            lib1_id = c.lib1_id,
            lib2_id = c.lib2_id
        )
        session.add(new_combination)
    session.commit()

def upload_anchor_combi(anchor_combi_df):
    to_db(AnchorCombi,anchor_combi_df)

def upload_anchor_synergy(anchor_synergy_df):
    to_db(AnchorSynergy,anchor_synergy_df)

if __name__ == '__main__':
    print("!!! Run this program using gdscmatrixexplorer/cli.py !!!")