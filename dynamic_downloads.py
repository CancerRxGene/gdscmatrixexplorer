from flask import abort
import pandas as pd
from sqlalchemy.orm.exc import NoResultFound
from db import session
from models import Project, MatrixResult, Drug, Model, Combination, WellResult


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

    query = session.query(Project, MatrixResult, Combination, Model)\
        .join(MatrixResult).join(Combination).join(Model)\
        .filter(Project.slug == project_slug)
    df = pd.read_sql(query.statement, session.get_bind())
    df.to_csv(STATIC_PATH + f"/{project_slug}_matrix_results.csv.gz",
              compression='gzip', index=False)

    return True