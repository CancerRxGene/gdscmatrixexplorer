import sqlalchemy as sa
import numpy as np
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr

from components.dr_plot import DoseResponsePlot
from db import Base, session


class ToDictMixin:
    def to_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in sa.inspection.inspect(obj).mapper.column_attrs}


@generic_repr
class Project(ToDictMixin, Base):
    __tablename__ = 'projects'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True)
    slug = sa.Column(sa.String, unique=True)
    matrices = relationship("MatrixResult", back_populates='project')
    dose_responses = relationship("DoseResponseCurve")
    combinations = relationship("Combination", lazy='dynamic', back_populates='project')

    @property
    def models(self):
        return sa.orm.object_session(self).query(Model).join(MatrixResult) \
            .filter(
            MatrixResult.project_id == self.id,
        ).distinct().all()


@generic_repr
class Model(ToDictMixin, Base):
    __tablename__ = 'models'
    id = sa.Column(sa.String, primary_key=True)
    cell_line_name = sa.Column(sa.String)
    master_cell_id = sa.Column(sa.Integer)
    cosmic_id = sa.Column(sa.Integer)
    tissue = sa.Column(sa.String)
    cancer_type = sa.Column(sa.String)
    name = sa.orm.synonym(cell_line_name)


@generic_repr
class Drug(ToDictMixin, Base):
    __tablename__ = 'drugs'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    target = sa.Column(sa.String)
    pathway = sa.Column(sa.String)
    owner = sa.Column(sa.String)


@generic_repr
class Combination(ToDictMixin, Base):
    __tablename__ = 'combinations'
    project_id = sa.Column(sa.Integer, sa.ForeignKey(Project.id), primary_key=True, index=True)
    lib1_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), primary_key=True, index=True)
    lib2_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), primary_key=True, index=True)

    lib1 = relationship(Drug, foreign_keys=[lib1_id])
    lib2 = relationship(Drug, foreign_keys=[lib2_id])

    matrices = relationship("MatrixResult", lazy='dynamic', back_populates='combination')
    project = relationship("Project", back_populates='combinations')

    @property
    def replicates_query(self):
        return sa.orm.object_session(self).query(Combination) \
            .filter(
             sa.or_(
                sa.and_(
                    Combination.lib1_id == self.lib1_id,
                    Combination.lib2_id == self.lib2_id,
                ),
                sa.and_(
                    Combination.lib1_id == self.lib2_id,
                    Combination.lib2_id == self.lib1_id,
                )
        ))

    @property
    def models(self):
        return sa.orm.object_session(self).query(Model) \
            .join(MatrixResult, Combination)\
            .filter(
                Combination.project_id == self.project_id,
                Combination.lib1_id == self.lib1_id,
                Combination.lib2_id == self.lib2_id)\
            .all()

    @property
    def replicates(self):
        return self.replicates_query.all()

    @classmethod
    def get(cls, project_id, lib1_id, lib2_id):
        return session.query(Combination) \
            .filter_by(lib1_id=lib1_id, lib2_id=lib2_id,
                       project_id=project_id) \
            .one()

    @property
    def url(self):
        return (f"/project/{self.project.slug}/combination/"
                f"{self.lib1_id}+{self.lib2_id}")


