import dash_bootstrap_components as dbc
import dash_html_components as html

footer = dbc.Container(fluid=True, className='mt-5 pt-3 footer-wrapper', children=
            dbc.Container([
                dbc.Row(className='w-100', children=[
                    dbc.Col(width=3, children=[
                        html.Div([
                            html.H4("GDSC² Matrix Explorer"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Interface version: 1.0.2")),
                                html.Li(html.Span("Data version: 2019.02.0")),
                                html.Li(html.A("Code on GitHub", href='https://github.com/CancerRxGene/gdscmatrixexplorer'), className='mt-3')

                            ])
                        ])

                    ]),
                    dbc.Col(width={'size': 3, 'offset': 3}, children=[
                        html.Div([
                            html.H4("Contact Sanger"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Elizabeth Coker")),
                                html.Li(html.Span("ec18@sanger.ac.uk"), className='mb-2'),
                                html.Li(html.Span("Patricia Jaaks")),
                                html.Li(html.Span("pj4@sanger.ac.uk"))
                            ])
                        ])

                    ]),
                    dbc.Col(width=3, children=[
                        html.Div([
                            html.H4("Contact AZ"),
                            html.Ul(className='list-unstyled', children=[
                                html.Li(html.Span("Krishna Bulusu")),
                                html.Li(html.Span("krishna.bulusu@astrazeneca.com"))
                            ])
                        ])

                    ]),
                ])

            ])
        )
