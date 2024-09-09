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


file_path = Path(__file__).parent / 'hashed_pw.pkl'
with file_path.open('rb') as file: 
    hashed_passwords = pickle.load(file)

# Mettre à jour le dictionnaire des credentials avec les mots de passe hachés
config.credentials['usernames']['cbri']['password'] = hashed_passwords['cbri']
config.credentials['usernames']['mpec']['password'] = hashed_passwords['mpec']

# Initialiser l'authentificateur avec le dictionnaire des credentials
authenticator = stauth.Authenticate(config.credentials, 'dashboard_support', 'support', cookie_expiry_days=0)

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
    "Agents": "agents"
    }

    if __name__ == "__main__": 

        selection_page = st.sidebar.selectbox("Choix de la page", list(PAGES.keys()), key="unique_page_selection")

        if selection_page == "Support":

            from support import read_df_aircall
            from support import read_df_jira_support
            from support import parameters_support
            from support import df_selection_support
            from support import metrics_support
            from support import tickets_support
            from Data_support import graph_activite , graph_taux_jour , graph_taux_heure
            from Data_support import graph_charge_affid_stellair, calcul_taux_reponse, calcul_productivite_appels
            import plotly.graph_objects as go
            from data_process_aircall import def_df_support
            from data_process_aircall import data_affid, line_support, agents_support

            def support():
                st.title(" :bar_chart: Dashboard support affid")
                #st.write("Contenu de la page Autre Page")

                # Sélection du dataframe
                dataframe_option = st.sidebar.selectbox(
                    "Choisir le dataframe",
                    ["df_support", "df_support_armatis"]
                )

                if dataframe_option == "df_support":
                    df_support = def_df_support(data_affid, data_affid, line_support, agents_support)
                    df2 = def_df_support(data_affid, data_affid, line_support, agents_support)
                else:
                    df_support = def_df_support(data_affid, data_affid, line_armatis, agents_armatis)
                    df2_armatis = def_df_support(data_affid, data_affid, line_armatis, agents_armatis)

                #df_support = read_df_aircall()
                #df_support = def_df_support(data_affid, data_affid, line_support, agents_support)
                #df2 = def_df_support(data_affid, data_affid, line_support, agents_support)
                #df2 = read_df_aircall()

                #df_tickets = read_df_jira_support()
                #df3 = read_df_jira_support()


                defaut_val = 'All'

                start_date, end_date  = parameters_support()
                df_support, df2 = df_selection_support(df_support,start_date, end_date)
                
                taux_reponse, mean_difference, df_taux_reponse =  calcul_taux_reponse (df_support)

                [Taux_de_service , tendance_taux, Entrant, tendance_entrant, Numero_unique, 
                tendance_unique, temps_moy_appel, tendance_appel, Nombre_appel_jour_agent] = metrics_support(df_support, df2)

                #df_grouped_ticket = tickets_support(df_tickets, option_pipeline, defaut_val)

                col1, col2, col3= st.columns(3)
                col1.metric("Taux de service en %", Taux_de_service, tendance_taux)
                col2.metric("Appels entrant / Jour",Entrant, tendance_entrant)
                col3.metric("Numéros unique", Numero_unique, tendance_unique)
                col_1, col_2, col_3 = st.columns(3)
                col_1.metric("Temps Moy / Appel", round((temps_moy_appel / 60),2), tendance_appel)
                col_2.metric("Nombre appels jour / agent", Nombre_appel_jour_agent)
                col_3.metric('Taux clients répondus', round(taux_reponse * 100))  

                st.plotly_chart(graph_activite(df_support), use_container_width=True)
                #st.plotly_chart(tickets_support(df_tickets), use_container_width=True)

                col_graph1, col_graph2 = st.columns(2)
                col_graph1.plotly_chart(graph_taux_jour(df_support))
                col_graph2.plotly_chart(graph_taux_heure(df_support))

                col_graph11, col_graph22 = st.columns(2)
                col_graph11.plotly_chart(graph_charge_affid_stellair(df_support))


            support()

        elif selection_page == "Agents":
            from support import read_df_aircall
            from support import parameters_support
            from support import df_selection_support
            from Data_support import calcul_productivite_appels
            from support import read_df_jira_support
            from Data_support import charge_agents
            from Data_support import graph_charge_agent
            from data_process_aircall import def_df_support
            from data_process_aircall import data_affid, line_support, agents_support
            import pandas as pd



            def agents (): 

                st.title(" :bar_chart: Dashboard support affid")
                #st.write("Contenu de la page Autre Page")

                #df_support = read_df_aircall()
                df_support = def_df_support(data_affid, data_affid, line_support, agents_support)
                start_date, end_date  = parameters_support()

                #df_support, df2, df_tickets, df3 = df_selection_support(df_support,df2, df_tickets, df3,values)
                df_support, df2 = df_selection_support(df_support,start_date, end_date)
                #df2, df_tickets, df3

                df_charge_pierre = charge_agents('Pierre GOUPILLON', df_support)
                df_charge_olivier = charge_agents('Olivier Sainte-Rose', df_support)
                df_charge_mourad = charge_agents('Mourad HUMBLOT', df_support)
                df_charge_archimede = charge_agents('Archimede KESSI', df_support)
                df_charge_frederic = charge_agents('Frederic SAUVAN', df_support)

                liste_data = [df_charge_pierre, df_charge_olivier, df_charge_mourad, 
                            df_charge_archimede, df_charge_frederic]
                df_charge = reduce(lambda  left,right: pd.merge(left,right,on=['Date'],how='outer'),liste_data).reset_index()
                df_charge = df_charge.sort_values(['Date'], ascending=True)

                df_charge_effectif = df_support.groupby(['Date']).agg({'Effectif':'mean'}).reset_index()
                df_charge = pd.merge(df_charge, df_charge_effectif, left_on='Date', right_on='Date', how = "left",)

                com_jour_mourad, temps_moy_com_mourad, nb_appels_jour_mourad = calcul_productivite_appels(df_support, 'Mourad HUMBLOT')
                com_jour_olivier, temps_moy_com_olivier, nb_appels_jour_olivier = calcul_productivite_appels(df_support, 'Olivier Sainte-Rose')
                com_jour_pierre, temps_moy_com_pierre, nb_appels_jour_pierre = calcul_productivite_appels(df_support, 'Pierre GOUPILLON')
                com_jour_archimede, temps_moy_com_archimede, nb_appels_jour_archimede = calcul_productivite_appels(df_support, 'Archimede KESSI')

                colm1, colm2, colm3= st.columns(3)
                colm1.metric('Mourad - Com Moy / Jour', com_jour_mourad)
                colm2.metric('Mourad - Temps Moy / Appel', round(temps_moy_com_mourad, 2))
                colm3.metric('Mourad - Nb Appels / Jour', round(nb_appels_jour_mourad, 2))

                colo1, colo2, colo3= st.columns(3)
                colo1.metric('Olivier - Com Moy / Jour', com_jour_olivier)
                colo2.metric('Olivier - Temps Moy / Appel', round(temps_moy_com_olivier, 2))
                colo3.metric('Olivier - Nb Appels / Jour', round(nb_appels_jour_olivier, 2))

                colp1, colp2, colp3= st.columns(3)
                colp1.metric('Pierre - Com Moy / Jour', com_jour_pierre)
                colp2.metric('Pierre - Temps Moy / Appel', round(temps_moy_com_pierre, 2))
                colp3.metric('Pierre - Nb Appels / Jour', round(nb_appels_jour_pierre, 2))

                cola1, cola2, cola3= st.columns(3)
                cola1.metric('Archimède - Com Moy / Jour', com_jour_archimede)
                cola2.metric('Archimède - Temps Moy / Appel', round(temps_moy_com_archimede, 2))
                cola3.metric('Archimède - Nb Appels / Jour', round(nb_appels_jour_archimede, 2))

                st.plotly_chart(graph_charge_agent(df_charge), use_container_width=True)

            agents()


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
