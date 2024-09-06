import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta
from datetime import datetime, timedelta
import datetime as dt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


MY_PATH_JIRA = ("jira.xlsx")

@st.cache_data
def read_df_jira():
    df = pd.read_excel(MY_PATH_JIRA)
    df = df[df['Clé de projet'] == 'SPSA']
    df = df[df['Création'] > '2022-01-01']
    return df


def parameters (selection, choix_formulaire):

    options_partenaire = st.selectbox(
    "Choix du partenaire",
    selection,
    placeholder="Select contact method...",
    )

    options_formulaire = st.selectbox(
    "Choix du formulaire",
    choix_formulaire,
    placeholder="Select contact method...",
    )

    values = st.slider(
    'Select a range of values',
    1, 52, (52))

    metric = 52

    #options_formulaire = st.multiselect(
    #'What are your favorite colors',
    #choix_formulaire, 
    #['C2 INCIDENT N2'])

    return options_partenaire, options_formulaire, values, metric


def df_selection(df, df2, df3, values, metric):

    df['Date'] = df['Date'].dt.date
    df2['Date'] = df2['Date'].dt.date
    df3['Date'] = df3['Date'].dt.date
    today = date.today()

    week_prior =  today - timedelta(weeks=values)
    week_prior2 =  today - timedelta(weeks=metric)
    week_prior3 =  ((today - timedelta(weeks=values)) - timedelta(weeks=values))

    df = df[df['Date'] >= week_prior]
    df = df.sort_values(by='Semaine', ascending=True)

    df2 = df2[df2['Date'] >= week_prior2]
    df2 = df2.sort_values(by='Semaine', ascending=True)

    df3 = df3[(df3['Date'] >= week_prior3) & (df3['Date'] <= week_prior)]
    df3 = df3.sort_values(by='Semaine', ascending=True)

    return df, df2, df3



def bar_chart_category_delai(df, df2, options_partenaire, options_formulaire, defaut_val):

    filtered_df = df.copy()
    filtered_df2 = df2.copy()

    if options_partenaire != defaut_val and options_partenaire != "All":
        filtered_df = filtered_df[filtered_df['Partenaires'] == options_partenaire]
        filtered_df2 = filtered_df2[filtered_df2['Partenaires'] == options_partenaire]

    if options_formulaire != defaut_val and options_formulaire != "All":
        filtered_df = filtered_df[filtered_df['Customer Request Type'] == options_formulaire]
        filtered_df2 = filtered_df2[filtered_df2['Customer Request Type'] == options_formulaire]

    df_grouped_category = filtered_df.groupby('main_category').agg({'Clé de ticket':'count'}).reset_index().sort_values('Clé de ticket', ascending=True)
    df_grouped_category_ticket = filtered_df.groupby('Customer Request Type').agg({'Clé de ticket':'count'}).reset_index().sort_values('Clé de ticket', ascending=True)


    df_grouped_ticket = filtered_df.groupby('Semaine').agg({'Clé de ticket':'count'}).reset_index()

    fig_category = px.bar(df_grouped_category, y='main_category', x='Clé de ticket', orientation='h', title='Bar Chart')
    fig_category_ticket = px.bar(df_grouped_category_ticket, y='Customer Request Type', x='Clé de ticket', orientation='h', title='Bar Chart')
    fig_ticket = st.bar_chart(df_grouped_ticket, x="Semaine", y="Clé de ticket")

    
    fig_box_delai = px.box(filtered_df, y="Temps écoulé pour la première réponse (en minutes)")

    metric_nb_ticket = filtered_df['Clé de ticket'].count()


    return fig_category, fig_ticket, fig_category_ticket, metric_nb_ticket