@generic_repr
class MatrixResult(ToDictMixin, Base):
    __tablename__ = 'matrix_results'
    barcode = sa.Column(sa.Integer, nullable=False, primary_key=True)
    drugset_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    cmatrix = sa.Column(sa.Integer, nullable=False, primary_key=True)

    lib1_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), nullable=False, index=True)
    lib2_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), nullable=False, index=True)

    lib1_tag = sa.Column(sa.String, nullable=False)
    lib2_tag = sa.Column(sa.String, nullable=False)

    model_id = sa.Column(sa.String, sa.ForeignKey(Model.id), nullable=False,
                         index=True)
    project_id = sa.Column(sa.Integer, sa.ForeignKey(Project.id),
                           nullable=False, index=True)

    hsa_synergistic_wells = sa.Column(sa.Integer)
    hsa_matrix = sa.Column(sa.Float)
    hsa_matrix_so = sa.Column(sa.Float)
    hsa_window_size = sa.Column(sa.Integer)
    hsa_window = sa.Column(sa.Float)
    hsa_window_dose1 = sa.Column(sa.String)
    hsa_window_dose2 = sa.Column(sa.String)
    hsa_window_so = sa.Column(sa.Float)
    hsa_window_so_dose1 = sa.Column(sa.String)
    hsa_window_so_dose2 = sa.Column(sa.String)

    bliss_synergistic_wells = sa.Column(sa.Integer)
    bliss_matrix = sa.Column(sa.Float)
    bliss_matrix_so = sa.Column(sa.Float)
    bliss_window_size = sa.Column(sa.Integer)
    bliss_window = sa.Column(sa.Float)
    bliss_window_dose1 = sa.Column(sa.String)
    bliss_window_dose2 = sa.Column(sa.String)
    bliss_window_so = sa.Column(sa.Float)
    bliss_window_so_dose1 = sa.Column(sa.String)
    bliss_window_so_dose2 = sa.Column(sa.String)

    combo_maxe = sa.Column(sa.Float)
    lib1_maxe = sa.Column(sa.Float)
    lib2_maxe = sa.Column(sa.Float)
    delta_maxe_lib1 = sa.Column(sa.Float)
    delta_maxe_lib2 = sa.Column(sa.Float)
    delta_combo_maxe_day1 = sa.Column(sa.Float)

    day1_viability_mean = sa.Column(sa.Float)
    day1_intensity_mean = sa.Column(sa.Float)
    day1_inhibition_scale = sa.Column(sa.Float)
    growth_rate = sa.Column(sa.Float)
    doubling_time = sa.Column(sa.Float)

    combination = relationship("Combination", back_populates='matrices',
                               primaryjoin="and_(Combination.project_id == MatrixResult.project_id, "
                                           "Combination.lib1_id == MatrixResult.lib1_id, "
                                           "Combination.lib2_id == MatrixResult.lib2_id)",
                               viewonly=True)

    project = relationship("Project", back_populates='matrices')

    well_results = relationship("WellResult")
    model = relationship("Model")

    @property
    def single_agent_curves(self):
        return sa.orm.object_session(self).query(DoseResponseCurve)\
            .filter(
                DoseResponseCurve.barcode == self.barcode,
                # Must match on tag in case multiple tags in ds for the same drug id,
                DoseResponseCurve.tag.in_([
                    self.lib1_tag,
                    self.lib2_tag
                ])).all()

    @property
    def drugs(self):
        return {
            self.combination.lib1_id: self.combination.lib1,
            self.combination.lib2_id: self.combination.lib2
        }

    @property
    def project_replicates_query(self):
        return sa.orm.object_session(self).query(MatrixResult)\
            .filter(MatrixResult.model_id == self.model_id)\
            .filter(MatrixResult.project_id == self.project_id)\
            .filter(MatrixResult.lib1_id == self.lib1_id)\
            .filter(MatrixResult.lib2_id == self.lib2_id)

    @property
    def project_replicates(self):
        return self.project_replicates_query.all()


    @property
    def all_replicates_query(self):
        subq = self.combination.replicates_query.subquery()
        al_reps = sa.orm.aliased(Combination, subq)

        return sa.orm.object_session(self).query(MatrixResult)\
            .join(Combination) \
            .filter(
                sa.and_(
                    Combination.project_id == al_reps.project_id,
                    Combination.lib1_id == al_reps.lib1_id,
                    Combination.lib2_id == al_reps.lib2_id
                ))\
            .filter(MatrixResult.model_id == self.model_id)

    @property
    def all_replicates(self):
        return self.all_replicates_query.all()


    __table_args__ = (
        sa.ForeignKeyConstraint(
            [project_id, lib1_id, lib2_id], [Combination.project_id, Combination.lib1_id, Combination.lib2_id]), {}
    )


