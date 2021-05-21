import dash_bootstrap_components as dbc
import dash_html_components as html

footer = dbc.Container(fluid=True, className='mt-5 pt-3 footer-wrapper', children=
            dbc.Container([
                dbc.Row(className='w-100', children=[
                    dbc.Col(width=3, children=[
                        html.Div([
                            html.H4("GDSC² Combo Explorer"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Interface version: 1.0.7")),
                                html.Li(html.Span("Data version: 2019.09.2")),
                                html.Li(html.A("Code on GitHub", href='https://github.com/CancerRxGene/gdscmatrixexplorer'), className='mt-3')

                            ])
                        ])

                    ]),
                    dbc.Col(width={'size': 3, 'offset': 3}, children=[
                        html.Div([
                            html.H4("Contact"),
                            html.Ul(className='list-unstyled', children=[

                                html.Li(html.Span("depmap@sanger.ac.uk"), className='mb-2'),
                                html.Li(html.Span("Wellcome Sanger Institute")),
                                html.Li(html.Span("Wellcome Genome Campus")),
                                html.Li(html.Span("Hinxton, Cambridgeshire")),
                                html.Li(html.Span("CB10 1SA, UK"))
                            ])
                        ])

                    ]),
                    # dbc.Col(width=3, children=[
                    #     html.Div([
                    #         html.H4("Contact AZ"),
                    #         html.Ul(className='list-unstyled', children=[
                    #             html.Li(html.Span("Krishna Bulusu")),
                    #             html.Li(html.Span("krishna.bulusu@astrazeneca.com"))
                    #         ])
                    #     ])
                    #
                    # ]),
                    # dbc.Col(width=3, children=[
                    #     html.Div([
                    #         html.H4("Users have a non-exclusive, non-transferable right to use data files for internal proprietary research and educational purposes, including target, biomarker and drug discovery. Excluded from this licence are use of the data (in whole or any significant part) for resale either alone or in combination with additional data/product offerings, or for provision of commercial services."),
                    #         html.H4(
                    #             "Please note: The data files are experimental and academic in nature and are not licensed or certified by any regulatory body. Genome Research Limited provides access to data files on an “as is” basis and excludes all warranties of any kind (express or implied)."),
                    #
                    #     ])
                    #
                    # ]),
                ])

            ])
        )
