from textwrap import dedent

import dash_html_components as html
import dash_table_experiments as dt
import dash_core_components as dcc
import requests
import numpy as np

from db import session
from app import app
from models import MatrixResult, Drug, DrugMatrix, Model
from plots import dose_response_plot

irinotecan = session.query(Drug).filter_by(drug_name='Irinotecan').one()
ly260 = session.query(Drug).filter(Drug.drug_name.startswith("LY260")).one()
drug_matrix = session.query(DrugMatrix).filter(DrugMatrix.lib2 == irinotecan, DrugMatrix.lib1 == ly260).one()
SW620 = session.query(Model).filter(Model.name.ilike("SW620")).one()

my_matrix = session.query(MatrixResult).filter(MatrixResult.drug_matrix == drug_matrix, MatrixResult.model == SW620).first()

curve1 = my_matrix.single_agent_curves[0]
drug1 = my_matrix.drugs[curve1.dosed_tag]

curve2 = my_matrix.single_agent_curves[1]
drug2 = my_matrix.drugs[curve2.dosed_tag]

model_information = requests.get(f"http://api.cmp.staging.team215.sanger.ac.uk/models/{SW620.id}?include=sample.tissue,sample.cancer_type,sample.patient").json()
model_drivers = requests.get(f"http://api.cmp.staging.team215.sanger.ac.uk/models/{SW620.id}/datasets/cancer_drivers?page[size]=0&fields[mutation]=gene&include=gene&fields[gene]=symbol").json()
driver_genes = []
for g in model_drivers['included']:
    driver_genes.append(g['attributes']['symbol'])

layout = html.Div([
    html.Div(className="row my-5 d-flex flex-row", children=[
        html.Div(className="col-12", children=[
            html.H2(f"{drug1.drug_name} + {drug2.drug_name} in {SW620.name}")
        ])
    ]),
    html.Div(className="row my-5 d-flex flex-row", children=[
        html.Div(className="col-4 d-flex flex-column", children=[
            html.Div(
                id=f"drug-info-{drug1.id}",
                className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                children=[
                    dcc.Markdown(dedent(f'''
                      ### Single Agent Response of **{drug1.drug_name}**
                      ---
                      **Target:** {drug1.target}  
                      **Drug ID:** {drug1.id}  **Owner:** {drug1.owner}
                        
                      #### Sensitivity  
                      **IC50:** {round(np.exp(curve1.ic50), 3)} uM  
                      **AUC:** {round(curve1.auc, 3)}
                    ''')),
                    dose_response_plot(drug1, curve1)
                ]
            ),
        ]),
        html.Div(className="col-4 d-flex flex-column", children=[
            html.Div(
                id=f"drug-info-{drug1.id}",
                className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                children=[dcc.Markdown(dedent(f'''
                    ### Single Agent Response of **{drug2.drug_name}**
                    ---
                    **Target:** {drug2.target}  
                    **Drug ID:** {drug2.id}  **Owner:** {drug2.owner}
                      
                    #### Sensitivity  
                    **IC50:** {round(np.exp(curve2.ic50), 3)} uM  
                    **AUC:** {round(curve2.auc, 3)}
                      ''')),
                    dose_response_plot(drug2, curve2)
                ]
            ),
        ]),
        html.Div(className="col-4 d-flex flex-column", children=[
            html.Div(
                id=f"cell-info-{SW620.id}",
                className="bg-white pt-4 px-4 pb-1 border border-warning h-100",
                children=[dcc.Markdown(dedent(f'''
                    ### **{SW620.name}** properties
                    ---
                    **Tissue:** {SW620.tissue}  
                    **Cancer Type:** {SW620.cancer_type}  
                    **Sample Site:** {model_information['included'][0]['attributes']['sample_site']}  
                    **Sample Tissue Status:** {model_information['included'][0]['attributes']['tissue_status']}  
                      
                    #### Genetic information  
                    **Mutated Driver Genes:** {'  '.join(dg for dg in driver_genes)}  
                    **MSI Status:** {model_information['data']['attributes']['msi_status']}  
                    **Ploidy:** {round(model_information['data']['attributes']['ploidy'], 3)}  
                    **Mutational Burden:** {model_information['data']['attributes']['mutations_per_mb']} mutations per Mb  
                      
                    [View {SW620.name} on Cell Model Passports](https://cellmodelpassports.sanger.ac.uk/passports/{SW620.id})
                      '''))
                ]
            ),
        ])
    ]),
    html.Div(
        dt.DataTable(
            rows=[x.to_dict() for x in my_matrix.well_results],
            columns=list(my_matrix.well_results[0].to_dict().keys()),
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='wells_table'
        ),
        style={'width': '100%'}
    )
],
    style={'width': '100%'}
)

if __name__ == '__main__':
    app.run_server(debug=True)
