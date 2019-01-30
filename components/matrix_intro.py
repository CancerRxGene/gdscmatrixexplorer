from textwrap import dedent

import dash
import dash_html_components as html
import dash_core_components as dcc
import requests

from app import app
from components.matrix_navigation import replicate_links_from_matrix
from components.navigation.dropdowns import model_links_from_matrix, \
    combo_links_from_matrix
from components.single_agent.info import infoblock


def layout(matrix):
    curve1 = matrix.single_agent_curves[0]
    drug1 = matrix.drugs[matrix.lib1_id]
    curve2 = matrix.single_agent_curves[1]
    drug2 = matrix.drugs[matrix.lib2_id]
    model = matrix.model

    matrix_hsa = [w.HSA_excess for w in matrix.well_results]
    max_hsa = max(matrix_hsa)

    try:
        model_information = requests.get(
            f"https://api.cellmodelpassports.sanger.ac.uk/models/{model.id}?include=sample.tissue,sample.cancer_type,sample.patient").json()
    except requests.exceptions.ConnectionError:
        model_information, model_drivers, driver_genes = None, None, None

    if model_information:
        try:
            model_drivers = requests.get(
                f"https://api.cellmodelpassports.sanger.ac.uk/models/{model.id}/datasets/cancer_drivers?page[size]=0&fields[mutation]=gene&include=gene&fields[gene]=symbol").json()
            driver_genes = []
            for g in model_drivers['included']:
                driver_genes.append(g['attributes']['symbol'])
        except KeyError:
            model_drivers, driver_genes = None, None

    return html.Div([

        html.Div(className="row mt-3 mb-2 pl-3 d-flex flex-row", children=[
            html.Div(className="col-12", children=[
                dcc.Markdown(f"# **{drug1.drug_name}** + **{drug2.drug_name}** in cell model **{model.name}**"),
                html.P("Combination Matrix Report", className='lead')
            ])
        ]),
        html.Div(className="row mt-2 mb-5", children=[
            html.Div(className="col-9 d-flex flex-column", children=[
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
                                        ], className="pl-0", style={"width": "50%"}),
                                        html.Td([
                                            html.Strong("Mutated Cancer Genes "), '  '.join(dg for dg in sorted(driver_genes)) if driver_genes else "No mutated cancer genes found", html.Br(),
                                            html.Strong("MSI Status "), model_information['data']['attributes']['msi_status'] , html.Br(),
                                            html.Strong("Ploidy "), round(model_information['data']['attributes']['ploidy'], 3) if model_information['data']['attributes']['ploidy'] else "Unknown", html.Br(),
                                            html.Strong("Mutational Burden "),
                                            f"{round(model_information['data']['attributes']['mutations_per_mb'], 2)} mutations per Mb" if model_information['data']['attributes']['mutations_per_mb'] else "Unknown", html.Br(),html.Br(),
                                            html.A(children=f"View {model.name} on Cell Model Passports", href=f"https://cellmodelpassports.sanger.ac.uk/passports/{model.id}")
                                        ])

                                    ]),
                                    className="table"
                                ) if model_information else html.Table(
                                    html.Tr([
                                        html.Td([
                                            html.Strong("Tissue "), model.tissue, html.Br(),
                                            html.Strong("Cancer Type "), model.cancer_type, html.Br(), html.Br(),
                                            html.Em("Could not connect to Cell Model Passports for more information")
                                        ], className="pl-0", style={"width": "30%"})
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
                                infoblock(drug1),
                                curve1.plot(style={'maxHeight': '250px'})
                            ]
                        ),
                    ]),
                    html.Div(className="col-6 d-flex flex-column", children=[
                        html.Div(
                            id=f"drug-info-{drug1.id}",
                            className="bg-white pt-4 px-4 pb-1 border border-info h-100",
                            children=[
                                infoblock(drug2),
                                curve2.plot(style={'maxHeight': '250px'})
                            ]
                        ),
                    ])
                ]),


            ]),

            html.Div(className='col-3', children=[
                html.Div(className='bg bg-light border pt-3 px-4 pb-3 mb-3', children=[
                    html.H3("Summary"),
                    html.Strong("Max. observed inhibition %"),
                    html.Hr(),
                    html.Table([
                        html.Tr([
                            html.Td(["Combination"]),
                            html.Td([html.Strong(round(matrix.combo_max_effect * 100, 1))])
                            ]),
                        html.Tr([
                            html.Td([drug1.drug_name]),
                            html.Td([html.Strong(round(matrix.lib1_max_effect * 100, 1))])
                        ]),
                        html.Tr([
                            html.Td([drug2.drug_name]),
                            html.Td([html.Strong(round(matrix.lib2_max_effect * 100, 1))])
                        ]),
                        html.Tr([
                            html.Td(["Excess over HSA"]),
                            html.Td([html.Strong(round(max_hsa * 100, 1))])
                        ])
                    ]),
                ]),
                html.Div(className='bg bg-light border pt-4 px-4 pb-1 d-print-none',
                         children=[
                             html.H3("Quick Navigation"),
                             html.Hr(),
                             replicate_links_from_matrix(matrix),
                             model_links_from_matrix(matrix),
                             combo_links_from_matrix(matrix)
                         ])
            ])
        ]),
        html.Div(id='hidden-div', className='d-none')
    ]
    )
