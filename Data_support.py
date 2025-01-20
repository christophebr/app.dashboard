
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


def graph_activite(df_support):
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Filtrage des données pour l'activité entrante
    data_graph1 = df_support[df_support['direction'] == 'inbound']

    # Agrégation des données par semaine et date
    data_graph2 = (
        data_graph1.groupby(['Semaine'])
        .agg(
            Entrant=('Entrant', 'sum'),
            Entrant_connect=('Entrant_connect', 'sum'),
            Numero_unique=('Number', 'nunique'),
            Effectif=('Effectif', 'mean')
        )
        .reset_index()
    )

    # Agrégation finale par semaine
    data_graph3 = (
        data_graph2.groupby('Semaine')[['Entrant', 'Entrant_connect', 'Numero_unique', 'Effectif']]
        .mean()
        .reset_index()
    )

    # Calcul du taux de service support
    data_graph3['Taux_de_service_support'] = (
        data_graph3['Entrant_connect'] / data_graph3['Entrant']
    )

    # Ajout d'une colonne 100%
    data_graph3['100%'] = 1

    # Création de la figure avec des sous-graphiques
    fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])

    # Ajouter les barres pour le Taux de service support
    fig.add_trace(
        go.Bar(
            x=data_graph3['Semaine'],
            y=data_graph3['Taux_de_service_support'],
            name='Taux',
            opacity=0.7,
            text=data_graph3['Taux_de_service_support'],
            texttemplate='%{text:.0%}'
        ),
        secondary_y=True,
    )

    # Ajouter les lignes empilées pour Numero_unique, Entrant_connect et Entrant
    fig.add_trace(
        go.Scatter(
            x=data_graph3['Semaine'],
            y=data_graph3['Numero_unique'],
            name='Numero_unique',
            fill='tozeroy'
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=data_graph3['Semaine'],
            y=data_graph3['Entrant_connect'],
            name='Entrant_connect',
            fill='tozeroy'
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=data_graph3['Semaine'],
            y=data_graph3['Entrant'],
            name='Entrant',
            fill='tozeroy'
        ),
        secondary_y=False,
    )

    # Mise à jour des axes Y pour les pourcentages
    fig.update_yaxes(range=[0, 1], secondary_y=True)
    fig.update_yaxes(tickformat=".0%", secondary_y=True)

    # Configuration de la mise en page et des légendes
    fig.update_layout(
        title='Graphique avec Taux en barres et Numero_unique/Entrant en aires empilées',
        template='plotly_dark',
        xaxis_title='Semaine',
        yaxis_title='Valeurs',
        title_text="Activité & Taux de service - 20 semaines",
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

    df_support  = df_support[df_support['direction'] == 'inbound']

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
    #df_support['Tags'] = df_support['Tags'].astype(str)
    semaines_uniques = df_support['Semaine'].unique()
    resultats = []

    for semaine in semaines_uniques: 
        stellair = df_support[((df_support['Semaine'] == str(semaine)) 
                              & (df_support["Logiciel"].str.contains('Stellair'))) ]['Count'].sum()
        affid = df_support[(df_support['Semaine'] == str(semaine)) & (df_support["Logiciel"].str.contains('Affid'))]['Count'].sum()
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
        title_text="Activité en % - NXT & Stellair",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    liste_fig2_stellair_affid = ['stellair', 'affid']
    fig2 = px.bar(df_resultats, 
                x = df_resultats.Semaine,
                y = [c for c in liste_fig2_stellair_affid],
                template = 'plotly_dark',
                )
    
    fig2.update_layout(
        title_text="Activité en Nb - NXT & Stellair",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    
    return fig, fig2


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



def calcul_taux_reponse2(df):
    #today = pd.Timestamp.today()  # Assurez-vous d'avoir 'today' défini ici
    #week = today - timedelta(weeks=nb)
    
    # Filtrer les données pour les dernières 'nb' semaines
    #df = df[df['Date'] >= week]x

    # Convertir la colonne 'LastState' en booléen (True si 'yes', sinon False)

    df = df.loc[~df["Number"].isin(["anonymous"])]

    df['LastState'] = df['LastState'] == 'yes'

    # Séparer les appels entrants et sortants
    entrants = df[df['direction'] == 'inbound']
    sortants = df[df['direction'] == 'outbound']

    # Regrouper les appels sortants et entrants par Date et Number
    grouped_sortants = sortants.groupby(['Date', 'Number']).agg({
        'LastState': 'any',  # Si au moins un appel a eu une réponse
        'StartTime':'mean'   # Calculer la moyenne des heures de début
    }).reset_index()
    
    grouped_entrants = entrants.groupby(['Date', 'Number']).agg({
        'LastState': 'any',
        'StartTime':'mean'
    }).reset_index()

    # Renommer les colonnes pour les appels sortants
    grouped_sortants = grouped_sortants.rename(columns={'LastState': 'Repondu_sortant', 'StartTime': 'Heure_sortant'})

    # Fusionner les appels entrants et sortants sur Date et Number
    merged = pd.merge(grouped_entrants, grouped_sortants, on=['Date', 'Number'], how='left')

    # Remplir les valeurs manquantes pour 'Repondu_sortant' avec False
    merged['Repondu_sortant'].fillna(False, inplace=True)

    # Calculer le statut total de réponse
    merged['Repondu_total'] = merged['LastState'] | merged['Repondu_sortant']

    # Calculer le taux de réponse
    taux_reponse = merged['Repondu_total'].mean()

    # Convertir les colonnes de temps en format datetime
    merged['StartTime'] = pd.to_datetime(merged['StartTime'])
    merged['Heure_sortant'] = pd.to_datetime(merged['Heure_sortant'])

    # Calculer la différence en minutes entre les appels entrants et sortants (exclure les cas où Heure_sortant < StartTime)
    merged['minute_difference'] = np.where(
        (merged['Repondu_sortant'] == True) & (merged['Heure_sortant'] >= merged['StartTime']),
        (merged['Heure_sortant'] - merged['StartTime']) / pd.Timedelta(minutes=1),
        np.nan
    )

    # Filtrer les valeurs négatives (ce cas est déjà traité en excluant les lignes où Heure_sortant < StartTime)
    filtered_minute_difference = merged['minute_difference'][merged['minute_difference'] >= 0]

    # Calculer la moyenne des différences en minutes
    mean_difference = filtered_minute_difference.mean()

    # Comptage des contacts qui n'ont pas été répondus (LastState == False)
    contact_counts = df[df['LastState'] == False].groupby(['Date', 'Number']).size().reset_index(name='ContactCount')

    # Fusionner les contacts non répondus avec le DataFrame fusionné
    merged = pd.merge(merged, contact_counts, on=['Date', 'Number'], how='left')

    # Remplacer les valeurs manquantes dans ContactCount par 0
    merged['ContactCount'].fillna(0, inplace=True)

    return taux_reponse, mean_difference, merged


def calcul_productivite_appels(df_support, agent):

    df_support_all = df_support

    df_grouped = df_support.groupby(['Date', 'UserName']).size().reset_index(name='TotalAppels')
    df_grouped = df_grouped[df_grouped['UserName'] == agent].groupby(['Date']).agg({'TotalAppels':'mean'})

    df_support = df_support[df_support['UserName'] == agent].groupby(['Date']).agg({'InCallDuration':'sum'})

    df_support = pd.merge(df_support, df_grouped, on='Date', how='left')
    
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

    if pd.notnull(com_jour):  # Vérifie si com_jour n'est pas NaT
        com_jour = com_jour.strftime('%H:%M:%S')
    else:
        com_jour = None  # Ou une autre valeur par défaut, comme '' ou '00:00:00'

    temps_moy_com = (df_support['InCallDuration'] /  df_support['TotalAppels']).mean()
    nb_appels_jour = df_support['TotalAppels'].mean()

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
    df_charge_agent[agent] = df_charge_agent['InCallDuration']
    df_charge_agent = df_charge_agent.groupby(['Date']).agg({agent:'mean',}).reset_index()
    df_charge_agent = df_charge_agent[['Date', agent]]
    
    return df_charge_agent


def graph_charge_agent (df, liste_agents): 

    data_graph2 = df


    data_graph2['Cible'] = data_graph2['Effectif'] * 0.70 

    #liste_agents = ['Pierre GOUPILLON', 'Mourad HUMBLOT', 'Olivier Sainte-Rose', 'Frederic SAUVAN', 'Archimede KESSI']

    data_graph2['Date'] = pd.to_datetime(data_graph2['Date'])

    data_weekly = data_graph2.resample('W-Mon', on='Date', label='left', origin='start_day').mean().shift(1, freq=pd.DateOffset(days=1)).reset_index()


    #def graph_agent_activite(): 

    fig6 = px.bar(data_weekly, 
                x = data_weekly.Date,
                y = [c for c in liste_agents],
                template = 'plotly_dark',
                title = 'Stacked bar chart using px.bar()', 
                )


    #fig6.add_trace(go.Scatter(x=data_weekly.Date,
    #                        y=data_weekly['Cible'],
    #                        mode='lines',
    #                        name='Cible',
    #                        line=dict(color='red'),
    #                        ))

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
           (df_support['LastState'] == 'yes')].groupby(['Semaine','line','direction']).agg({'Date':'count'}).reset_index()
    
    df_support['Empilement'] = df_support.apply(
    lambda row: f"inbound - {row['line']}" if row['direction'] == 'inbound' else row['direction'], axis=1
    )
    #df_support = df_support.sort_values(by='Semaine', ascending=False)
    ordre_semaines = sorted(df_support['Semaine'].unique(), key=lambda x: (int(x[1:5]), int(x[6:])))
    df_support['Semaine'] = pd.Categorical(df_support['Semaine'], categories=ordre_semaines, ordered=True)

    fig = px.histogram(df_support, x="Semaine", y='Date', color="Empilement", 
                       title= agent)
    
    fig.update_layout(
         xaxis=dict(categoryorder="array", categoryarray=ordre_semaines),
         yaxis_title="Appels",
         yaxis=dict(range=[0, 200])  # Ajuste la plage de l'axe y entre 0 et 100
        )
    

    return fig





def graph_tag(logiciel, df_support): 

    df = df_support[df_support['Tags'].str.startswith(logiciel)]

    df['categories_split'] = df['Tags'].str.split(' / ')  # Séparer par ' / '
    df_exploded = df.explode('categories_split')  # Convertir chaque sous-catégorie en ligne distincte

    counts = df_exploded['categories_split'].value_counts().reset_index()
    counts.columns = ['category', 'count']

    top_20 = counts.head(20)
    top_20 = top_20.sort_values(by='count', ascending=True)

    fig = px.bar(top_20, x='count', y='category', orientation='h', title='Top 20 des catégories' + " " +logiciel)

    temps_moy_appel_cat = df[(df['InCallDuration'] > 0)].InCallDuration.mean()

    return fig, temps_moy_appel_cat
    






# Désactiver l'affichage du graphique
#pyo.init_notebook_mode(connected=False)


#from functools import reduce




# Désactiver l'affichage du graphique
#pyo.init_notebook_mode(connected=False)

### filtrer le dataframe sur la derniere valeur de la colonne "Semaine"





#fig20.add_trace(go.Line(x=data_graph1['Semaine'], y=data_graph1['Effectif']), secondary_y=False,)




    # Affichage du graphique
    #chart.show()
