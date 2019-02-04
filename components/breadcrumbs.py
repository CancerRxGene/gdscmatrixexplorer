import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


def breadcrumb_generator(paths):
    crumbs = [html.Span("You are here: ")]
    for label, url in paths[:-1]:
        crumbs.append(dcc.Link(label, href=url))
        crumbs.append(html.Span(" > "))

    crumbs.append(html.Strong(paths[-1][0]))

    return dbc.Row(
        dbc.Col(html.P(crumbs), width=12, className='pl-4 pt-2'),
        className='pl-2 d-print-none'
    )
