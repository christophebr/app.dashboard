import pandas as pd
#pd.options.plotting.backend = 'hvplot'
import numpy as np
import datetime as dt
from isoweek import Week
from time import gmtime
import os
#import matplotlib.pyplot as plt
from functools import reduce
import re
import warnings
warnings.filterwarnings('ignore')
#from pivottablejs import pivot_ui
from IPython.display import HTML
from datetime import date, timedelta 
#import nltkx
from datetime import datetime
from datetime import datetime, time
#import pygwalker as pyg


#path = %pwd
path_source_affid_aircall_v1 = 'data/Affid/Aircall/data_v1'
path_source_affid_aircall_v2 = 'data/Affid/Aircall/data_v2'
files_aircall_v1 = [file for file in os.listdir(path_source_affid_aircall_v1) if not file.startswith('.')] # Ignore hidden files
files_aircall_v2 = [file for file in os.listdir(path_source_affid_aircall_v2) if not file.startswith('.')] # Ignore hidden files    
    
data_affid_aircall_v1 = pd.DataFrame()
data_affid_aircall_v2 = pd.DataFrame()

for file in files_aircall_v1:
    current_data_aircall_v1 = pd.read_excel(path_source_affid_aircall_v1 +"/"+ file)
    data_affid_aircall_v1 = pd.concat([data_affid_aircall_v1, current_data_aircall_v1])

for file in files_aircall_v2:
    current_data_aircall_v2 = pd.read_excel(path_source_affid_aircall_v2 +"/"+ file)
    data_affid_aircall_v2 = pd.concat([data_affid_aircall_v2, current_data_aircall_v2])


#data_affid_aircall_v1['datetime (UTC)'] = pd.to_datetime(data_affid_aircall_v1['datetime (UTC)'], errors='coerce', dayfirst=False)
#data_affid_aircall_v1['datetime (UTC)'] = data_affid_aircall_v1['datetime (UTC)'].dt.strftime('%d/%m/%Y %H:%M')
#data_affid_aircall_v1['datetime (UTC)'] = pd.to_datetime(data_affid_aircall_v1['datetime (UTC)'], format='%d/%m/%Y %H:%M')

#data_affid_aircall_v2['datetime (UTC)'] = pd.to_datetime(data_affid_aircall_v2['datetime (UTC)'], errors='coerce', dayfirst=False)
#data_affid_aircall_v2['datetime (UTC)'] = data_affid_aircall_v2['datetime (UTC)'].dt.strftime('%d/%m/%Y %H:%M')
#data_affid_aircall_v2['datetime (UTC)'] = pd.to_datetime(data_affid_aircall_v2['datetime (UTC)'], format='%d/%m/%Y %H:%M')

data_affid_aircall_v1['IVR Branch'] = ""


data_affid_aircall_v1 = data_affid_aircall_v1[['line', 'date (TZ offset incl.)', 'time (TZ offset incl.)', 'number timezone', 'datetime (UTC)', 'country_code', 'direction', 'from',
                                               'to', 'answered','missed_call_reason', 'user', 'duration (total)','duration (in call)', 'via', 'voicemail', 'tags', 'IVR Branch']]


columns_to_select  = data_affid_aircall_v1.columns.tolist()

data_affid_aircall_v2 = data_affid_aircall_v2[columns_to_select]




data_affid_aircall = pd.concat([data_affid_aircall_v1, data_affid_aircall_v2])


data_affid_aircall = data_affid_aircall.loc[data_affid_aircall["line"].isin(["Standard - √† porter (sortants)", "Standard - Ã  porter (sortants)", "Standard", "Technique", "Commerce", "ADV", "Armatis", "Armatis Technique"])]
data_affid_aircall['HangupTime'] = pd.to_datetime(data_affid_aircall['time (TZ offset incl.)'], format='%H:%M:%S') + pd.to_timedelta(data_affid_aircall['duration (in call)'], unit='s')
#data_affid_aircall['datetime (UTC)'] = data_affid_aircall.apply(lambda row: row['datetime (UTC)'].replace(hour=row['time (TZ offset incl.)'].hour, minute=row['time (TZ offset incl.)'].minute, second=row['time (TZ offset incl.)'].second), axis=1)
data_affid_aircall['time (TZ offset incl.)'] = pd.to_datetime(data_affid_aircall['time (TZ offset incl.)'], format='%H:%M:%S')

data_affid_aircall.rename(columns = {"answered":"LastState", 
                                     'date (TZ offset incl.)':"StartTime", 
                                     "duration (total)":"TotalDuration", 
                                     "duration (in call)":"InCallDuration", 
                                     "from":"FromNumber", 
                                     "to":"ToNumber", 
                                     "user":"UserName", 
                                     "comments":"Note", 
                                     "tags":"Tags", 
                                     "missed_call_reason":"ScenarioName",}, inplace = True)

