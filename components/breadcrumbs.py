import dash_core_components as dcc
import dash_html_components as html


def breadcrumb_generator(paths):
    crumbs = [html.Span("You are here: ")]
    for label, url in paths[:-1]:
        crumbs.append(dcc.Link(label, href=url))
        crumbs.append(html.Span(" > "))

    crumbs.append(html.Strong(paths[-1][0]))

    return html.Div(className='row pl-2 d-print-none', children=[
        html.Div(className='col-12 pl-4 pt-1', children=[
            html.P(crumbs)
        ])
    ])