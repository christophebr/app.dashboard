import pandas as pd
import numpy as np
import datetime as dt
import os
from functools import reduce
import re
import warnings
warnings.filterwarnings('ignore')
from datetime import date, timedelta, datetime, time
import plotly.express as px

# Définir les chemins
path_source_affid_hubspot_ticket = 'data/Affid/hubspot/ticket'
path_source_affid_hubspot_agent = 'data/Affid/hubspot/agent'

# Chargement des fichiers tickets
files_hubspot_ticket = [file for file in os.listdir(path_source_affid_hubspot_ticket) if not file.startswith('.')]

data_affid_hubspot_ticket = pd.DataFrame()

for file in files_hubspot_ticket:
    current_data_hubspot = pd.read_excel(os.path.join(path_source_affid_hubspot_ticket, file))
    data_affid_hubspot_ticket = pd.concat([data_affid_hubspot_ticket, current_data_hubspot], ignore_index=True)

# Chargement des fichiers agents
files_hubspot_agent = [file for file in os.listdir(path_source_affid_hubspot_agent) if not file.startswith('.')]

data_affid_hubspot_agent = pd.DataFrame()

for file in files_hubspot_agent:
    current_data_hubspot_agent = pd.read_excel(os.path.join(path_source_affid_hubspot_agent, file))
    data_affid_hubspot_agent = pd.concat([data_affid_hubspot_agent, current_data_hubspot_agent], ignore_index=True)

def processing_hubspot(data_affid_hubspot_ticket, data_affid_hubspot_agent):
    # Filtrer les activités agent
    data_affid_hubspot_agent = data_affid_hubspot_agent[
        (data_affid_hubspot_agent["Nombre d'e-mails envoyés"] == 1) &
        (data_affid_hubspot_agent["Conversation ID"] != "(Aucune valeur)") &
        (data_affid_hubspot_agent['Source'].isin(['Chat', 'Formulaire', 'E-mail']))
    ]

    data_affid_hubspot_agent["Date d'activité"] = pd.to_datetime(data_affid_hubspot_agent["Date d'activité"])
    data_affid_hubspot_agent["Semaine"] = data_affid_hubspot_agent["Date d'activité"].dt.strftime("S%Y-%V")
    data_affid_hubspot_agent.sort_values(["Date d'activité"], ascending=True, inplace=True)

    return data_affid_hubspot_ticket, data_affid_hubspot_agent

data_affid_hubspot_ticket, data_affid_hubspot_agent = processing_hubspot(data_affid_hubspot_ticket, data_affid_hubspot_agent)

def processing_df_ticket(data_affid_hubspot_ticket_process): 
    df = data_affid_hubspot_ticket.copy()

    # Conversion des colonnes en datetime (assure que ces colonnes existent)
    df['Date de création'] = pd.to_datetime(df['Date de création'], format='%d/%m/%Y %H:%M', errors='coerce')
    df["Date de la première réponse par e-mail de l'agent"] = pd.to_datetime(df["Date de la première réponse par e-mail de l'agent"], format='%d/%m/%Y %H:%M', errors='coerce')

    # Filtrer les lignes non convertibles (optionnel)
    df = df.dropna(subset=['Date de création', "Date de la première réponse par e-mail de l'agent"])

    def calculate_working_hours(start, end):
        start_hour, end_hour = 9, 18
        total_working_hours = 0
        current = start
        while current < end:
            next_day = (current + pd.Timedelta(days=1)).normalize()
            # Jour ouvré (0=lundi, 4=vendredi)
            if current.weekday() < 5:
                work_start = current.replace(hour=start_hour, minute=0, second=0)
                work_end = current.replace(hour=end_hour, minute=0, second=0)
                day_start = max(current, work_start)
                day_end = min(end, work_end, next_day)
                if day_start < day_end:
                    total_working_hours += (day_end - day_start).total_seconds() / 3600
            current = next_day
        return total_working_hours

    df['working_hours'] = df.apply(lambda row: calculate_working_hours(row['Date de création'], row["Date de la première réponse par e-mail de l'agent"]), axis=1)

    def convert_hours_to_hms(hours):
        total_seconds = int(hours * 3600)
        h, remainder = divmod(total_seconds, 3600)
        m, s = divmod(remainder, 60)
        return f"{h:02}:{m:02}:{s:02}"

    df['working_hours_hms'] = df['working_hours'].apply(convert_hours_to_hms)
    df["Semaine"] = df['Date de création'].dt.strftime("S%Y-%V")

    return df

df_affid_hubspot_ticket = processing_df_ticket(data_affid_hubspot_ticket)

def repartition_activite_agent(data_affid_hubspot_agent):
    df = data_affid_hubspot_agent.groupby("Propriétaire du ticket").agg({
        "Nombre d'e-mails envoyés": "sum",
        "Ticket ID": "nunique"
    }).reset_index()

    fig = px.pie(
        df, 
        names="Propriétaire du ticket", 
        values="Nombre d'e-mails envoyés", 
        title="Répartition des e-mails envoyés par propriétaire de ticket"
    )
    return fig

#graph_repartition_activite_agent = repartition_activite_agent(data_affid_hubspot_agent)

def activite_ticket_source_client(df):
    # Filtrer par pipeline et sources
    #df = df[df['Pipeline'].isin([pipeline])]
    df = df[df['Source'].isin(['Chat', 'E-mail', 'Formulaire'])].groupby(['Semaine', 'Pipeline'])['Ticket ID'].nunique().reset_index()

    fig = px.bar(
        df,
        x="Semaine",
        y="Ticket ID",
        color="Pipeline",
        title="Tickets créés par les clients via le chat, l'email et les formulaires",
        labels={"working_hours": "Heures de travail", "Semaine": "Semaine"},
    )
    return fig

def mails_envoyes_agent(df):
    graph_affid_hubspot_agent = df.groupby(['Semaine', 'Propriétaire du ticket'])["Nombre d'e-mails envoyés"].sum().reset_index()

    semaines_ordonnees = graph_affid_hubspot_agent["Semaine"].unique().tolist()

    fig = px.bar(
        graph_affid_hubspot_agent,
        x="Semaine",
        y="Nombre d'e-mails envoyés",
        color="Propriétaire du ticket",
        title="Nombre E-mails envoyés / Agent ",
        labels={"working_hours": "Heures de travail", "Semaine": "Semaine"},
        category_orders={"Semaine": semaines_ordonnees}
    )

    return fig

def sla_2h (df, pipeline): 

    df_sla_2h = df[(df['Pipeline'] == pipeline) & (df['working_hours'] < 2) & (df['working_hours'] > 0.1)].groupby(['Semaine'])['working_hours'].count().reset_index().rename(columns={'working_hours': 'SLA < 2h'})

    df_tickets_ssia = df[(df['Pipeline'] == pipeline) 
                ].groupby(['Semaine'])['working_hours'].count().reset_index().rename(columns={'working_hours': 'Nb tickets'})


    df_tickets_ssia_sla = pd.merge(df_tickets_ssia, df_sla_2h, how='left', on='Semaine')

    pourcentage_sla = (df_tickets_ssia_sla['SLA < 2h'].mean() / df_tickets_ssia_sla['Nb tickets'].mean()) * 100
    pourcentage_sla = (f"{pourcentage_sla:.2f}%")
    return pourcentage_sla

# Exemple d'utilisation (si nécessaire, veillez à fournir une liste 'semaines' valide)
# semaines_list = df_graph_agent["Semaine"].unique().tolist()
# graph_activite_ticket_source_client_ssia = activite_ticket_source_client(data_affid_hubspot_ticket, 'SSIA', semaines_list)
