import dash_html_components as html
import dash_table_experiments as dt

def layout(matrix):

    return html.Div(className='row', children=[
        html.Div(className='col-11', children=[
            dt.DataTable(
                rows=[x.to_dict() for x in matrix.well_results],
                columns=list(matrix.well_results[0].to_dict().keys()),
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[],
                id='wells_table'
            )])
        ])