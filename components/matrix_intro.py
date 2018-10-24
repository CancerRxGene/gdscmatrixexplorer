from textwrap import dedent

import dash_html_components as html
import dash_core_components as dcc
import requests

from app import app
from components.single_agent.info import infoblock, infoblock_curve


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
            html.Div(className="col-8 d-flex flex-column", children=[
                html.Div(className="row mb-3", children=[
                    html.Div(className='col-12', children=[
                        html.Div(
                            id=f"cell-info-{model.id}",
                            className="bg-white pt-4 px-4 pb-1 border border-warning",
                            children=[html.Div([
                                html.H3(["Cell Line ", html.Strong(model.name)]),
                                html.Table(
                                    html.Tr([
                                        html.Td([
                                            html.Strong("Tissue "), model.tissue, html.Br(),
                                            html.Strong("Cancer Type "), model.cancer_type, html.Br(),
                                            html.Strong("Sample Site "), model_information['included'][0]['attributes']['sample_site'], html.Br(),
                                            html.Strong("Sample Tissue Status "), model_information['included'][0]['attributes']['tissue_status'], html.Br(),
                                        ], className="pl-0", style={"width": "30%"}),
                                        html.Td([
                                            html.Strong("Mutated Driver Genes "), '  '.join(dg for dg in sorted(driver_genes)), html.Br(),
                                            html.Strong("MSI Status "), model_information['data']['attributes']['msi_status'], html.Br(),
                                            html.Strong("Ploidy "), round(model_information['data']['attributes']['ploidy'], 3), html.Br(),
                                            html.Strong("Mutational Burden "), round(model_information['data']['attributes']['mutations_per_mb'],2), " mutations per Mb", html.Br(),html.Br(),
                                            html.A(children=f"View {model.name} on Cell Model Passports", href=f"https://cellmodelpassports.sanger.ac.uk/passports/{model.id}")
                                        ])

                                    ]),
                                    className="table"
                                )
                            ])]
                        )
                    ])
                ]),

                html.Div(className="row", children=[
                    html.Div(className="col-6 d-flex flex-column", children=[
                        html.Div(
                            id=f"drug-info-{drug1.id}",
                            className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                            children=[
                                infoblock_curve(drug1, curve1),
                                curve1.plot(mark_auc=False, label_auc=False, mark_ic50=False,
                                            label_ic50=False, mark_emax=False,
                                            label_emax=False, label_rmse=False)
                            ]
                        ),
                    ]),
                    html.Div(className="col-6 d-flex flex-column", children=[
                        html.Div(
                            id=f"drug-info-{drug1.id}",
                            className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                            children=[
                                infoblock(drug2),
                                curve2.plot()
                            ]
                        ),
                    ])
                ]),


            ]),
            html.Div(className='col-4 bg bg-light border', children=[
                dcc.Markdown(dedent("""
                    ### Quick Navigation  
                      
                    ##### Links to Replicates (if any)  
                    [Replicate 1](rep1)  
                    [Replicate 2](rep1)  
                    [Replicate 3](rep1)  
                    [Replicate 4](rep1)  
                      
                      
                    ##### Links to all combinations for the same model
                    [Combo 1](rep1)  
                    [Combo 2](rep1)  
                    [Combo 3](rep1)  
                    [Combo 4](rep1) 
                      
                      
                    ##### Links to all models for the same combination
                    [Model 1](rep1)  
                    [Model 2](rep1)  
                    [Model 3](rep1)  
                    [Model 4](rep1) 
                    ... Probably a dropdown
                """))
            ])
        ])]
    )

if __name__ == '__main__':
    app.run_server(debug=True)
