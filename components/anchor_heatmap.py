import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import sqlalchemy as sa
from models import Project
from db import session
from models import Drug, AnchorSynergy

def layout(display_opt,project_id):
    try:
        project = session.query(Project).get(project_id)

    except sa.orm.exc.NoResultFound:
        return html.Div("Project not found")

    # get the data ready
    anchor_synergy = session.query(AnchorSynergy).filter(AnchorSynergy.project_id == project_id)

    df = pd.read_sql(anchor_synergy.statement, session.bind)
    lib_drugs = df['library_id'].drop_duplicates()
    anchor_drugs = df['anchor_id'].drop_duplicates()

    # create dictionary
    lib_names_ids = {}
    for ID in lib_drugs:
        l_drug = session.query(Drug).get(ID)
        lib_names_ids[l_drug.name] = ID

    anchor_names_ids = {}
    for ID in anchor_drugs:
        an_drug = session.query(Drug).get(ID)
        anchor_names_ids[an_drug.name] = ID

    # sort names
    # anc_name_sorted = sorted(list(anchor_names_ids.keys()), key=str.lower,reverse=True)
    # lib_name_sorted = sorted(list(lib_names_ids.keys()), key=str.lower,reverse=False)
    anc_name_sorted = sorted(list(anchor_names_ids.keys()), key=str.lower, reverse=False)
    lib_name_sorted = sorted(list(lib_names_ids.keys()), key=str.lower, reverse=True)

    # match sorted names with id
    anchor_drugs = [anchor_names_ids[name] for name in anc_name_sorted]
    lib_drugs = [lib_names_ids[name] for name in lib_name_sorted]

    synergy_counts_list = []

    #for anc_drug_id in anchor_drugs:
    for lib_drug_id in lib_drugs:
        synergy_counts = []

        #for lib_drug_id in lib_drugs:
        for anc_drug_id in anchor_drugs:
            synergy_count_per_combi_df = df.loc[(df['library_id'] == lib_drug_id) & (df['anchor_id'] == anc_drug_id) & (df['synergy'] == 1)]
            total_count_per_combi_df = df.loc[(df['library_id'] == lib_drug_id) & (df['anchor_id'] == anc_drug_id)]

            synergy_count_per_combi = synergy_count_per_combi_df['cell_line_name'].size
            total_count_per_combi = total_count_per_combi_df['cell_line_name'].size

            if (total_count_per_combi > 0):
                if(display_opt == 'count'):
                    z_label = '#synergistic cell lines'
                    synergy_counts.append(synergy_count_per_combi)
                else:
                    z_label = '%synergistic cell lines'
                    synergy_counts.append(round((synergy_count_per_combi/total_count_per_combi)*100))
            else:
                synergy_counts.append(None)

        synergy_counts_list.append(synergy_counts)

    if(display_opt == 'count'):
        fig = go.Figure(
            data=go.Heatmap(
                    z=synergy_counts_list,
                    # x=lib_name_sorted,
                    # y=anc_name_sorted,
                    y=lib_name_sorted,
                    x=anc_name_sorted,
                    colorbar=dict(title='Synergy#'),
                    #hovertemplate='Lib: %{x}<br>Anchor: %{y}<br>Synergy#: %{z}<extra></extra>'
                    hovertemplate = 'Anchor: %{x}<br>Lib: %{y}<br>Synergy#: %{z}<extra></extra>'
                ),
            layout = go.Layout(
                # xaxis={'type': 'category',
                #        'title': {"text": "Library",
                #                  "font": { "size": 30}
                #                 }
                #       },
                yaxis={'type': 'category',
                       'title': {"text": "Library",
                                 "font": {"size": 20}
                                 }
                       },
                width= 800,
                height=600,
                # yaxis={'type': 'category',
                #        'title': {"text": "Anchor",
                #              "font": { "size": 30}
                #              }
                #    },
                xaxis={'type': 'category',
                       'title': {"text": "Anchor",
                                 "font": {"size": 20}
                                 }
                       },
                margin=dict(t=100, b=50, l=200)
            )
        )
    else:
        fig = go.Figure(
            data=go.Heatmap(
                z=synergy_counts_list,
                # x=lib_name_sorted,
                # y=anc_name_sorted,
                y=lib_name_sorted,
                x=anc_name_sorted,
                colorbar=dict(title='Synergy%'),
                #hovertemplate='Lib: %{x}<br>Anchor: %{y}<br>Synergy%: %{z}%<extra></extra>'
                hovertemplate = 'Anchor: %{x}<br>Lib: %{y}<br>Synergy%: %{z}%<extra></extra>'
            ),
            layout=go.Layout(
                # xaxis={'type': 'category',
                #        'title': "Library"
                #        },
                yaxis={'type': 'category',
                       'title': {"text": "Library",
                                 "font": {"size": 20}
                                 }
                       },
                width= 800,
                height=600,
                # yaxis={'type': 'category',
                #        'title': "Anchor"
                #        },
                xaxis={'type': 'category',
                       'title': {"text": "Anchor",
                                 "font": {"size": 20}
                                 },
                       },
                margin=dict(t=100, b=50, l=200)
            )
        )
    fig.update_xaxes(side="top")

    return fig
