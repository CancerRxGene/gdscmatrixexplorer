import dash_core_components as dcc
import dash_html_components as html


def replicate_links_from_matrix(matrix):

    link_text = lambda x: f"Barcode {x.barcode} ({x.project.name}) {'*' if x.hsa_matrix > 0 else ''}"

    children = []
    for rep in sorted(matrix.all_replicates, key=lambda x: x.barcode):
        if rep != matrix:
            children.append(dcc.Link(link_text(rep), href=f"/matrix/{rep.barcode}/{rep.cmatrix}"))
            children.append((html.Br()))
        else:
            children.append(html.Span(link_text(rep)))
            children.append((html.Br()))

    return html.Div( className="mb-4", children=
        [html.H5('Replicates')] +
        children
    )




