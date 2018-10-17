html.Div(
        dt.DataTable(
            rows=[x.to_dict() for x in my_matrix.well_results],
            columns=list(my_matrix.well_results[0].to_dict().keys()),
            row_selectable=True,
            filterable=True,
            sortable=True,
            selected_row_indices=[],
            id='wells_table'
        ),
        style={'width': '100%'}
    )