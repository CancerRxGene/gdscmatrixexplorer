import dash_bootstrap_components as dbc
import dash_html_components as html

from components.navigation.dropdowns import model_links_from_combo


def layout(project,combination):
    return html.Div(
        children=[
            dbc.Row(className="mt-5 mb-3", children=
                dbc.Col(width=12, children=[
                    html.H3(project.name),
                    html.H1([
                        html.Strong(f"{combination.lib1.name}"), " + ",
                        html.Strong(f"{combination.lib2.name}")
                    ]),
                   # html.P("Combination Report", className='lead')
                ])
            ),
            dbc.Row(className='d-flex', children=[
                dbc.Col(width=6, children=[
                    html.Div(className="bg-white pt-3 px-4 pb-2 mb-3 border border-primary shadow-sm",
                             children=[
                                html.H3("Drug Information"),
                                html.Hr(),
                                dbc.Row([
                                    dbc.Col(width=6, children=[
                                        html.Tr([
                                            html.Td(html.Strong("Name")),
                                            html.Td(combination.lib1.name)
                                        ]),
                                        html.Tr([
                                            html.Td(html.Strong("Target")),
                                            html.Td(combination.lib1.target)
                                        ]),

                                        html.Tr([
                                            html.Td(html.Strong("Max. conc.")),
                                            # html.Td(f"{lib1_maxc} µM")
                                        ])
                                        ]
                                    ),
                                    dbc.Col(width=6, children=[
                                        html.Tr([
                                            html.Td(html.Strong("Name")),
                                            html.Td(combination.lib2.name)
                                        ]),
                                        html.Tr([
                                            html.Td(html.Strong("Target")),
                                            html.Td(combination.lib2.target)
                                        ]),

                                        html.Tr([
                                            html.Td(html.Strong("Max. conc.")),
                                            # html.Td(f"{lib1_maxc} µM")
                                        ])
                                         ]
                                    )
                                ])
                     ])
                ]),
                dbc.Col(
                    width=6,
                    className='d-print-none align-self-stretch pb-3',
                    children=
                    html.Div(
                        className="bg-white pt-3 px-4 pb-2 mb-3 border shadow-sm h-100",
                        children=[
                            html.H3("View combination in cell line"),
                            html.Hr(),
                            dbc.Row(
                                className="pb-4",
                                children=dbc.Col(
                                    width=12,
                                    children=[]
                                ),
                            )
                        ],
                    )
                )
            ])
        ]
    )