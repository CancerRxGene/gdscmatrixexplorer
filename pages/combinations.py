import dash_html_components as html

from components.combination_intro import layout as intro
from components.combination_max_effect import layout as max_effect_analysis
from components.combination_mm_plot import layout as mm_plot
from components.breadcrumbs import breadcrumb_generator as crumbs
from utils import get_combination_from_url


def layout(url):

    combination = get_combination_from_url(url)

    return html.Div([
        crumbs([("Home", "/"), (combination.project.name, f"/project/{combination.project.slug}"),
                (f"{combination.lib1.drug_name} + {combination.lib2.drug_name}",)]),
        intro(combination),
        max_effect_analysis(combination),
        mm_plot()
    ])




