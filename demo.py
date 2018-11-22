import pandas as pd
import sqlalchemy as sa
from db import engine
from models import Model, Drug, Combination, MatrixResult, WellResult, DoseResponseCurve

session = sa.orm.sessionmaker(bind=engine)()

my_matrix = session.query(MatrixResult).first()

# Matrix Drugs
my_matrix.drugs

# Matrix Cell Line
my_matrix.model

# Matrix details
my_matrix.barcode
my_matrix.drugset_id
my_matrix.cmatrix

# Matrix summary stats
my_matrix.HSA_excess
my_matrix.HSA_excess_syn
my_matrix.HSA_excess_well_count
my_matrix.Bliss_excess
my_matrix.Bliss_excess_syn
my_matrix.Bliss_excess_well_count
my_matrix.window_size
my_matrix.HSA_excess_window
my_matrix.HSA_excess_window_dose_lib1
my_matrix.HSA_excess_window_dose_lib2
my_matrix.HSA_excess_window_syn
my_matrix.HSA_excess_window_syn_dose_lib1
my_matrix.HSA_excess_window_syn_dose_lib2
my_matrix.Bliss_excess_window
my_matrix.Bliss_excess_window_dose_lib1
my_matrix.Bliss_excess_window_dose_lib2
my_matrix.Bliss_excess_window_syn
my_matrix.Bliss_excess_window_syn_dose_lib1
my_matrix.Bliss_excess_window_syn_dose_lib2

# Matrix fitted curves
my_matrix.single_agent_curves
my_matrix.combination_curves

# Matrix wells
my_matrix.well_results


# make_dataframes if you want
wells = pd.DataFrame([w.to_dict() for w in my_matrix.well_results])
wells.head()

combination_curves = pd.DataFrame([c.to_dict()
                                   for c in my_matrix.combination_curves])
