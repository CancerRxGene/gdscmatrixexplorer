import dash_html_components as html

def layout(combination=None):
    #     Select combination - dropdown?
    #     Infobox for select combination - names, targets etc...
    #     Michael Menden plot for all cell lines link to selected cell line
    #     Synergy metric dropdown for MM plot
    #     Link from plot to replicates for cell line and then link to matrix page

    # my_matrix = session.query(MatrixResult) \
    #     .filter_by(barcode=barcode, cmatrix=cmatrix).one()

    return html.Div([
        combination
        # intro(my_combination),
        # comparison_plot(my_combination),
        # matrix_link(my_combination), link to cell line replicates
    ])


