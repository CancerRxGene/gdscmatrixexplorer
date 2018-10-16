import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlalchemy as sa
from db import engine
import pandas as pd
import plotly.graph_objs as go

from db import session
from app import app
from models import MatrixResult, Drug, DrugMatrix, Model, WellResult

session = sa.orm.sessionmaker(bind=engine)()

my_model = session.query(Model).filter_by(name = 'SW620').one()
mydrug1 = session.query(Drug).filter(Drug.drug_name.startswith('LY260')).one()
mydrug2 = session.query(Drug).filter_by(drug_name = 'Irinotecan').one()

my_cmatrix = session.query(DrugMatrix).filter_by(lib1_id = mydrug1.id, lib2_id = mydrug2.id).one()

my_matrices = session.query(MatrixResult).filter_by(
    model_id = my_model.id,
    cmatrix = my_cmatrix.cmatrix,
    drugset_id = my_cmatrix.drugset_id
)

# my_matrix = next(x for x in my_matrices if x.barcode == 39354)
my_matrix = my_matrices.first()

df = pd.DataFrame([w.to_dict() for w in my_matrix.well_results])

# df = pd.read_csv("/Volumes/team215_pipeline/Curve_fitting/GDSC_007-A/combinations/barcode_39782_cmatrix_4.csv")

df = df.assign(lib1_dose = df.lib1_dose.str.extract(r'D(?P<lib1_dose>\d+)'))
df = df.assign(lib2_dose = df.lib2_dose.str.extract(r'D(?P<lib2_dose>\d+)'))

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

available_combo_metrics = ['HSA_excess', 'Bliss_excess']

layout = html.Div(children=[
    html.H1(children='Barcode: Cell line name : Drugs'),

    html.Div(children='''
    Combination result
    '''),

    dcc.Graph(
        figure=go.Figure(
            data=[
                go.Heatmap(
                    x = df.lib1_dose,
                    y = df.lib2_dose,
                    z = df.viability,
                    zmax = 1,
                    zmin = 0,
                    colorscale = 'Viridis'
                )
            ],
            layout=go.Layout(title='Viability')
        ),
        id='viability-heatmap'
    ),

    html.Div([
        dcc.Dropdown(
            id='combo-heatmap-zvalue',
            options = [{'label': i, 'value': i} for i in available_combo_metrics],
            value='HSA_excess'
        )
    ]),

    dcc.Graph(
        id='combo-heatmap'
    )
])

@app.callback(
    dash.dependencies.Output('combo-heatmap', 'figure'),
    [dash.dependencies.Input('combo-heatmap-zvalue', 'value')]
)
def update_combo_heatmap(combo_heatmap_zvalue):

    zvalue = df[combo_heatmap_zvalue]


    return{
        'data' : [
            go.Heatmap(
                x=df.lib1_dose,
                y=df.lib2_dose,
                z=zvalue,
                zmax=1,
                zmin=0,
                colorscale='Reds'
            )
        ],
        'layout' : go.Layout(
            title=combo_heatmap_zvalue
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)