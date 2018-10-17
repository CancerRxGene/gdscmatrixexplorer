from textwrap import dedent

import dash_html_components as html
import dash_core_components as dcc
import requests
import numpy as np

from app import app
from plots import dose_response_plot

def layout(matrix):
    curve1 = matrix.single_agent_curves[0]
    drug1 = matrix.drugs[curve1.dosed_tag]
    curve2 = matrix.single_agent_curves[1]
    drug2 = matrix.drugs[curve2.dosed_tag]
    model = matrix.model

    model_information = requests.get(
        f"http://api.cmp.staging.team215.sanger.ac.uk/models/{model.id}?include=sample.tissue,sample.cancer_type,sample.patient").json()
    model_drivers = requests.get(
        f"http://api.cmp.staging.team215.sanger.ac.uk/models/{model.id}/datasets/cancer_drivers?page[size]=0&fields[mutation]=gene&include=gene&fields[gene]=symbol").json()
    driver_genes = []
    for g in model_drivers['included']:
        driver_genes.append(g['attributes']['symbol'])

    return html.Div([
        html.Div(className="row my-5 d-flex flex-row", children=[
            html.Div(className="col-12", children=[
                dcc.Markdown(f"# Combination Report for **{drug1.drug_name}** + **{drug2.drug_name}** in cell model **{model.name}**")
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
                          
                        #### Sensitivity of {model.name}  
                        **IC50:** {round(np.exp(curve2.ic50), 3)} uM  
                        **AUC:** {round(curve2.auc, 3)}
                          ''')),
                        dose_response_plot(drug2, curve2)
                    ]
                ),
            ]),
            html.Div(className="col-4 d-flex flex-column", children=[
                html.Div(
                    id=f"cell-info-{model.id}",
                    className="bg-white pt-4 px-4 pb-1 border border-warning h-100",
                    children=[dcc.Markdown(dedent(f'''
                        ### **{model.name}** properties
                        ---
                        **Tissue:** {model.tissue}  
                        **Cancer Type:** {model.cancer_type}  
                        **Sample Site:** {model_information['included'][0]['attributes']['sample_site']}  
                        **Sample Tissue Status:** {model_information['included'][0]['attributes']['tissue_status']}  
                          
                        #### Genetic information  
                        **Mutated Driver Genes:** {'  '.join(dg for dg in driver_genes)}  
                        **MSI Status:** {model_information['data']['attributes']['msi_status']}  
                        **Ploidy:** {round(model_information['data']['attributes']['ploidy'], 3)}  
                        **Mutational Burden:** {model_information['data']['attributes']['mutations_per_mb']} mutations per Mb  
                          
                        [View {model.name} on Cell Model Passports](https://cellmodelpassports.sanger.ac.uk/passports/{model.id})
                          '''))
                    ]
                ),
            ])
        ])]
    )

if __name__ == '__main__':
    app.run_server(debug=True)
