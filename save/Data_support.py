
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import pandas as pd


def graph_activite (df_support) : 

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    data_graph1 = df_support.groupby(['Semaine']).agg({'Entrant':'sum',
                                                    'Entrant_connect':'sum',
                                                    'Number':'nunique',
                                                    'Effectif':'mean'}).rename(columns = {"Number":"Numero_unique",}).reset_index()

    data_graph1 = data_graph1.groupby(['Semaine']).agg({'Entrant':'mean',
                                                    'Entrant_connect':'mean',
                                                    'Numero_unique':'mean',
                                                    'Effectif':'mean'}).reset_index()

    #data_graph1['Semaine'] = pd.to_datetime(data_graph1['Semaine'] + '-1', format='%Y-%W-%w')
    #data_graph1['Semaine'] = pd.to_datetime(data_graph1['Semaine'])
    #data_graph1['Date'] = pd.to_datetime(data_graph1['Date'])

    data_graph1['Taux_de_service_support'] = (data_graph1['Entrant_connect'] 
                                            / data_graph1['Entrant'])

    #data_graph1 = data_graph1.reset_index()

    data_graph1['100%'] = 1

    # Créer la figure avec plusieurs sous-graphiques
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]] )

    # Ajouter les barres pour Taux
    fig.add_trace(go.Bar(x=data_graph1['Semaine'], y=data_graph1['Taux_de_service_support'], name='Taux', opacity=0.7), secondary_y=True,)

    fig.update_traces(
            text=data_graph1['Taux_de_service_support'], texttemplate='%{text:.0%}', 
                    secondary_y=True,      
        )

    # Ajouter les lignes empilées pour Numero_unique et Entrant
    fig.add_trace(go.Scatter(x=data_graph1['Semaine'], y=data_graph1['Numero_unique'], name='Numero_unique', fill='tozeroy'), secondary_y=False,)
    fig.add_trace(go.Scatter(x=data_graph1['Semaine'], y=data_graph1['Entrant'], name='Entrant', fill='tozeroy'), secondary_y=False,)

    fig.update_yaxes(range = [0,1], secondary_y=True)
    fig.update_yaxes(tickformat=".0%", secondary_y=True)

    # Ajouter des légendes et étiquettes
    fig.update_layout(title='Graphique avec Taux en barres et Numero_unique/Entrant en aires empilées',
                    template='plotly_dark',
                    xaxis_title='Semaine',
                    yaxis_title='Valeurs',
                    )


    fig.update_layout(
            title_text="Activité & Taux de service - 20 semaines",
            template='plotly_dark',
            #height=400,
            #width=1440,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    
    return fig




def graph_taux_jour (df_support): 


    data_graph2 = df_support.groupby(['Semaine','Date', 'Jour']).agg({'Entrant':'sum',
                                                                'Entrant_connect':'sum',
                                                                'Number':'nunique',
                                                                'Effectif':'mean'})
    data_graph2 = data_graph2.groupby(['Semaine','Date', 'Jour']).agg({'Entrant':'mean',
                                                    'Entrant_connect':'mean',
                                                    'Number':'mean',
                                                    'Effectif':'mean'}).rename(columns = {"Number":"Numero_unique",})
    data_graph2['Taux_de_service_support'] = (data_graph2['Entrant_connect'] 
                                            / data_graph2['Entrant'])

    data_graph2 = data_graph2.reset_index()

    data_moyenne = data_graph2.groupby("Jour")[["Taux_de_service_support", "Entrant"]].mean().reset_index()


    derniere_semaine = data_graph2['Semaine'].iloc[-1]
    data_derniere_semaine = data_graph2.loc[(data_graph2['Semaine'] == derniere_semaine)]


    #def graph_taux_semaine():
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    last_week = [data_graph2.tail(1).values[0,0]]


    fig.add_trace(
        go.Bar(x=data_moyenne['Jour'], y=data_moyenne['Taux_de_service_support'], name="Taux de service"),
        secondary_y=False,)

    fig.add_trace(
        go.Line(x=data_moyenne['Jour'], y=data_moyenne['Entrant'], name="Entrant"),
        secondary_y=True,)
    
    fig.update_yaxes(range = [0,1], secondary_y=False)
    fig.update_yaxes(range = [20,150], secondary_y=True)
    fig.update_yaxes(tickformat=".0%", secondary_y=False)


    fig.update_layout(title='Graphique avec Taux en barres et Numero_unique/Entrant en aires empilées',
                template='plotly_dark',
                xaxis_title='Semaine',
                yaxis_title='Valeurs',
                )


    fig.update_layout(
        title_text="Activité & Taux de service / jour",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

       
    
    return fig




def graph_taux_heure (df_support): 

    data_by_heure = df_support.groupby(['Heure']).agg({'Entrant':'sum', 
                                                   'Entrant_connect':'sum'}).query("Heure > 8 & Heure < 18 != 12").reset_index()


    data_by_heure['Taux_de_service_support'] = data_by_heure['Entrant_connect'] / data_by_heure['Entrant']


    #def graph_taux_heure(): 
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=data_by_heure['Heure'], y=data_by_heure['Entrant'], name="Entrant"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Bar(x=data_by_heure['Heure'], y=data_by_heure['Taux_de_service_support'], name="Taux de service"),
        secondary_y=False,
    )


    # Formater les étiquettes de l'axe y en pourcentages
    fig.update_yaxes(range = [0,1], secondary_y=False)
    fig.update_yaxes(tickformat=".0%", secondary_y=False)
    #fig.update_yaxes(range = [50,150], secondary_y=True)

    fig.update_layout(title='Graphique avec Taux en barres et Numero_unique/Entrant en aires empilées',
                template='plotly_dark',
                xaxis_title='Semaine',
                yaxis_title='Valeurs',
                )


    fig.update_layout(
        title_text="Activité & Taux de service / Heure",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig



def graph_charge_affid_stellair(df_support):
    df_support['Tags'] = df_support['Tags'].astype(str)
    semaines_uniques = df_support['Semaine'].unique()
    resultats = []

    for semaine in semaines_uniques: 
        stellair = df_support[(df_support['Semaine'] == str(semaine)) & (~df_support["Tags"].str.contains('STE 1er Pas') & (df_support["Tags"].str.contains('STE')))]['Count'].sum()
        affid = df_support[(df_support['Semaine'] == str(semaine)) & (df_support["Tags"].str.contains('AFD'))]['Count'].sum()
        resultats.append({'Semaine': semaine, 'stellair': stellair, 'affid': affid})

    df_resultats = pd.DataFrame(resultats)

    df_resultats['Charge_support_call_stellair'] = df_resultats['stellair'] / (df_resultats['stellair'] + df_resultats['affid'])
    df_resultats['Charge_support_call_affid'] = df_resultats['affid'] / (df_resultats['stellair'] + df_resultats['affid'])
    
    liste_fig_stellair_affid = ['Charge_support_call_stellair', 'Charge_support_call_affid']
    fig = px.bar(df_resultats, 
                x = df_resultats.Semaine,
                y = [c for c in liste_fig_stellair_affid],
                template = 'plotly_dark',
                )
    

    fig.update_yaxes(tickformat=".0%", secondary_y=False)

    fig.update_layout(
        title_text="Activité & Taux de service / Heure",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig





# Désactiver l'affichage du graphique
#pyo.init_notebook_mode(connected=False)

### filtrer le dataframe sur la derniere valeur de la colonne "Semaine"





#fig20.add_trace(go.Line(x=data_graph1['Semaine'], y=data_graph1['Effectif']), secondary_y=False,)




    # Affichage du graphique
    #chart.show()