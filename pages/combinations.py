import dash_html_components as html
import pandas as pd

from db import session

from models import Drug, Combination, MatrixResult
from components.combination_intro import layout as intro
from components.combination_mm_plot import layout as mm_plot
from components.breadcrumbs import breadcrumb_generator as crumbs

def layout(combination=None):
    #     Select combination - dropdown?
    #     Infobox for select combination - names, targets etc...
    #     Michael Menden plot for all cell lines link to selected cell line
    #     Synergy metric dropdown for MM plot
    #     Link from plot to replicates for cell line and then link to matrix page

    drug1, drug2 = combination.split("+")

    drug1 = session.query(Drug).filter(Drug.id == drug1).first()
    drug2 = session.query(Drug).filter(Drug.id == drug2).first()

    # for mm plot need all IC50s and all synergy metric per cell line incl repls.
    all_combos = session.query(Combination).filter(Combination.lib1_id == drug1.id, Combination.lib2_id == drug2.id).all()

    all_matrices = session.query(MatrixResult).filter(MatrixResult.drugset_id == all_combos[0].drugset_id, MatrixResult.cmatrix == all_combos[0].cmatrix).all()

    all_cell_models = pd.DataFrame([dict(barcode=res.barcode,
                                         model_id=res.model.id,
                                         model_name=res.model.name,
                                         tissue=res.model.tissue,
                                         cancer_type=res.model.cancer_type)
                                    for res in all_matrices])

    all_dr_curves = pd.DataFrame([curve.to_dict() for res in all_matrices for curve in res.single_agent_curves])

    all_matrices = pd.DataFrame([x.to_dict() for x in all_matrices])

    all_matrices['lib1_tag'] = all_combos[0].lib1_tag
    all_matrices['lib2_tag'] = all_combos[0].lib2_tag
    all_matrices['lib1_name'] = drug1.drug_name
    all_matrices['lib2_name'] = drug2.drug_name

    all_matrices = pd.merge(all_matrices,
                   all_dr_curves.rename(columns={'dosed_tag': 'lib1_tag',
                                                 'ic50': 'lib1_ic50',
                                                 'auc': 'lib1_auc',
                                                 'rmse': 'lib1_rmse'
                                                 }, index=str)\
                       [['barcode', 'lib1_tag', 'lib1_ic50', 'lib1_auc', 'lib1_rmse']],
                   on=['barcode', 'lib1_tag'])

    all_matrices = pd.merge(all_matrices,
                   all_dr_curves.rename(columns={'dosed_tag': 'lib2_tag',
                                                 'ic50': 'lib2_ic50',
                                                 'auc': 'lib2_auc',
                                                 'rmse': 'lib2_rmse'
                                                 }, index=str)\
                       [['barcode', 'lib2_tag', 'lib2_ic50', 'lib2_auc', 'lib2_rmse']],
                   on=['barcode', 'lib2_tag'])

    all_matrices = pd.merge(all_matrices,
                            all_cell_models,
                            on=['barcode'])


    if len(all_combos) == 1:
        return html.Div([
            crumbs([("Home", "/")])
            intro(drug1, drug2, all_combos[0]),
            mm_plot(all_matrices)
            #  matrix_link(my_combination), link to cell line replicates
            # tissue specific box plot
        ])
    else:
        return html.Div("More than one screen or drugset for this combo")




