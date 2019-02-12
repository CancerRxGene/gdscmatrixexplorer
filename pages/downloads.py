import dash_html_components as html


def layout(*args, **kwargs):
    return html.Div([
        html.H1("Downloads", className='display-4 text-center mt-5 mb-3'),

        html.H2("Raw Data", className='my-3'),
        html.H4(html.A("Matrix & Well Data GDSC_007",
                       href='/downloads/GDSC_007_results_20190131.zip'),
                className='d-inline'), html.Span(" (ZIP, 135.9MB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),
        html.H4(html.A("Matrix & Well Data Sandpiper-01",
                       href='downloads/sandpiper1_results_20190129.zip'),
                className='d-inline'), html.Span(" (ZIP, 24.8MB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),

        html.H2("Documentation", className='my-3'),
        html.H4(html.A("MatrixExplorer Documentation",
               href='downloads/matrixexplorer_documentation_20190211.pdf'),
                className='d-inline'), html.Span(" (PDF, 768kB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),
        html.H4(html.A("Glossary for datasets", href='/downloads/glossary.pdf'),
                className='d-inline'), html.Span(" (PDF, 573kB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),
        html.H4(html.A("Drug Screening Information", href='/downloads/screen_information_20190211.pdf'),
                className='d-inline'), html.Span(" (PDF, 614kB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),

        html.H2("SOPs", className='my-3'),
        html.H4(html.A("SOP 1: Exploring a combination",
                       href='/downloads/matrixexplorer_sop_combination_20190211.pdf'),
                className='d-inline'), html.Span(" (PDF, 4.5MB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),
        html.H4(html.A("SOP 2: Exploring a tissue / disease",
                       href='/downloads/matrixexplorer_sop_disease_tissue_20190211.pdf'),
                className='d-inline'), html.Span(" (PDF, 3.5MB)"), html.Br(),
        html.Span("11 February 2019", className='small'), html.Br(), html.Br(),
        html.H2("Other", className='my-3'),
    ])

