import sqlalchemy as sa
import numpy as np
from sqlalchemy.orm import relationship
from sqlalchemy_utils import generic_repr
from db import Base


class ToDictMixin:
    def to_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in sa.inspection.inspect(obj).mapper.column_attrs}


@generic_repr
class Model(ToDictMixin, Base):
    __tablename__ = 'models'
    id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String)
    master_cell_id = sa.Column(sa.Integer)
    cosmic_id = sa.Column(sa.Integer)
    tissue = sa.Column(sa.String)
    cancer_type = sa.Column(sa.String)


@generic_repr
class Drug(ToDictMixin, Base):
    __tablename__ = 'drugs'
    id = sa.Column(sa.Integer, primary_key=True)
    drug_name = sa.Column(sa.String)
    target = sa.Column(sa.String)
    owner = sa.Column(sa.String)


@generic_repr
class DrugMatrix(ToDictMixin, Base):
    __tablename__ = 'drug_matrices'
    drugset_id = sa.Column(sa.Integer, primary_key=True)
    cmatrix = sa.Column(sa.Integer, primary_key=True)

    lib1_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), nullable=False,
                        index=True)
    lib2_id = sa.Column(sa.Integer, sa.ForeignKey(Drug.id), nullable=False,
                        index=True)
    matrix_size = sa.Column(sa.Integer)

    lib1_tag = sa.Column(sa.String)
    lib2_tag = sa.Column(sa.String)

    lib1 = relationship(Drug, foreign_keys=[lib1_id])
    lib2 = relationship(Drug, foreign_keys=[lib2_id])


@generic_repr
class MatrixResult(ToDictMixin, Base):
    __tablename__ = 'matrix_results'
    barcode = sa.Column(sa.Integer, nullable=False, primary_key=True)
    drugset_id = sa.Column(sa.Integer, nullable=False, primary_key=True)
    cmatrix = sa.Column(sa.Integer, nullable=False, primary_key=True)

    model_id = sa.Column(sa.String, sa.ForeignKey(Model.id), nullable=False,
                         index=True)
    HSA_excess = sa.Column(sa.Float)
    HSA_excess_syn = sa.Column(sa.Float)
    HSA_excess_well_count = sa.Column(sa.Integer)
    Bliss_excess = sa.Column(sa.Float)
    Bliss_excess_syn = sa.Column(sa.Float)
    Bliss_excess_well_count = sa.Column(sa.Integer)
    window_size = sa.Column(sa.Integer)
    HSA_excess_window = sa.Column(sa.Float)
    HSA_excess_window_dose_lib1 = sa.Column(sa.String)
    HSA_excess_window_dose_lib2 = sa.Column(sa.String)
    HSA_excess_window_syn = sa.Column(sa.Float)
    HSA_excess_window_syn_dose_lib1 = sa.Column(sa.String)
    HSA_excess_window_syn_dose_lib2 = sa.Column(sa.String)
    Bliss_excess_window = sa.Column(sa.Float)
    Bliss_excess_window_dose_lib1 = sa.Column(sa.String)
    Bliss_excess_window_dose_lib2 = sa.Column(sa.String)
    Bliss_excess_window_syn = sa.Column(sa.Float)
    Bliss_excess_window_syn_dose_lib1 = sa.Column(sa.String)
    Bliss_excess_window_syn_dose_lib2 = sa.Column(sa.String)

    drug_matrix = relationship("DrugMatrix")
    well_results = relationship("WellResult")
    combination_curves = relationship("DoseResponseCurve")
    model = relationship("Model")

    @property
    def single_agent_curves(self):
        return sa.orm.object_session(self).query(DoseResponseCurve)\
            .filter(
                DoseResponseCurve.barcode == self.barcode,
                DoseResponseCurve.treatment_type == 'S',
                DoseResponseCurve.dosed_tag.in_([
                    self.drug_matrix.lib1_tag,
                    self.drug_matrix.lib2_tag])
                ).all()

    @property
    def drugs(self):
        return {
            self.drug_matrix.lib1_tag: self.drug_matrix.lib1,
            self.drug_matrix.lib2_tag: self.drug_matrix.lib2
        }

    __table_args__ = (sa.ForeignKeyConstraint(
        [drugset_id, cmatrix], [DrugMatrix.drugset_id, DrugMatrix.cmatrix]), {}
    )


@generic_repr
class WellResult(ToDictMixin, Base):
    __tablename__ = 'well_results'
    id = sa.Column(sa.Integer, primary_key=True)
    barcode = sa.Column(sa.Integer, nullable=False)
    drugset_id = sa.Column(sa.Integer, nullable=False)
    cmatrix = sa.Column(sa.Integer, nullable=False)
    position = sa.Column(sa.Integer, nullable=False)
    lib1_dose = sa.Column(sa.String, nullable=False)
    lib1_conc = sa.Column(sa.Float, nullable=False)
    lib2_dose = sa.Column(sa.String, nullable=False)
    lib2_conc = sa.Column(sa.Float, nullable=False)
    viability = sa.Column(sa.Float)
    HSA = sa.Column(sa.Float)
    HSA_excess = sa.Column(sa.Float)
    Bliss_additivity = sa.Column(sa.Float)
    Bliss_index = sa.Column(sa.Float)
    Bliss_excess = sa.Column(sa.Float)
    lib1_equiv_dose = sa.Column(sa.Float)
    lib2_equiv_dose = sa.Column(sa.Float)
    Loewe_index = sa.Column(sa.Float)

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
    dose = sa.Column(sa.String, nullable=False)
    conc = sa.Column(sa.Float, nullable=False)
    viability = sa.Column(sa.Float, nullable=False)


@generic_repr
class DoseResponseCurve(ToDictMixin, Base):
    __tablename__ = 'dose_response_curves'
    id = sa.Column(sa.Integer, primary_key=True)
    barcode = sa.Column(sa.Integer, nullable=False)
    cmatrix = sa.Column(sa.Integer, nullable=True)
    drugset_id = sa.Column(sa.Integer, nullable=False)
    fixed_tag = sa.Column(sa.String, nullable=True)
    fixed_dose = sa.Column(sa.String, nullable=True)
    dosed_tag = sa.Column(sa.String, nullable=False)
    treatment_type = sa.Column(sa.String(1), nullable=False)
    maxc = sa.Column(sa.Float, nullable=False)
    rmse = sa.Column(sa.Float)
    ic50 = sa.Column(sa.Float)
    auc = sa.Column(sa.Float)
    emax = sa.Column(sa.Float)
    xmid = sa.Column(sa.Float)
    scal = sa.Column(sa.Float)

    matrix_result = relationship("MatrixResult", back_populates='combination_curves')

    __table_args__ = (sa.ForeignKeyConstraint(
        [drugset_id, cmatrix, barcode],
        [MatrixResult.drugset_id, MatrixResult.cmatrix, MatrixResult.barcode]),
                      {}
    )

    @property
    def single_agent_well_results(self):
        if self.treatment_type != 'S':
            return []

        return sa.orm.object_session(self).query(SingleAgentWellResult) \
            .filter(
                SingleAgentWellResult.drugset_id == self.drugset_id,
                SingleAgentWellResult.lib_drug == self.dosed_tag,
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