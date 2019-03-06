import dash_html_components as html


def infoblock(drug, rmse=0):

    return html.Div([
        html.H3([
            html.Strong(drug.name),
            html.Span(f" ({drug.target})")
        ]),
        html.Hr(),
        html.P(["Monotherapy response ", html.Strong("POOR FIT: RMSE > 0.3")], style={'color': 'red'})
            if rmse > 0.3 else html.P("Monotherapy response")
    ])