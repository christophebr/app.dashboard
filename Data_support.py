
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


def graph_activite (df_support) : 

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    data_graph1 = df_support[((df_support['direction'] == 'inbound'))]
    
    data_graph1 = data_graph1.groupby(['Semaine']).agg({'Entrant':'sum',
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


def calcul_taux_reponse (df_support): 
    df = df_support

    df['LastState'] = df['LastState'] == 'yes'

    entrants = df[df['direction'] == 'inbound']
    sortants = df[df['direction'] == 'outbound']

    grouped_sortants = sortants.groupby(['Date', 'Number']).agg({'LastState': 'any', 
                                                                 'StartTime':'mean'}).reset_index()
    grouped_entrants = entrants.groupby(['Date', 'Number']).agg({'LastState': 'any', 
                                                                 'StartTime':'mean'}).reset_index()

    grouped_sortants = grouped_sortants.rename(columns={'LastState': 'Repondu_sortant'})
    grouped_sortants = grouped_sortants.rename(columns={'StartTime': 'Heure_sortant'})

    merged = pd.merge(grouped_entrants, grouped_sortants, on=['Date', 'Number'], how='left')

    merged['Repondu_sortant'].fillna(False, inplace=True)

    merged['Repondu_total'] = merged['LastState'] | merged['Repondu_sortant']

    taux_reponse = merged['Repondu_total'].mean()

    merged['StartTime'] = pd.to_datetime(merged['StartTime'])
    merged['Heure_sortant'] = pd.to_datetime(merged['Heure_sortant'])

    merged['minute_difference'] = np.where(
        merged['Repondu_sortant'] == True,
        (merged['Heure_sortant'] - merged['StartTime']) / pd.Timedelta(minutes=1),
        np.nan
    )

    # Filtrer les valeurs négatives
    filtered_minute_difference = merged['minute_difference'][merged['minute_difference'] >= 0]

    # Calculer la moyenne
    mean_difference = filtered_minute_difference.mean()

    return taux_reponse, mean_difference, merged


def calcul_productivite_appels(df_support, agent): 

    df_support = df_support[df_support[agent] == 1].groupby(['Date']).agg({'Number':'count', 
                                                    'InCallDuration':'sum'})
    
    def convert_minutes_to_hhmmss(minutes):
        # Convertir les minutes en heures, minutes et secondes
        hours = int(minutes // 3600)
        minutes = int(minutes % 60)
        seconds = int((minutes % 1) * 60)
        # Formater en hh:mm:ss
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    df_support['InCallDuration_format'] = df_support['InCallDuration'].apply(convert_minutes_to_hhmmss)
    df_support['InCallDuration_format'] = pd.to_datetime(df_support['InCallDuration_format'])

    com_jour = df_support['InCallDuration_format'].mean()
    com_jour = com_jour.strftime('%H:%M:%S')
    temps_moy_com = (df_support['InCallDuration'] /  df_support['Number']).mean()
    nb_appels_jour = df_support['Number'].mean()

    #df_support['Productivite_appels'] = (df_support['Number'] / 420) * 60

    #taux = df_support['Productivite_appels'].mean()

    return com_jour, temps_moy_com, nb_appels_jour


def nan_tags_appels (df, agent):
    df = df[(df[agent] == 1) & (df['Tags'] == 'nan')].groupby('Semaine').count().reset_index()[['Semaine', 'Tags']]
    
    taux = df['Tags'].mean()
    
    return df, taux


def charge_agents (agent, df) : 
    df_charge_agent = df[(df['UserName'] == agent )]
    df_charge_agent = df_charge_agent.groupby(['Date']).agg({'InCallDuration':'sum'})
    df_charge_agent['InCallDuration'] = df_charge_agent['InCallDuration'] / 60 
    df_charge_agent[agent] = df_charge_agent['InCallDuration'] / 180
    df_charge_agent = df_charge_agent.groupby(['Date']).agg({agent:'mean',}).reset_index()
    df_charge_agent = df_charge_agent[['Date', agent]]
    
    return df_charge_agent


def graph_charge_agent (df): 

    data_graph2 = df


    data_graph2['Cible'] = data_graph2['Effectif'] * 0.70 

    liste10 = ['Pierre GOUPILLON', 'Mourad HUMBLOT', 'Olivier Sainte-Rose', 'Frederic SAUVAN', 'Archimede KESSI']

    data_graph2['Date'] = pd.to_datetime(data_graph2['Date'])

    data_weekly = data_graph2.resample('W-Mon', on='Date', label='left', origin='start_day').mean().shift(1, freq=pd.DateOffset(days=1)).reset_index()


    #def graph_agent_activite(): 

    fig6 = px.bar(data_weekly, 
                x = data_weekly.Date,
                y = [c for c in liste10],
                template = 'plotly_dark',
                title = 'Stacked bar chart using px.bar()', 
                )


    fig6.add_trace(go.Scatter(x=data_weekly.Date,
                            y=data_weekly['Cible'],
                            mode='lines',
                            name='Cible',
                            line=dict(color='red'),
                            ))

    fig6.update_layout(
            title_text="Activité & Taux de service - 20 semaines",
            template='plotly_dark',
            height=400,
            width=1440)

    fig6.update_xaxes(
            tickangle = 90,
            tickmode='array',
            tickvals=data_weekly['Date'],
            ticktext=data_weekly['Date'].dt.strftime('%Y-%U'),
            )
    
    return fig6


def charge_entrant_sortant (df_support, agent): 
    df_support = df_support[(df_support['UserName'] == agent) & 
           (df_support['LastState'] == 'yes')].groupby(['Semaine', 'direction']).agg({'line':'count'}).reset_index()
    

    fig = px.histogram(df_support, x="Semaine", y='line', color="direction", 
                       title= agent)
    
    fig.update_layout(
         yaxis_title="Appels",
         yaxis=dict(range=[0, 200])  # Ajuste la plage de l'axe y entre 0 et 100
        )
    

    return fig
    






# Désactiver l'affichage du graphique
#pyo.init_notebook_mode(connected=False)


#from functools import reduce




# Désactiver l'affichage du graphique
#pyo.init_notebook_mode(connected=False)

### filtrer le dataframe sur la derniere valeur de la colonne "Semaine"





#fig20.add_trace(go.Line(x=data_graph1['Semaine'], y=data_graph1['Effectif']), secondary_y=False,)




    # Affichage du graphique
    #chart.show()
