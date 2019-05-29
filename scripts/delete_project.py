from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from models import Model, Drug, Combination, MatrixResult, WellResult, \
    DoseResponseCurve, SingleAgentWellResult, Project

from db import engine
Session = sessionmaker(bind=engine)
session = Session()


def delete_by_barcodes(model, barcodes):

    session.query(model).filter(model.barcode.in_(barcodes)).delete(synchronize_session=False)


def delete_project_barcodes(barcodes):

    def delete_pb(model):
        delete_by_barcodes(model, barcodes)

    return delete_pb


def delete_project(name):

    project = session.query(Project).filter_by(name=name).one()

    if not project:
        raise NoResultFound(f"No project found with name {name}")


    project_barcodes = {b[0] for b in session.query(MatrixResult.barcode.distinct()).filter(MatrixResult.project == project).all()}

    model_barcode_deleter = delete_project_barcodes(project_barcodes)

    model_barcode_deleter(DoseResponseCurve)
    model_barcode_deleter(SingleAgentWellResult)
    model_barcode_deleter(WellResult)
    model_barcode_deleter(MatrixResult)

    session.query(Combination).filter(Combination.project == project).delete(synchronize_session=False)

    drugs_in_use = {i for combo in session.query(Combination.lib1_id, Combination.lib2_id).distinct().all() for i in combo}
    session.query(Drug).filter(Drug.id.notin_(drugs_in_use)).delete(synchronize_session=False)

    models_in_use = {m[0] for m in session.query(MatrixResult.model_id).distinct().all()}
    session.query(Model).filter(Model.id.notin_(models_in_use)).delete(synchronize_session=False)

    session.delete(project)

    session.commit()