data_affid_aircall = data_affid_aircall[['line', 'direction', 
                                         'LastState', 'StartTime','HangupTime', 'time (TZ offset incl.)',
                                         'TotalDuration', 'InCallDuration', 'FromNumber',
                                         'ToNumber', 'UserName', 'Tags', 'IVR Branch', 'ScenarioName']]



data_affid = data_affid_aircall

data_affid["LastState"] = data_affid["LastState"].map({
                                     "ANSWERED":"yes", 
                                     "VOICEMAIL":"no",
                                     "MISSED":"no", 
                                     "VOICEMAIL_ANSWERED":"no",
                                     "BLIND_TRANSFERED":"no", 
                                     "NOANSWER_TRANSFERED":"no",
                                     "FAILED":"no", 
                                     "CANCELLED":"no",
                                     "QUEUE_TIMEOUT":"no", 
                                     "yes":"yes",
                                     "no":"no",
                                     "Yes":"yes",
                                     "No":"no"},)


data_affid["Semaine"] = data_affid['StartTime'].dt.strftime("S%Y-%V")

data_affid["Heure"] = pd.to_datetime(data_affid['time (TZ offset incl.)']).dt.hour
data_affid["Date"] = data_affid["StartTime"].dt.date
data_affid["Jour"] = data_affid["StartTime"].dt.day_name()

data_affid = data_affid.loc[~data_affid["Jour"].isin(["Saturday", "Sunday"])]
data_affid = data_affid.loc[~data_affid["ScenarioName"].isin(["Ferm√©",
                                                              "out_of_opening_hours",
                                                              "abandoned_in_ivr", 
                                                              'short_abandoned'])]

from datetime import date

#data_affid['tags'] = data_affid['Tags'].str.replace('[^a-zA-Z-,]', '')
data_affid['Tags'] = data_affid['Tags'].apply(lambda x: str(x).replace('[^a-zA-Z-,]', ''))
#data_affid['Note'] = data_affid['Note'].apply(lambda x: str(x).lower())

nrp = ['NRP']
data_affid['NRP'] = 'no'


data_affid['LastState'] = np.where(
    (data_affid['Tags'].isin(['NRP'])) & (data_affid['direction'] == 'outbound'),
    data_affid['NRP'],
    data_affid['LastState']
)

data_affid = data_affid[['line','Semaine', 'Date', 'Jour','Heure', 'direction',
                         'LastState', 'ScenarioName', 'StartTime','HangupTime', 'time (TZ offset incl.)', 
                         'TotalDuration', 'InCallDuration', 'FromNumber',
                         'ToNumber', 'UserName', 'Tags','IVR Branch']]


today = date.today()
week_prior =  today - timedelta(weeks=52)
data_affid = data_affid[data_affid['Date'] >= week_prior]
data_affid = data_affid.sort_values(by='Semaine', ascending=True)



data_affid['UserName'] = data_affid['UserName'].str.replace("Archim√®de KESSI", 
                                                            'Archimede KESSI')
data_affid['UserName'] = data_affid['UserName'].str.replace("Olivier SAINTE-ROSE", 
                                                            'Olivier Sainte-Rose')

agents = ['Olivier Sainte-Rose', 
          'Mourad HUMBLOT', 
          'Pierre GOUPILLON',
          'Frederic SAUVAN', 
          'Christophe Brichet']

frederic = ['Frederic SAUVAN']

agents_support = ['Olivier Sainte-Rose', 
                  'Mourad HUMBLOT', 
                  'Pierre GOUPILLON', 
                  'Archimede KESSI', 
                  'Frederic SAUVAN', 
                  'Christophe Brichet']

agents_armatis = ['Melinda Marmin', 
                  'Sandrine Sauvage', 
                  'Emilie GEST', 
                  'Morgane Vandenbussche']

agents_all = [ 'Melinda Marmin',
                  'Sandrine Sauvage', 
                  'Emilie GEST', 
                  'Morgane Vandenbussche',
                  'Olivier Sainte-Rose', 
                  'Mourad HUMBLOT', 
                  'Pierre GOUPILLON', 
                  'Archimede KESSI', 
                  'Frederic SAUVAN', 
                  'Christophe Brichet']


line_support = 'technique'
line_armatis = 'armatistechnique'
line_tous = 'tous'

