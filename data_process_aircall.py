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
path_source_affid_aircall = 'data/Affid/Aircall'
files_aircall = [file for file in os.listdir(path_source_affid_aircall) if not file.startswith('.')] # Ignore hidden files

data_affid_aircall = pd.DataFrame()

for file in files_aircall:
    current_data_aircall = pd.read_excel(path_source_affid_aircall +"/"+ file)
    data_affid_aircall = pd.concat([data_affid_aircall, current_data_aircall])

data_affid_aircall = data_affid_aircall.loc[data_affid_aircall["line"].isin(["Standard - √† porter (sortants)", "Standard - Ã  porter (sortants)", "Standard", "Technique", "Commerce", "ADV", "Armatis"])]
data_affid_aircall['HangupTime'] = pd.to_datetime(data_affid_aircall['time (TZ offset incl.)'], format='%H:%M:%S') + pd.to_timedelta(data_affid_aircall['duration (in call)'], unit='s')
data_affid_aircall['datetime (UTC)'] = data_affid_aircall.apply(lambda row: row['datetime (UTC)'].replace(hour=row['time (TZ offset incl.)'].hour, minute=row['time (TZ offset incl.)'].minute, second=row['time (TZ offset incl.)'].second), axis=1)
data_affid_aircall['time (TZ offset incl.)'] = pd.to_datetime(data_affid_aircall['time (TZ offset incl.)'], format='%H:%M:%S')

data_affid_aircall.rename(columns = {"answered":"LastState", 
                                     'datetime (UTC)':"StartTime", 
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
                                         'ToNumber', 'UserName', 'Note', 'Tags', 'ScenarioName']]






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
                                     "no":"no"},)


data_affid["Semaine"] = data_affid['StartTime'].dt.strftime("S%Y-%V")

data_affid["Heure"] = pd.to_datetime(data_affid['StartTime']).dt.hour
data_affid["Date"] = data_affid["StartTime"].dt.date
data_affid["Jour"] = data_affid["StartTime"].dt.day_name()

data_affid = data_affid.loc[~data_affid["Jour"].isin(["Saturday", "Sunday"])]
data_affid = data_affid.loc[~data_affid["ScenarioName"].isin(["Ferm√©",
                                                              "out_of_opening_hours",
                                                              "abandoned_in_ivr"])]

from datetime import date

#data_affid['tags'] = data_affid['Tags'].str.replace('[^a-zA-Z-,]', '')
data_affid['Tags'] = data_affid['Tags'].apply(lambda x: str(x).replace('[^a-zA-Z-,]', ''))
data_affid['Note'] = data_affid['Note'].apply(lambda x: str(x).lower())

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
                         'ToNumber', 'UserName', 'Note', 'Tags']]


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
          'Frederic SAUVAN']

frederic = ['Frederic SAUVAN']

agents_support = ['Olivier Sainte-Rose', 
                  'Mourad HUMBLOT', 
                  'Pierre GOUPILLON', 
                  'Archimede KESSI', 
                  'Frederic SAUVAN']

agents_armatis = ['Armatis Agent 1', 
                  'Armatis Agent 2', 
                  'Armatis Agent 3']


line_support = 'Technique'
line_armatis = 'Armatis'

def def_df_support (df_entrant, df_sortant, line, liste_agents) :
    
    df_entrant = df_entrant[(df_entrant['line'] == line)
                          & (df_entrant['direction'] == 'inbound')]
    
    df_sortant = df_sortant[df_sortant['UserName'].isin(liste_agents)]
    df_sortant = df_sortant[(df_sortant['direction'] == 'outbound')]
    
    
    def number(row):
        if row['FromNumber'] == (33187662300 or 33189730123 or 
                                 33189730124 or 33189730125 or 33189730128):
            return row['ToNumber']
        else:
            return row['FromNumber']
        
    df_entrant['Number'] = df_entrant['FromNumber']
    df_sortant['Number'] = df_sortant['ToNumber']
    
    df = pd.concat([df_entrant, df_sortant])
    
    #df['Number'] = df.apply(number, axis=1)
    df = df.loc[~df["Jour"].isin(["Saturday", "Sunday"])]
    df = df.loc[~df["UserName"].isin(["Vincent Gourvat", 
                                      "Thierry CAROFF", 
                                      'Armatis Agent 1',])]
    
    for x in liste_agents:
        df[x] = df["UserName"].map({x:1,"NaN":0}) 
    
    if liste_agents == agents_support : 
        for x in frederic:
            df[x] = df["UserName"].map({x:0,"NaN":0})
    
    df_effectif = pd.DataFrame()
    
    if liste_agents == agents_support:
        liste_agents.append('Frederic SAUVAN')
        for x in liste_agents:
            current_support_effectif = df.groupby('Date').agg({x:'mean'})
            df_effectif = pd.concat([current_support_effectif, df_effectif])
            df_effectif = df_effectif.groupby('Date').mean().sort_values(['Date'])
            df_effectif.fillna(0, inplace=True)
    
        df_effectif = df_effectif.reset_index()
    
    if liste_agents == agents_armatis:
        for x in liste_agents:
            current_support_effectif = df.groupby('Date').agg({x:'mean'})
            df_effectif = pd.concat([current_support_effectif, df_effectif])
            df_effectif = df_effectif.groupby('Date').mean().sort_values(['Date'])
            df_effectif.fillna(0, inplace=True)
    
        df_effectif = df_effectif.reset_index()
    
    if liste_agents == agents_support : 
        df_effectif['Effectif'] = (df_effectif['Archimede KESSI']
                                    + df_effectif['Olivier Sainte-Rose']
                                    + df_effectif['Mourad HUMBLOT']
                                    + df_effectif['Pierre GOUPILLON'] 
                                    + df_effectif['Frederic SAUVAN'])
        df_effectif = df_effectif[['Date', 'Effectif']]
        
    if liste_agents == agents_armatis : 
        df_effectif['Effectif'] = (df_effectif['Armatis Agent 1']
                                    + df_effectif['Armatis Agent 2']
                                    + df_effectif['Armatis Agent 3'])
    
        df_effectif = df_effectif[['Date', 'Effectif']]
    
    df = pd.merge(df, df_effectif, how = "left")
    df['Count'] = 1
    df['Entrant_connect'] = df.apply(lambda x : 1 if x['LastState'] == 'yes' 
                                     and x['direction'] == 'inbound' else 0, axis=1)
    df['Entrant'] = df.apply(lambda x : 1 if x['direction'] == 'inbound' else 0, axis=1)
    df['Sortant_connect'] = df.apply(lambda x : 1 if x['direction'] == 'outbound' and x['InCallDuration'] > 60 else 0, axis=1)
    df['Taux_de_service'] = (df['Entrant_connect'] 
                                    / df['Entrant'])
    
    df["Mois"] = df['StartTime'].dt.strftime("%Y-%m")

    def afd_ste(row):
        if 'STE' in row['Tags']:
            return 'STE'
        else:
            return 'AFD'

    df["Logiciel"] = df.apply(afd_ste, axis=1)
    
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

    