@generic_repr
class WellResult(ToDictMixin, Base):
    __tablename__ = 'well_results'
    id = sa.Column(sa.Integer, primary_key=True)
    barcode = sa.Column(sa.Integer, nullable=False)
    drugset_id = sa.Column(sa.Integer, nullable=False)
    cmatrix = sa.Column(sa.Integer, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)
    lib1_tag = sa.Column(sa.String, nullable=False)
    lib1_dose = sa.Column(sa.String, nullable=False)
    lib1_conc = sa.Column(sa.Float, nullable=False)
    lib2_tag = sa.Column(sa.String, nullable=False)
    lib2_dose = sa.Column(sa.String, nullable=False)
    lib2_conc = sa.Column(sa.Float, nullable=False)
    inhibition = sa.Column(sa.Float)
    hsa = sa.Column(sa.Float)
    hsa_excess = sa.Column(sa.Float)
    bliss_additivity = sa.Column(sa.Float)
    bliss_excess = sa.Column(sa.Float)

    matrix_result = relationship("MatrixResult", back_populates='well_results')

    __table_args__ = (sa.ForeignKeyConstraint(
        [drugset_id, cmatrix, barcode],
        [MatrixResult.drugset_id, MatrixResult.cmatrix, MatrixResult.barcode]),
                      {}
    )


@generic_repr
class SingleAgentWellResult(ToDictMixin, Base):
    __tablename__ = 'single_agent_well_results'
    id = sa.Column(sa.Integer, primary_key=True)
    barcode = sa.Column(sa.Integer, nullable=False)
    drugset_id = sa.Column(sa.Integer, nullable=False)
    lib_drug = sa.Column(sa.String, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)
    viability = sa.Column(sa.Float, nullable=False)
    dose = sa.Column(sa.String, nullable=True)
    conc = sa.Column(sa.Float, nullable=False)


@generic_repr
class DoseResponseCurve(ToDictMixin, Base):
    __tablename__ = 'dose_response_curves'
    id = sa.Column(sa.Integer, primary_key=True)
    barcode = sa.Column(sa.Integer, nullable=False)
    drugset_id = sa.Column(sa.Integer, nullable=False)
    project_id = sa.Column(sa.Integer, sa.ForeignKey(Project.id), nullable=False, index=True)
    drug_id_lib = sa.Column(sa.Integer, nullable=False, index=True)
    tag = sa.Column(sa.String, nullable=False)
    maxc = sa.Column(sa.Float, nullable=False)
    minc = sa.Column(sa.Float, nullable=True)
    rmse = sa.Column(sa.Float)
    ic50 = sa.Column(sa.Float)
    auc = sa.Column(sa.Float)
    maxe = sa.Column(sa.Float)
    xmid = sa.Column(sa.Float)
    scal = sa.Column(sa.Float)

    @property
    def matrix_results(self):
        return sa.orm.object_session(self).query(MatrixResult) \
            .filter(MatrixResult.barcode == self.barcode)\
            .filter(sa.or_(MatrixResult.lib1_tag == self.tag,
                           MatrixResult.lib2_tag == self.tag))\
            .all()

    @property
    def well_results(self):
        return sa.orm.object_session(self).query(SingleAgentWellResult) \
            .filter(
                SingleAgentWellResult.drugset_id == self.drugset_id,
                SingleAgentWellResult.lib_drug == self.tag,
                SingleAgentWellResult.barcode == self.barcode
            ).all()

    def x_to_conc(self, x):
        try:
            return self.maxc * np.power(2, (x - 9)) / 1000000
        except ValueError:
            x = float(x)
            return self.maxc * np.power(2, (x - 9)) / 1000000

    def conc_to_x(self, conc):
        conc = conc * 1000000
        return (np.log(conc / self.maxc) / np.log(2)) + 9

    def nlme_model(self, x):
        return 1 - (1 / (1 + np.exp(-(x - self.xmid) / self.scal)))

    def y_hat(self, x):
        return self.nlme_model(x)

    def plot(self, *args, **kwargs):
        return DoseResponsePlot(self, *args, **kwargs).plot()
