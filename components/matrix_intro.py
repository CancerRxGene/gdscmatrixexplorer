import json

import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import requests

from app import app
from components.matrix_navigation import replicate_links_from_matrix
from components.navigation.dropdowns import model_links_from_matrix, \
    combo_links_from_matrix
from components.single_agent.info import infoblock
from db import session
from models import Model


def layout(matrix):
    curve1, curve2 = matrix.single_agent_curves
    drug1 = matrix.combination.lib1
    drug2 = matrix.combination.lib2
    model = matrix.model

    max_hsa = max([w.HSA_excess for w in matrix.well_results])
    max_bliss = max([w.Bliss_excess for w in matrix.well_results])

    return html.Div([
        dbc.Row(className="mt-3 mb-2 pl-3", children=
            dbc.Col(width=12, children=[
                dcc.Markdown(f"# **{drug1.drug_name}** + **{drug2.drug_name}** in cell model **{model.name}**"),
                html.P(f"Combination Matrix Report for barcode {matrix.barcode}", className='lead')
            ])
        ),
        dbc.Row(className="mt-2 mb-5", children=[
            dbc.Col(width=9, children=[
                html.Div(
                    id=f"cell-info-{model.id}",
                    className="bg-white pt-4 px-4 pb-1 mb-3 border shadow-sm",
                    children=html.Div([
                        html.H3(["Cell Line ", html.Strong(model.name)]),
                        html.Table(
                            id='model-information',
                            className='table',
                            children=[
                                html.Tr([
                                    html.Td([
                                        html.Strong("Tissue "), model.tissue, html.Br(),
                                        html.Strong("Cancer Type "), model.cancer_type, html.Br(),
                                        html.Strong("Estimated doubling time "), f"{round(matrix.doubling_time, 1)} hours", html.Br(),
                                        html.Br(),
                                        html.Em("Loading more information from Cell Model Passports...")],
                                        className="pl-0")
                                ])
                            ]
                        )
                    ])
                ),

                dbc.Row([
                    dbc.Col(width=6, children=
                        html.Div(
                            id=f"drug-info-{drug1.id}",
                            className="bg-white pt-4 px-4 pb-1 border h-100 shadow-sm",
                            children=[
                                infoblock(drug1, rmse=curve1.rmse),
                                curve1.plot(height=250)
                            ]
                        ),
                    ),
                    dbc.Col(width=6, children=
                        html.Div(
                            id=f"drug-info-{drug2.id}",
                            className="bg-white pt-4 px-4 pb-1 border h-100 shadow-sm",
                            children=[
                                infoblock(drug2, rmse=curve2.rmse),
                                curve2.plot(height=250)
                            ]
                        )
                    )
                ]),
            ]),

            dbc.Col(width=3, children=[
                html.Div(className='bg bg-light border pt-3 px-4 pb-3 mb-3 shadow-sm', children=[
                    html.H3("Summary"),
                    html.Strong("Max. observed inhibition %"),
                    html.Hr(),
                    html.Table(className='table table-borderless table-sm', children=[
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
                        ]),
                        html.Tr([
                            html.Td(["Excess over Bliss"]),
                            html.Td([html.Strong(round(max_bliss * 100, 1))])
                        ])
                    ]),
                ]),
                html.Div(className='bg bg-white border pt-4 px-4 pb-1 d-print-none shadow-sm',
                         children=[
                             html.H3("Quick Navigation"),
                             html.Hr(),
                             replicate_links_from_matrix(matrix),
                             model_links_from_matrix(matrix),
                             combo_links_from_matrix(matrix)
                         ])
            ])
        ]),
        # html.Div(id='hidden-div', className='d-none'),
        html.Div(id='model-id', className='d-none', children=matrix.model_id),
        html.Div(id='passport-data', className='d-none'),
        html.Div(id='gr-data', className='d-none', children=json.dumps(dict(doubling_time=matrix.doubling_time, growth_rate=matrix.growth_rate, day1_viab=matrix.day1_viability_mean))),
    ]
    )


