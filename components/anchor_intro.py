import dash_bootstrap_components as dbc
import dash_html_components as html

from components.navigation.dropdowns import model_links_from_combo


def layout(combination):
    return html.Div(
        children=[
            dbc.Row(className="mt-5 mb-3", children=
                dbc.Col(width=12, children=[
                    html.H1([
                        html.Strong(f"{combination.lib1.name}"), " + ",
                        html.Strong(f"{combination.lib2.name}")
                    ]),
                    html.P("Combination Report", className='lead')
            ])
                    )]
    )