def metrics(df, df3, options_partenaire, options_formulaire, defaut_val):

    df_formulaire = df.copy()
    df_formulaire_before = df3.copy()

    if options_partenaire != defaut_val and options_partenaire != "All":
        df_formulaire = df_formulaire[df_formulaire['Partenaires'] == options_partenaire]
        df_formulaire_before = df_formulaire_before[df_formulaire_before['Partenaires'] == options_partenaire]
 
    if options_formulaire != defaut_val and options_formulaire != "All":
        df_formulaire = df_formulaire[df_formulaire['Customer Request Type'] == options_formulaire]
        df_formulaire_before = df_formulaire_before[df_formulaire_before['Customer Request Type'] == options_formulaire]


    def metric_tendance (tendance) :
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
    

    max_value = 10000
 
    df_formulaire = df_formulaire[(df_formulaire['Temps écoulé pour la première réponse (en minutes)'] < max_value)]
    df_formulaire_before = df_formulaire_before[(df_formulaire_before['Temps écoulé pour la première réponse (en minutes)'] < max_value)]

    # Calcul du nombre de tickets pour le partenaire et le formulaire sélectionnés
    metric_nb_ticket = len(df_formulaire)

    # Calcul du nombre de tickets N2 pour le partenaire et le formulaire sélectionnés
    df_n2 = df_formulaire[df_formulaire['Customer Request Type'] == 'C2 INCIDENT N2']
    metric_nb_ticket_n2 = len(df_n2)

    # Calcul de la tendance du nombre de tickets pour le partenaire et le formulaire sélectionnés
    metric_nb_ticket_before = len(df_formulaire_before)
    if metric_nb_ticket == 0:
        tendance_ticket = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_ticket = metric_nb_ticket_before / metric_nb_ticket
    tendance_ticket = metric_tendance(tendance_ticket) 
    #tendance_ticket = metric_tendance(tendance_ticket)

    # Calcul de la tendance du nombre de tickets N2 pour le partenaire et le formulaire sélectionnés
    df_n2_before = df_formulaire_before[df_formulaire_before['Customer Request Type'] == 'C2 INCIDENT N2']
    metric_nb_ticket_n2_before = len(df_n2_before)
    if metric_nb_ticket_n2 == 0:
        tendance_n2 = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_n2 = metric_nb_ticket_n2_before / metric_nb_ticket_n2
    tendance_n2 = metric_tendance(tendance_n2)
    
    # Calcul du nombre de tickets prestation pour le partenaire et le formulaire sélectionnés
    df_presta = df_formulaire[df_formulaire['Type_ticket'] == 'Prestation']
    metric_nb_ticket_presta = len(df_presta)

    # Calcul de la tendance du nombre de tickets prestation pour le partenaire et le formulaire sélectionnés
    df_presta_before = df_formulaire_before[df_formulaire_before['Type_ticket'] == 'Prestation']
    metric_nb_ticket_presta_before = len(df_presta_before)
    # Calcul de la tendance de la prestation
    if metric_nb_ticket_presta == 0:
        tendance_presta = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_presta = metric_nb_ticket_presta_before / metric_nb_ticket_presta
    tendance_presta = metric_tendance(tendance_presta)
    
    df_formulaire['Délai_prise_en_charge'] = df_formulaire['Temps écoulé pour la première réponse (en minutes)']
    df_formulaire_before['Délai_prise_en_charge'] = df_formulaire_before['Temps écoulé pour la première réponse (en minutes)']

    # Calcul du délai moyen de prise en charge pour le partenaire et le formulaire sélectionnés
    mean_delai = df_formulaire['Délai_prise_en_charge'].mean()

    # Calcul de la tendance du délai moyen de prise en charge pour le partenaire et le formulaire sélectionnés
    mean_delai_before = df_formulaire_before['Délai_prise_en_charge'].mean()

    if mean_delai == 0:
        tendance_delai = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_delai = mean_delai_before / mean_delai
    tendance_delai = metric_tendance(tendance_delai)

    # Calcul du nombre de tickets avec un délai de prise en charge supérieur à 2 heures pour le partenaire et le formulaire sélectionnés
    df_superieur_2h = df_formulaire[df_formulaire['Délai_prise_en_charge'] > 120]
    count_superieur_2h = len(df_superieur_2h)

    # Calcul de la tendance du nombre de tickets avec un délai de prise en charge supérieur à 2 heures pour le partenaire et le formulaire sélectionnés
    df_superieur_2h_before = df_formulaire_before[df_formulaire_before['Délai_prise_en_charge'] > 120]
    count_superieur_2h_before = len(df_superieur_2h_before)
    if count_superieur_2h == 0:
        tendance_superieur_2h = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_superieur_2h = count_superieur_2h_before / count_superieur_2h

    tendance_superieur_2h = metric_tendance(tendance_superieur_2h)

    # Calcul du nombre d'appels directs pour le partenaire et le formulaire sélectionnés
    df_appel_direct = df_formulaire.loc[df_formulaire["Créateur"].isin(["operation-supp", "assistancestellair"])]
    df_appel_direct = df_appel_direct.loc[~df_appel_direct["Partenaires"].isin(["Affid"])]
    nb_appel_direct = len(df_appel_direct)

    # Calcul de la tendance du nombre d'appels directs pour le partenaire et le formulaire sélectionnés
    df_appel_direct_before = df_formulaire_before.loc[df_formulaire_before["Créateur"].isin(["operation-supp", "assistancestellair"])]
    nb_appel_direct_before = len(df_appel_direct_before)
    if nb_appel_direct == 0:
        tendance_appel_direct = 0  # Affiche zéro en cas de division par zéro
    else:
        tendance_appel_direct = nb_appel_direct_before / nb_appel_direct
    tendance_appel_direct = metric_tendance(tendance_appel_direct)

    # Calcul des statistiques pour les délais de prise en charge
    filtered_df_describe = df_formulaire['Délai_prise_en_charge'].describe()

    # Création du graphique en boîte à moustaches pour les délais de prise en charge
    fig_box_delai = go.Figure(data=[go.Box(y=df_formulaire['Délai_prise_en_charge'], name='Délai de prise en charge')])
    fig_box_delai.update_layout(title='Délai de prise en charge', yaxis_title='Temps (heures)')

    return [mean_delai_before,df_formulaire,metric_nb_ticket, metric_nb_ticket_n2, tendance_ticket, tendance_n2, mean_delai,
            tendance_delai, metric_nb_ticket_presta, metric_nb_ticket_presta_before,
            tendance_presta, filtered_df_describe, df_superieur_2h, count_superieur_2h,
            tendance_superieur_2h, nb_appel_direct, tendance_appel_direct, fig_box_delai]
