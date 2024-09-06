import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from datetime import datetime, timedelta
import datetime as dt
import plotly.express as px
from plotly.subplots import make_subplots

MY_PATH_AIRCALL = ("support.xlsx")
MY_PATH_JIRA = ("jira.xlsx")

@st.cache_data
def read_df_aircall():
    df = pd.read_excel(MY_PATH_AIRCALL)
    return df

#@st.cache_data
#def read_df_jira_support():
#    df_tickets = pd.read_excel(MY_PATH_JIRA)
#    return df_tickets


def parameters_support ():

    #option_pipeline = st.selectbox(
    #"Choix du pipeline",
    #selection,
    #placeholder="Select contact method...",
    #)

    values = st.slider(
    'Select a range of values',
    1, 52, (52))

    metric = 52

    return values


def df_selection_support(df_support, df2, values):

    df2['Date'] = df2['Date'].dt.date
    df_support['Date'] = df_support['Date'].dt.date

    today = date.today()

    week_prior =  today - timedelta(weeks=values)
    week_prior3 =  ((today - timedelta(weeks=values)) - timedelta(weeks=values))

    df_support = df_support[df_support['Date'] >= week_prior]
    df_support = df_support.sort_values(by='Semaine', ascending=True)

    df2 = df2[(df2['Date'] >= week_prior3) & (df2['Date'] <= week_prior)]
    df2 = df2.sort_values(by='Semaine', ascending=True)


    #df_tickets = df_tickets[df_tickets['Date'] >= week_prior]
    #df_tickets = df_tickets.sort_values(by='Semaine', ascending=True)

    #df3 = df3[(df3['Date'] >= week_prior3) & (df3['Date'] <= week_prior)]
    #df3 = df3.sort_values(by='Semaine', ascending=True)

    return df_support, df2


def metrics_support(df_support, df2) : 

    Taux_de_service = int(df_support.Taux_de_service.mean() * 100)
    Taux_de_service_before = int(df2.Taux_de_service.mean() * 100)

    Entrant = df_support.groupby('Date').agg({'Entrant':'sum'}).mean().values[0].astype(int)
    Entrant_before  = df2.groupby('Date').agg({'Entrant':'sum'}).mean().values[0].astype(int)

    Numero_unique = df_support.groupby('Date').agg({'Number':'nunique'}).mean().values[0].astype(int)
    Numero_unique_before  = df2.groupby('Date').agg({'Number':'nunique'}).mean().values[0].astype(int)

    temps_moy_appel = df_support.InCallDuration.mean()
    temps_moy_appel_before = df2.InCallDuration.mean()
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





def tickets_support(df_tickets, option_pipeline, defaut_val):
    filtered_df = df_tickets.copy()

    if option_pipeline != defaut_val and option_pipeline != "All":
        filtered_df = filtered_df[filtered_df['Clé de projet'] == option_pipeline]


    df_grouped_ticket = filtered_df.groupby('Semaine').agg({'Clé de ticket':'count'}).reset_index()



    return df_grouped_ticket

    

    

