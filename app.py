import streamlit as st
import streamlit as st
from Data_support import graph_activite , graph_taux_jour , graph_taux_heure, graph_charge_affid_stellair
from support import metrics_support
import plotly.graph_objects as go
from functools import reduce
import pickle
from pathlib import Path
import bcrypt
import streamlit_authenticator as stauth 
import config


# Configuration de la page
st.set_page_config(
    page_title=":bar_chart: Dashboard support",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Charger les mots de passe hachés à partir du fichier
file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('rb') as file:
    hashed_passwords = pickle.load(file)


#file_path = Path(__file__).parent / 'hashed_pw.pkl'
#with file_path.open('rb') as file: 
#    hashed_passwords = pickle.load(file)

# Mettre à jour le dictionnaire des credentials avec les mots de passe hachés
config.credentials['usernames']['cbri']['password'] = hashed_passwords['cbri']
config.credentials['usernames']['mpec']['password'] = hashed_passwords['mpec']
config.credentials['usernames']['elap']['password'] = hashed_passwords['elap']
config.credentials['usernames']['pgou']['password'] = hashed_passwords['pgou']
config.credentials['usernames']['osai']['password'] = hashed_passwords['osai']
config.credentials['usernames']['fsau']['password'] = hashed_passwords['fsau']
config.credentials['usernames']['mhum']['password'] = hashed_passwords['mhum']
config.credentials['usernames']['akes']['password'] = hashed_passwords['akes']
config.credentials['usernames']['dlau']['password'] = hashed_passwords['dlau']
config.credentials['usernames']['jdel']['password'] = hashed_passwords['jdel']

# Initialiser l'authentificateur avec le dictionnaire des credentials
authenticator = stauth.Authenticate(config.credentials, 'dashboard_support', 'support', cookie_expiry_days=2)

name, authentification_status, username = authenticator.login()

if authentification_status == False : 
     st.error('username/password is incorrect')

if authentification_status == None : 
    st.warning('Please enter your username and password')

if authentification_status :

    st.sidebar.title(f"Welcome, {name}")
    authenticator.logout('Logout', 'sidebar')

    #st.set_page_config(
    #page_title= " :bar_chart: Dashboard support partenaires",
    #layout= "wide",
    #initial_sidebar_state="collapsed",
    #) 

    PAGES = {
    "Support": "support",
    "Agents": "agents",
    "Tickets": "tickets"
    }

    if __name__ == "__main__": 

        selection_page = st.sidebar.selectbox("Choix de la page", list(PAGES.keys()), key="unique_page_selection")

        if selection_page == "Support":

            from support import read_df_aircall
            import pandas as pd
            from support import read_df_jira_support
            from support import parameters_support
            from support import df_selection_support
            from support import metrics_support
            from support import tickets_support , convert_to_sixtieth
            from Data_support import graph_activite , graph_taux_jour , graph_taux_heure, graph_tag
            from Data_support import graph_charge_affid_stellair, calcul_taux_reponse, calcul_productivite_appels
            import plotly.graph_objects as go
            from data_process_aircall import def_df_support
            from data_process_aircall import data_affid, line_support, agents_support, line_armatis, agents_armatis, line_tous, agents_all
            from hubspot import df_affid_hubspot_ticket

                

            def support():
                st.title("📊 Dashboard Support")

                # Sélection du dataframe
                dataframe_option = st.sidebar.selectbox(
                    "Choisir le dataframe",
                    ["support_suresnes", "support_armatis", "support_stellair", "support_affid"]
                )

                df_stellair = def_df_support(data_affid, data_affid, line_tous, agents_all)
                df_stellair = df_stellair[(df_stellair['line'] == 'armatistechnique') 
                                          | (df_stellair['IVR Branch'] == 'Stellair')]

                df_affid = def_df_support(data_affid, data_affid, line_tous, agents_support)
                df_affid = df_affid[df_affid['IVR Branch'] == 'Affid']


                # Association des dataframes aux paramètres correspondants
                dataframe_config = {
                    "support_suresnes": {
                        "df": def_df_support(data_affid, data_affid, line_support, agents_support),
                        "agents": agents_support
                    },
                    "support_armatis": {
                        "df": def_df_support(data_affid, data_affid, line_armatis, agents_armatis),
                        "agents": agents_armatis
                    },
                    "support_stellair": {
                        "df": df_stellair,
                        "agents": agents_all
                    },
                    "support_affid": {
                        "df": df_affid,
                        "agents": agents_support
                    }
                }

                # Chargement du dataframe sélectionné
                df_support = dataframe_config[dataframe_option]["df"]
                agents = dataframe_config[dataframe_option]["agents"]

                # Filtrage des données en fonction des dates sélectionnées
                start_date, end_date = parameters_support()
                df_support_filtered, _ = df_selection_support(df_support, start_date, end_date)

                # Calcul des métriques
                taux_reponse, mean_difference, df_taux_reponse = calcul_taux_reponse(df_support_filtered)
                [Taux_de_service, tendance_taux, Entrant, tendance_entrant, Numero_unique, tendance_unique, 
                temps_moy_appel, tendance_appel, Nombre_appel_jour_agent] = metrics_support(df_support_filtered, df_support)

                fig_tags_cat_afd, temps_moy_appel_afd = graph_tag('AFD', df_support_filtered)
                fig_tags_cat_ste, temps_moy_appel_ste = graph_tag('STE', df_support_filtered)

                # Affichage des métriques principales
                col1, col2, col3 = st.columns(3)
                col1.metric("Taux de service en %", Taux_de_service)
                col2.metric("Appels entrant / Jour", Entrant)
                col3.metric("Numéros uniques / Jour", Numero_unique)

                col4, col5, col6 = st.columns(3)
                col4.metric("Temps Moy / Appel", convert_to_sixtieth(temps_moy_appel), tendance_appel)
                col5.metric("Nombre d'appels / Agent / Jour", Nombre_appel_jour_agent)
                col6.metric("Taux de réponse (%)", round(taux_reponse * 100))

                # Affichage des graphiques d'activité
                st.plotly_chart(graph_activite(df_support_filtered), use_container_width=True)

                # Affichage des graphiques de taux
                col_graph1, col_graph2 = st.columns(2)
                col_graph1.plotly_chart(graph_taux_jour(df_support_filtered), use_container_width=True)
                col_graph2.plotly_chart(graph_taux_heure(df_support_filtered), use_container_width=True)

                # Graphiques spécifiques au dataframe
                if dataframe_option == "support_suresnes":
                    fig_charge_affid_stellair_pour, fig_charge_affid_stellair_nb = graph_charge_affid_stellair(df_support_filtered)
                    col_graph3, col_graph4 = st.columns(2)
                    col_graph3.plotly_chart(fig_charge_affid_stellair_pour, use_container_width=True)
                    col_graph4.plotly_chart(fig_charge_affid_stellair_nb, use_container_width=True)

                # Graphiques des catégories AFD et STE
                #col_cat_afd, col_cat_ste = st.columns(2)
                #col_cat_afd.plotly_chart(fig_tags_cat_afd, use_container_width=True)
                #col_cat_ste.plotly_chart(fig_tags_cat_ste, use_container_width=True)

            support()


        elif selection_page == "Agents":
            from support import read_df_aircall
            from support import parameters_support
            from support import df_selection_support, convert_to_sixtieth
            from Data_support import calcul_productivite_appels
            from support import read_df_jira_support
            from Data_support import charge_agents
            from Data_support import graph_charge_agent, charge_entrant_sortant
            from data_process_aircall import def_df_support
            from data_process_aircall import data_affid, line_support, agents_support, line_armatis, agents_armatis, line_tous, agents_all
            import pandas as pd



            def agents():
                st.title(":bar_chart: Dashboard Support")

                # Sélection de la page
                dataframe_option = st.sidebar.selectbox(
                    "Choisir la page",
                    ["support_suresnes", "support_armatis", "support_stellair", "support_affid"],
                    index=0
                )

                # Définir la liste d'agents en fonction de la page sélectionnée
                if dataframe_option == "support_suresnes":
                    liste_agents = ['Pierre GOUPILLON', 'Mourad HUMBLOT', 'Olivier Sainte-Rose', 'Frederic SAUVAN', 'Archimede KESSI']
                elif dataframe_option == "support_armatis":
                    liste_agents = ['Emilie GEST', 'Sandrine Sauvage', 'Morgane Vandenbussche', 'Melinda Marmin']
                elif dataframe_option == "support_stellair":
                    liste_agents = ['Emilie GEST', 'Sandrine Sauvage', 'Morgane Vandenbussche', 'Melinda Marmin',
                                    'Pierre GOUPILLON', 'Mourad HUMBLOT', 'Olivier Sainte-Rose', 'Frederic SAUVAN', 'Archimede KESSI']
                elif dataframe_option == "support_affid":
                    liste_agents = ['Pierre GOUPILLON', 'Mourad HUMBLOT', 'Olivier Sainte-Rose', 'Frederic SAUVAN', 'Archimede KESSI']

                # Charger le dataframe avec les bons agents
                df_support = def_df_support(data_affid, data_affid, line_tous, liste_agents)
                start_date, end_date = parameters_support()
                df_support, df2 = df_selection_support(df_support, start_date, end_date)

                # Calculer la charge des agents
                liste_data = [charge_agents(agent, df_support) for agent in liste_agents]
                df_charge = reduce(lambda left, right: pd.merge(left, right, on=['Date'], how='outer'), liste_data).reset_index()
                df_charge = df_charge.sort_values(['Date'], ascending=True)

                df_charge_effectif = df_support.groupby(['Date']).agg({'Effectif': 'mean'}).reset_index()
                df_charge = pd.merge(df_charge, df_charge_effectif, on='Date', how="left")
                
            
                com_jour_mourad, temps_moy_com_mourad, nb_appels_jour_mourad = calcul_productivite_appels(df_support, "Mourad HUMBLOT")
                com_jour_olivier, temps_moy_com_olivier, nb_appels_jour_olivier = calcul_productivite_appels(df_support, "Olivier Sainte-Rose")
                com_jour_archimede, temps_moy_com_archimede, nb_appels_jour_archimede = calcul_productivite_appels(df_support, "Archimede KESSI")

                nb_appels_jour_moyen = (nb_appels_jour_mourad + nb_appels_jour_olivier + nb_appels_jour_archimede) / 3
                nb_appels_jour_objectif = 30
                
                #nb_appels_jour_entrants = df_support[(df_support['direction'] == 'inbound') & (df_support['UserName'] == agent)]['Entrant_connect'].sum()
                #nb_appels_jour_sortants = df_support[(df_support['direction'] == 'outbound') & (df_support['UserName'] == agent)]['Sortant_connect'].sum()


                # Afficher les métriques et graphiques pour chaque agent
                for agent in liste_agents:
                    com_jour, temps_moy_com, nb_appels_jour= calcul_productivite_appels(df_support, agent)
                    nb_appels_jour_entrants = df_support[
                        (df_support['direction'] == 'inbound') & (df_support['UserName'] == agent) & (df_support['LastState'] == 'yes')
                         ].groupby('Date').agg({'Date':'count'}).mean().values[0]
                    nb_appels_jour_sortants = df_support[
                        (df_support['direction'] == 'outbound') & (df_support['UserName'] == agent)& (df_support['LastState'] == 'yes')
                         ].groupby('Date').agg({'Date':'count'}).mean().values[0]
                    ratio_entrants = nb_appels_jour_entrants / (nb_appels_jour_entrants +  nb_appels_jour_sortants)
                    ratio_sortants = nb_appels_jour_sortants / (nb_appels_jour_entrants +  nb_appels_jour_sortants)

                    if nb_appels_jour_moyen < nb_appels_jour_objectif:
                        nb_appels_diff = (nb_appels_jour_moyen - nb_appels_jour) / nb_appels_jour_moyen
                        if nb_appels_jour < nb_appels_jour_objectif:
                            nb_appels_diff = (nb_appels_jour - nb_appels_jour_objectif)
                        else:
                            nb_appels_diff = (nb_appels_jour - nb_appels_jour_objectif)

                    #nb_appels_diff = (nb_appels_jour - nb_appels_jour_moyen) / nb_appels_jour_moyen
                    col1, col2, col3, col4 = st.columns(4) 
                    col1.metric(f'{agent} - Com Moy / Jour', com_jour)
                    col2.metric(f'{agent} - Temps Moy / Appel', convert_to_sixtieth(temps_moy_com))
                    col3.metric(f'{agent} - Nb Appels / Jour', round(nb_appels_jour, 2))

                    col4.metric(
                        f"{agent} - Répartition Entrants / Sortants",
                        f"{int(ratio_entrants * 100)}% / {int(ratio_sortants * 100)}%"
                    )
                    st.plotly_chart(charge_entrant_sortant(df_support, agent), use_container_width=True)
                
               # for agent in liste_agents:
               #     st.plotly_chart(charge_entrant_sortant(df_support, agent), use_container_width=True)

                # Afficher le graphique global de la charge des agents
                st.plotly_chart(graph_charge_agent(df_charge, liste_agents), use_container_width=True)

            # Appeler la fonction agents()
            agents()


        elif selection_page == "Tickets":
                    from hubspot import df_affid_hubspot_ticket, data_affid_hubspot_agent
                    from hubspot import activite_ticket_source_client, mails_envoyes_agent, sla_2h
                    import pandas as pd

                    #df_affid_hubspot_ticket = None  # Définir la variable avant la condition

                    def tickets():
                        st.title(":bar_chart: Dashboard Support")

                        # Sélection de la page
                        #dataframe_option = st.sidebar.selectbox(
                        #    "Choisir la page",
                        #    ["support_suresnes", "support_armatis", "support_stellair", "support_affid"],
                        #    index=0
                        #)

                                        # Affichage des métriques principales
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Taux de réponse <2h - SSIA", sla_2h(df_affid_hubspot_ticket, 'SSIA'))

                        st.plotly_chart(activite_ticket_source_client(df_affid_hubspot_ticket ))
                        
                        st.plotly_chart(mails_envoyes_agent(data_affid_hubspot_agent))


                    # Appeler la fonction agents()
                    tickets()
        #selection_page = st.sidebar.selectbox("Choix de la page", list(PAGES.keys()), key="page_selection")


        #if selection_page == "Partenaires":
        #    partenaires()
        #elif selection_page == "Support":
        #    support()


    

    #df_metrics = metrics (df2)
    #st.dataframe(df_metrics)

    #st.line_chart(metrics(df))

    
    


    #st.table(df.style.format({
    #'Delai_de_reponse': '{:.2f}h:{:.2f}m:{:.2f}s'.format
    #}))

    #st.plotly_chart(bar_chart_category_delai(df, options_partenaire, options_formulaire, defaut_val))
    #layout()

    




# Affichage du graphique
#chart.show()
