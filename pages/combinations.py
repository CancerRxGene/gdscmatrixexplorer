import dash_html_components as html

from components.combination_intro import layout as intro
from components.combination_max_effect import layout as max_effect_analysis
from components.combination_mm_plot import layout as mm_plot
from components.anchor_overview import layout as anchor_overview_plot
from components.anchor_intro import layout as anchor_intro
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_combination_from_url, get_project_from_url


def layout(url):

    combination = get_combination_from_url(url)
    project = get_project_from_url(url)

    if(project.combination_type == 'matrix'):
        return html.Div([
            crumbs([("Home", "/"), (combination.project.name, f"/project/{combination.project.slug}"),
                    (f"{combination.lib1.name} + {combination.lib2.name}",)]),
            intro(combination),
            max_effect_analysis(combination),
            mm_plot()
        ])

    else:
        return html.Div([
            crumbs([("Home", "/"), (combination.project.name, f"/project/{combination.project.slug}"),
                    (f"{combination.lib1.name} + {combination.lib2.name}",)]),
            anchor_intro(combination),
            anchor_overview_plot(combination)
        ])