def def_df_support(df_entrant, df_sortant, line, liste_agents):

    def clean_string(s):
        return ''.join(s.split()).lower()

    df_entrant['line'] = df_entrant['line'].apply(clean_string)

    if line == "tous":
        df_entrant = df_entrant[(df_entrant['line'].isin(['technique', 'armatistechnique'])) 
                                & (df_entrant['direction'] == 'inbound')]
    elif line in ['technique', 'armatistechnique']:
        df_entrant = df_entrant[(df_entrant['line'] == line) & (df_entrant['direction'] == 'inbound')]

    df_sortant = df_sortant[(df_sortant['UserName'].isin(liste_agents)) & (df_sortant['direction'] == 'outbound')]

    df_entrant['Number'] = df_entrant['FromNumber']
    df_sortant['Number'] = df_sortant['ToNumber']

    df = pd.concat([df_entrant, df_sortant])

    df = df.loc[~df["Jour"].isin(["Saturday", "Sunday"])]
    df = df.loc[~df["UserName"].isin(["Vincent Gourvat", "Thierry CAROFF", 'Armatis Agent 1'])]

    df['Count'] = 1
    df['Entrant_connect'] = df.apply(lambda x: 1 if x['LastState'] == 'yes' and x['direction'] == 'inbound' else 0, axis=1)
    df['Entrant'] = df.apply(lambda x: 1 if x['direction'] == 'inbound' else 0, axis=1)
    df['Sortant_connect'] = df.apply(lambda x: 1 if x['direction'] == 'outbound' and x['InCallDuration'] > 60 else 0, axis=1)
    df['Taux_de_service'] = df['Entrant_connect'] / df['Entrant']
    
    df["Mois"] = df['StartTime'].dt.strftime("%Y-%m")

    # Ajouter la logique de filtrage des agents ayant pris au moins 2 appels
    df_grouped = df.groupby(['Date', 'UserName']).size().reset_index(name='TotalAppels')
    
    # Marquer les agents ayant pris au moins 2 appels
    df_grouped['Actif'] = df_grouped['TotalAppels'].apply(lambda x: 1 if x >= 2 else 0)

    # Calculer l'effectif moyen par jour
    df_effectif = df_grouped.groupby('Date')['Actif'].sum().reset_index()
    df_effectif.rename(columns={'Actif': 'Effectif'}, inplace=True)

    # Fusionner l'effectif avec le DataFrame principal
    df = pd.merge(df, df_effectif, on='Date', how='left')

    # Fonction de conversion de tags IVR

    def get_ivr_or_tags_transformed(row):
        """
        Retourne la valeur de 'IVR Branch' si elle est renseignée,
        sinon 'Stellair' si 'line' est égale à 'armatistechnique',
        sinon transforme les 3 premiers caractères de 'Tags' :
        - 'STE' -> 'Stellair'
        - 'AFD' -> 'Affid'

        Args:
            row (pd.Series): Une ligne du DataFrame.

        Returns:
            str: La valeur de 'IVR Branch', 'Stellair', ou la transformation de 'Tags'.
        """
        if pd.notna(row['IVR Branch']) and row['IVR Branch'].strip():
            return row['IVR Branch']
        elif row['line'] == 'armatistechnique':
            return 'Stellair'
        else:
            tags_prefix = row['Tags'][:3].upper() if pd.notna(row['Tags']) else ''
            if tags_prefix == 'STE':
                return 'Stellair'
            elif tags_prefix == 'AFD':
                return 'Affid'
            else:
                return 'Inconnu'  # Retourne 'Inconnu' si aucun préfixe ne correspond

    # Exemple d'utilisation sur un DataFrame
    df['Logiciel'] = df.apply(get_ivr_or_tags_transformed, axis=1)


    #df["Logiciel"] = df.apply(afd_ste, axis=1)

    return df


    


df_support = def_df_support(data_affid, data_affid, line_support, agents_support)

#df_support.to_excel('Data_process_prod.xlsx')

def charge_agents (agent) : 
    df_charge_agent = df_support[(df_support['UserName'] == agent )]
    df_charge_agent = df_charge_agent.groupby(['Date']).agg({'InCallDuration':'sum'})
    df_charge_agent['InCallDuration'] = df_charge_agent['InCallDuration'] / 60 
    df_charge_agent[agent] = df_charge_agent['InCallDuration'] / 180
    df_charge_agent = df_charge_agent.groupby(['Date']).agg({agent:'mean',}).reset_index()
    df_charge_agent = df_charge_agent[['Date', agent]]
    
    return df_charge_agent

#from functools import reduce

df_charge_pierre = charge_agents('Pierre GOUPILLON')
df_charge_olivier = charge_agents('Olivier Sainte-Rose')
df_charge_mourad = charge_agents('Mourad HUMBLOT')
df_charge_archimede = charge_agents('Archimede KESSI')
df_charge_frederic = charge_agents('Frederic SAUVAN')
df_charge_frederic = charge_agents('Christophe BRICHET')



    
