import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash_html_components import *
from textwrap import dedent

sub = lambda letter, number: [Em(f"{letter}"), Sub(f"{number}")]
E1 = sub('E', 1)
E2 = sub('E', 2)
E12 = sub('E', "1,2")
X1 = sub("X", 1)
X2 = sub("X", 2)
x1 = sub("x", 1)
x2 = sub("x", 2)


def layout(*args, **kwargs):
    return dbc.Col(width={'size': 8, 'offset': 2}, className='text-justify documentation', children=[
        H1("Documentation", className='display-4 text-center my-5'),

        H2("Screen Design"),
        P(["Information on screen design, cell lines, compounds and quality control can be downloaded here: ", Br(),
                A("Download Screen Information", href="/downloads/screen_information_20190211.pdf", target="_blank", rel="noopener noreferrer"),
                " (PDF, 614kB)."]),
        H2("Single agent & combination response"),
        P("Single agent responses are normalised to controls and fitted. Single agent maximum effect (MaxE) is derived from the fit of the single agent response at the highest screened concentration (fitted for individual replicates if available)."),
        P("Measured inhibition of the combination wells is also normalised to controls. The combination maximum effect (combo_MaxE) corresponds to the second highest measured data point. There is currently no combination surface fit available in MatrixExplorer v1."),

        H2("Synergy reference models"),
        H4("Highest Single Agent (HSA)"),
        P(["According to the HSA model, a combination of Drug 1 and Drug 2 is classified as synergistic if the effect of the combination (", *E12, ") is larger than the effect of either Drug 1 (", *E1, " or Drug 2 (", *E2, ") alone (whichever is larger)."]),
        P([Em("Synergy: "), Em("E", className="pl-5"), Sub("1,2"), " > max(", *E1, ",", *E2, ")"]),
        P("Whilst the HSA model can simply and effectively identify combinations with a better effect than either of the single agents, it fails to distinguish between responses that are less than or greater than the additive response expected by combining the two drugs. Hence, the HSA model does not distinguish between additive and synergistic effects."),
        P(["HSA excess is calculated by subtracting the highest effect of either single agent from the combination response (", *E12, "), whereby a positive HSA excess indicates synergy."]),
        P([Em("HSA excess: "), Em("E", className="pl-5"), Sub("1,2"), " - max(", *E1, ",", *E2, ")"]),

        H4("Bliss independence"),
        P("Bliss independence is one of the most widely used synergy metrics. The null model assumes that the drug effects of two drugs are mechanistically, and therefore also probabilistically, independent. Additionally, Bliss scores assume the single agents have exponential dose effect curves."),
        P(["To calculate a Bliss excess, the single agent activities of Drug 1 (", *E1, ") and Drug 2 (", *E2, "), as well as the observed effect of the combination (", *E12, "), must be expressed as a probability between 0 and 1 (0 ≤ ", *E1, " ≤ 1, 0 ≤ ", *E2, " ≤ 1, and 0 ≤ ", *E12, " ≤ 1, respectively)."]),
        P([Em("Additive Bliss effect: "), Em("E", className="pl-5"), Sub("1"), " + ", *E2, "(1-", *E1, ") =", *E1, " + ", *E2, " - ", *E1, *E2]),
        P("Bliss excess is currently calculated as the difference between the measured inhibition of the combination and the Bliss additivity of the monotherapies at the same concentrations."),
        P([Em("Bliss excess: "), Em("E", className="pl-5"), Sub("1,2"), " - (", *E1, " + ", *E2, " - ", *E1, *E2, ")"]),

        H4("Loewe additivity"),
        P(["Loewe additivity focusses on the concentrations necessary to produce a given effect, rather than the effects at given concentrations. To fulfil Loewe additivity, the combination effect ", *E12, " at doses ", *X1, " and ", *X2, " has to produce the same inhibitory effect than the single agent doses at ", *x1, " and ", *x2, "."]),
        P([Em("Loewe index: "), Span("(", className='pl-5'), *x1, " / ", *X1, ") + (", *x2, " / ", *X2, ")"]),
        P("with an index = 1 indicating Loewe additivity, an index > 1 an effect greater than Loewe additivity and an index < 1 an effect smaller than Loewe additivity."),
        P(["Loewe additivity assumes a constant potency ratio between the two drugs and that there is dose equivalence. This leads to the same combination principle that an equivalent dose of drug 1 (", *x1,") can be substituted for drug 2 (", *x2, ") to produce the same combined effect of ", *E12, "."]),
        P("A fitted model of the combination interaction surface is currently not available. Hence, no reliable Loewe index can be calculated."),

        H4("References"),
        P("Foucquier and Guedj, \"Analysis of drug combinations: current methodological landscape\", Pharmacology Research and Perspectives, 2015."),
        P("Lehar et al., \"Chemical combination effects predict connectivity in biological systems\", Molecular Systems Biology, 2007."),
        P("Bliss, \"The toxicity of poisons applied jointly\", Annals of Applied Biology, 1939."),

        H2("Full matrix vs. 3x3 window"),
        P("Synergy metrics can be calculated across the entire combination dose matrix (i.e. across all the 49 wells), or across a smaller 3x3 sub-matrix (a \"window\"). The window is used to uncover dose ranges where highest synergy is seen and thereby describes localised synergy effects."),
        P("Reported are the windows with highest mean synergy across all 3x3 wells or across all synergistic wells within a 3x3 window. For this, mean synergy is calculated for all possible 3x3 windows in a matrix and the highest window is reported."),
        P([Em("3x3 window: "), Span("sum of 9 wells / 9 wells", className='pl-5')]),
        P([Em("3x3 window, synergy only: "), Span("sum of synergistic wells in window / # of synergistic wells in window", className='pl-5')]),
        Img(src="assets/matrix_layout.png"),

        P("To locate the window in a matrix two locators are available describing the upper right corner of the window, whereby dose1 describes the dose of drug 1 (horizontal) and dose2 describes the dose of drug 2 (vertical). Doses are reported on a scale from D1 to D7, with D1 being the highest screened concentration."),

        H2("Glossary of terminology"),
        P(["The full glossary can be downloaded here: ", A("Glossary of available metrics", href='/downloads/glossary.pdf'), Span(" (PDF, 573kB)")]),

        H4("Screen-related metrics"),
        Table(className='table table-sm', children=[
            Tr([
                Th("Metric name", className='w-25'),
                Th("Explanation")
            ]),
            Tr([
                Td("BARCODE"),
                Td("Barcode of the assay plate")
            ]),
            Tr([
                Td("DRUGSET_ID"),
                Td(["ID of the drug set used for the assay plate", Br(),
                    "(Drug set describes the individual plate layout & drug composition)"])
            ]),
            Tr([
                Td("cmatrix"),
                Td("Identifier for a combination matrix within a drug set")
            ]),
            Tr([
                Td("well_treatments"),
                Td("Combination of drug set library tags")
            ])
        ]),

        H4("Cell line-related metrics"),
        Table(className='table table-sm', children=[
            Tr([
                Th("Metric name", className='w-25'),
                Th("Explanation")
            ]),
            Tr([
                Td("CL"),
                Td("Cell line identifier used in the curve fit")
            ]),
            Tr([
                Td("CELL_LINE_NAME"),
                Td(["Name of the cell line"])
            ]),
            Tr([
                Td("COSMIC_ID"),
                Td("COSMIC database identifie")
            ]),
            Tr([
                Td("TISSUE"),
                Td("Sanger tissue classification")
            ]),
            Tr([
                Td("CANCER_TYPE"),
                Td("Sanger cancer type classification")
            ])
        ]),

        H4("Library drug-related metrics"),
        P("The two drugs used in the matrices are called \"lib1\" and \"lib2\", with lib1 being the first drug listed in the combination. All metrics below are available for both drugs."),
        Table(className='table table-sm', children=[
            Tr([Th("Metric name", className='w-25'), Th("Explanation")]),
            Tr([Td("lib1"), Td("Drug set library tag identifier")]),
            Tr([Td("lib1_ID"), Td("Sanger database identifier of drug")]),
            Tr([Td("lib1_name"), Td("Drug name")]),
            Tr([Td("lib1_conc"), Td("Highest screened concentration (in μM)")]),
            Tr([Td("lib1_RMSE"), Td(["RMSE: root mean square error", Br(), "Describes how far the data points are from the single agent curve fit"])]),
            Tr([Td("lib1_MaxE"), Td("Fitted inhibition value at the highest used concentration")]),
            Tr([Td("lib1_IC50_ln"), Td("Natural log of IC50")]),
            Tr([Td("lib1_IC50_uM"), Td("IC50 in μM")]),
            Tr([Td("lib1_target"), Td("Protein target(s)")]),
            Tr([Td("lib1_pathway"), Td("Pathway of protein target(s)")]),
            Tr([Td("lib1_owner"), Td("Sanger database drug owner")]),
        ]),
        H4("Combination response-related metrics"),
        Table(className='table table-sm', children=[
            Tr([Th("Metric name", className='w-25'), Th("Explanation")]),
            Tr([Td("matrix_size"), Td("Number of wells treated with the combination e.g. 49 for a 7x7 matrix")]),
            Tr([Td("combo_MaxE"), Td("Maximum inhibitory effect of the combination within the matrixBased on the 2nd highest data point in the matrix")]),
            Tr([Td("Delta_MaxE_lib1"), Td("combo_MaxE - lib1_MaxE")]),
            Tr([Td("Delta_MaxE_lib2"), Td("combo_MaxE - lib2_MaxE")]),
            Tr([Td("Delta_combo_MaxE_day1"), Td("combo_MaxE - day1_inhibition_scale_")]),
        ]),

        H4("Synergy-related metrics"),
        P("All metrics below have been derived for two synergy reference models: Bliss excess and HSA excess. The used placeholder \"X\" thereby stands either for \"Bliss\" or for \"HSA\"."),
        Table(className='table table-sm', children=[
            Tr([Th("Metric name", className='w-25'), Th("Explanation")]),
            Tr([Td("X_synergistic_wells"), Td("Number of wells with a response in excess of that expected by the synergy reference model")]),
            Tr([Td("X_matrix"), Td("Mean excess effect over X across the matrixCalculated by _sum all wells_ / _number of wells_")]),
            Tr([Td("X_matrix_SO"), Td("Mean excess effect over X across the matrix (synergistic wells only)Calculated by _sum synergistic wells_ / _number of synergistic wells_")]),
            Tr([Td("X_window_size"), Td("Local sub-matrix size in one dimension e.g. \"3\" = 3x3 matrix")]),
            Tr([Td("X_window"), Td("Mean excess effect over X across the windowCalculated by _sum all wells_ / _number of wells_")]),
            Tr([Td("X_window_dose1"), Td("Locator of upper right corner of window (library 1)D1-D7 with D1 being the highest screened concentration")]),
            Tr([Td("X_window_dose2"), Td("Locator of upper right corner of window (library 2)D1-D7 with D1 being the highest screened concentration")]),
            Tr([Td("X_window_SO_size"), Td("Local synergy only sub-matrix size in one dimension e.g. \"3\" = 3x3 matrix")]),
            Tr([Td("X_window_SO"), Td(["Mean excess effect over X across the window (synergistic wells only)", Br(), "Calculated by ", Em("sum synergistic wells / number of synergistic wells")])]),
            Tr([Td("X_window_SO_dose1"), Td("Locator of upper right corner of synergy only window (library 1)D1-D7 with D1 being the highest screened concentration")]),
            Tr([Td("X_window_SO_dose2"), Td("Locator of upper right corner of synergy only window (library 2)D1-D7 with D1 being the highest screened concentration")]),

        ]),
        H4("Day1 & growth-related metrics", className='mt-4'),
        Table(className='table table-sm', children=[
            Tr([Th("Metric name", className='w-25'), Th("Explanation")]),
            Tr([Td("day1_intensity_mean"), Td("Mean observed luminescent intensity of Day1 plate")]),
            Tr([Td("day1_intensity_sd"), Td("Standard deviation of observed luminescent intensities across Day1 plate")]),
            Tr([Td("day1_viability_mean"), Td(["Mean viability of Day1 plate, scale: 0-1 with 1 = full viability", Br(), "Calculated with respect to Day4 controls"])]),
            Tr([Td("day1_viability_sd"), Td("Standard deviation of Day1 plate viabilities")]),
            Tr([Td("day1_inhibition_scale"), Td(["Mean viability of Day1 plate converted to inhibition scale, scale: 0-1 with 1 = full inhibition", Br(), Em("1 - day1_viability_mean")])]),
            Tr([Td("growth_rate"), Td([Em(["log", Sub("2"), "((NC) / day1_intensity_mean)"]), Br(), "Where NC is the mean intensity of negative controls for the Day4 plate"])]),
            Tr([Td("doubling_time"), Td(["Doubling time in hours", Br(), Em(["72* log", Sub("2"), "(2) / (log", Sub("2"), ", (NC) - log", Sub("2"), " (day1_intensity_mean))"])])]),

        ]),
    ])

