import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from datetime import datetime, timedelta
import datetime as dt
import plotly.express as px
from plotly.subplots import make_subplots
from data_process_aircall import def_df_support
from data_process_aircall import data_affid, line_support, agents_support

MY_PATH_AIRCALL = ("support.xlsx")
MY_PATH_JIRA = ("jira.xlsx")

@st.cache_data
def read_df_aircall():
    df = pd.read_excel(MY_PATH_AIRCALL)
    return df

@st.cache_data
def read_df_jira_support():
    df_tickets = pd.read_excel(MY_PATH_JIRA)
    df_tickets = df_tickets[df_tickets['Clé de projet'].isin(['SSIA'])]
    df_tickets = df_tickets[df_tickets['Création'] > '2022-01-01']
    return df_tickets

df_support = def_df_support(data_affid, data_affid, line_support, agents_support)


def parameters_support ():

    min_date = df_support['StartTime'].min()
    max_date = df_support['StartTime'].max()


    # Date de début et de fin par défaut
    start_date = st.date_input("Date de départ", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)


    #values = st.slider(
    #'Select a range of values',
    #1, 52, (50))

    metric = 52

    return start_date, end_date


from datetime import timedelta

def df_selection_support(df_support, start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtrer le DataFrame pour la période sélectionnée
    df_support = df_support[(df_support['StartTime'] >= start_date) & (df_support['StartTime'] <= end_date)]

    # Calculer la durée de la période sélectionnée
    duration = end_date - start_date

    # Déterminer la période précédente
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - duration

    # Filtrer le DataFrame pour la période précédente
    df2 = df_support[(df_support['StartTime'] >= prev_start_date) & (df_support['StartTime'] <= prev_end_date)]

    # Trier les deux DataFrames par la colonne 'Semaine' en ordre croissant
    df_support = df_support.sort_values(by='Semaine', ascending=True)
    df2 = df2.sort_values(by='Semaine', ascending=True)

    df2 = df_support

    return df_support, df2



#def df_selection_support(df_support,values):
#
#    df2 = df_support
#
#    today = date.today()
#    week_prior =  today - timedelta(weeks=values)
#    week_prior3 =  ((today - timedelta(weeks=values)) - timedelta(weeks=values))
#
#    df_support = df_support[df_support['Date'] >= week_prior]
#
#    df2 = df2[(df2['Date'] >= week_prior3) & (df2['Date'] <= week_prior)]
#    df2 = df2.sort_values(by='Semaine', ascending=True)
#
#    return df_support, df2

def convert_to_sixtieth(seconds):
    minutes, seconds = divmod(seconds, 60)  # Convertir en heures
    return f"{int(minutes)}m{int(seconds):02d}s"



def metrics_support(df_support, df2) : 

    Taux_de_service = int(df_support.Taux_de_service.mean() * 100)
    Taux_de_service_before = int(df2.Taux_de_service.mean() * 100)

    Entrant = df_support.groupby('Date').agg({'Entrant':'sum'}).mean().values[0].astype(int)
    Entrant_before  = df2.groupby('Date').agg({'Entrant':'sum'}).mean().values[0].astype(int)

    Numero_unique = df_support[(df_support['direction'] == 'inbound')].groupby('Date').agg({'Number':'nunique'}).mean().values[0].astype(int)
    Numero_unique_before  = df2.groupby('Date').agg({'Number':'nunique'}).mean().values[0].astype(int)

    temps_moy_appel = df_support[(df_support['InCallDuration'] > 0)].InCallDuration.mean()
    temps_moy_appel_before = df2[(df2['InCallDuration'] > 0)].InCallDuration.mean()
    tendance_appel = temps_moy_appel_before / temps_moy_appel

    Nombre_appel_jour_agent = round((df_support.groupby('Date').agg({'Entrant_connect':'sum'}).mean().values[0].astype(int) 
                        + df_support.groupby('Date').agg({'Sortant_connect':'sum'}).mean().values[0].astype(int)) / df_support.Effectif.mean(),0)


    def metric_tendance (tendance) : 
        if tendance > 1:
            signe = "-"
            tendance = tendance - 1
            tendance = abs(tendance) 
            tendance = (f"{signe}{((tendance)):.2f}%")
        else:
            signe = ""
            tendance = tendance - 1 
            tendance = abs(tendance)
            tendance = (f"{signe}{((tendance)):.2f}%")

        return tendance
    

    def metric_tendance_pourcentage (tendance) : 
        if tendance > 1:
            signe = "-"
            tendance = tendance - 1
            tendance = abs(tendance) 
            tendance = (f"{signe}{((tendance) * 100):.2f}%")
        else:
            signe = ""
            tendance = tendance - 1 
            tendance = abs(tendance)
            tendance = (f"{signe}{((tendance) * 100):.2f}%")

        return tendance
    
    tendance_taux = (Taux_de_service_before - Taux_de_service)
    tendance_taux = metric_tendance(tendance_taux)

    tendance_entrant = Entrant_before / Entrant
    tendance_entrant = metric_tendance_pourcentage(tendance_entrant)

    tendance_unique = Numero_unique_before / Numero_unique
    tendance_unique = metric_tendance_pourcentage(tendance_unique)


    return [Taux_de_service ,tendance_taux, Entrant, tendance_entrant, Numero_unique, tendance_unique, 
            temps_moy_appel, tendance_appel, Nombre_appel_jour_agent]



def tickets_support(df_tickets):
    filtered_df = df_tickets.copy()


    df_grouped_ticket = filtered_df.groupby('Semaine').agg({'Clé de ticket':'count'}).reset_index()

    #fig_activite_ticket = px.bar(df_grouped_ticket, x="Semaine", y="Clé de ticket")

    semaines_uniques = df_tickets['Semaine'].unique()
    resultats = []

    for semaine in semaines_uniques: 
        incident = df_tickets[(df_tickets['Semaine'] == str(semaine)) & (df_tickets["Customer Request Type"].str.contains('Déclarer un incident'))]['Clé de ticket'].count()
        information = df_tickets[(df_tickets['Semaine'] == str(semaine)) & (df_tickets["Customer Request Type"].str.contains('Demander une information'))]['Clé de ticket'].count()
        amelioration = df_tickets[(df_tickets['Semaine'] == str(semaine)) & (df_tickets["Customer Request Type"].str.contains('Suggérer une amélioration'))]['Clé de ticket'].count()                        
        resultats.append({'Semaine': semaine, 'Déclarer un incident': incident, 'Demander une information': information, 'Suggérer une amélioration':amelioration})


        df_resultats = pd.DataFrame(resultats)
    


    df_resultats = df_resultats.sort_values(['Semaine'], ascending=True)
        # Initialisation du graphique
    fig_activite_ticket = px.bar()

    liste_form = ['Déclarer un incident', 'Demander une information', 'Suggérer une amélioration']

    # Ajout de chaque série de données au graphique
    for form in liste_form:
        fig_activite_ticket.add_bar(x=df_resultats['Semaine'], y=df_resultats[form], name=form)

    

        fig_activite_ticket.update_layout(
        title_text="Activité & Taux de service / jour",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )



    return fig_activite_ticket

    

    