@app.callback(dash.dependencies.Output('passport-data', 'children'),
              [dash.dependencies.Input('model-id', 'children')],
              [dash.dependencies.State('passport-data', 'children')])
def compute_value(model_id, passport_data):
    """
    passport-data acts as a signaling div for the site to determine
    if any data from the CMP API has been loaded. If not (API down or model not
    present), only the tissue and cancer type will show.
    """
    if passport_data is not None:
        return passport_data

    if model_id is None:
        return

    model = session.query(Model).get(model_id)

    try:
        model_information = requests.get(
            f"https://api.cellmodelpassports.sanger.ac.uk/models/{model.id}?include=sample.tissue,sample.cancer_type,sample.patient", timeout=2).json()
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            json.decoder.JSONDecodeError):
        model_information, model_drivers, driver_genes = None, None, None

    if model_information:
        try:
            model_drivers = requests.get(
                f"https://api.cellmodelpassports.sanger.ac.uk/models/{model.id}/datasets/cancer_drivers?page[size]=0&fields[mutation]=gene&include=gene&fields[gene]=symbol", timeout=2).json()
            driver_genes = []
            for g in model_drivers['included']:
                driver_genes.append(g['attributes']['symbol'])
        except KeyError:
            model_drivers, driver_genes = None, None

    return json.dumps(dict(model_information=model_information,
                           driver_genes=driver_genes))


@app.callback(dash.dependencies.Output('model-information', 'children'),
              [dash.dependencies.Input('model-id', 'children'),
               dash.dependencies.Input('passport-data', 'children'),
               dash.dependencies.Input('gr-data', 'children')],
              [dash.dependencies.State('model-information', 'children')])
def model_information(model_id, passport_data, gr_data, current_model_information):
    if model_id is None:
        return current_model_information
    if passport_data is None:
        return current_model_information

    model = session.query(Model).get(model_id)
    cmp_data = json.loads(passport_data)
    gr_data = json.loads(gr_data)

    def model_attribute_section(model_attributes, text, attribute, from_sample=False):

        if model_attributes is None:
            return ['']
        text = text.strip() + " "

        model_attributes = model_attributes['included'][0]['attributes'] \
            if from_sample else model_attributes['data']['attributes']

        if attribute in model_attributes:
            return [html.Strong(text),
                    round(model_attributes[attribute], 3)
                        if isinstance(model_attributes[attribute], float)
                        else model_attributes[attribute],
                    html.Br()]
        else:
            return [f"{attribute} not found in {str(list(model_attributes.keys()))}"]

    if cmp_data['driver_genes'] is not None:
        driver_genes_block = [html.Strong("Mutated Cancer Genes ")] + \
            ['  '.join(dg for dg in sorted(cmp_data['driver_genes']))] + \
            [html.Br()]
    else:
        driver_genes_block = []


    return html.Tr([
            html.Td(
                [html.Strong("Tissue "), model.tissue, html.Br(),
                 html.Strong("Cancer Type "), model.cancer_type, html.Br()] +
                 model_attribute_section(cmp_data['model_information'], 'Sample Site', 'sample_site', from_sample=True) +
                 model_attribute_section(cmp_data['model_information'], 'Sample Tissue Status', 'tissue_status', from_sample=True) +
                [html.Strong("Estimated doubling time "), round(gr_data['doubling_time'], 1), 'hours (on this plate)', html.Br()],
                 className="pl-0", style={"width": "50%"}),
            html.Td(
                driver_genes_block +
                model_attribute_section(cmp_data['model_information'], 'MSI Status', 'msi_status') +
                model_attribute_section(cmp_data['model_information'], 'Ploidy','ploidy') +
                model_attribute_section(cmp_data['model_information'], 'Mutations per Mb', 'mutations_per_mb') +
                [html.Br(), html.Br(),
                 html.A(children=f"View {model.name} on Cell Model Passports",
                        href=f"https://cellmodelpassports.sanger.ac.uk/passports/{model.id}")
                 ]
            )

        ])