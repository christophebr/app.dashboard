import streamlit as st
#import pandas as pd
#import numpy as np
#from datetime import date, timedelta
#from datetime import datetime, timedelta
#import datetime as dt
#import plotly.express as px
#from plotly.subplots import make_subplots

import streamlit as st
#import streamlit_authenticator as stauth

#from partenaires import read_df_jira
#from partenaires import parameters
#from partenaires import df_selection
#from partenaires import bar_chart_category_delai
#from partenaires import metrics

#from support import read_df_aircall
#from support import parameters_support
#from support import df_selection_support

from Data_support import graph_activite , graph_taux_jour , graph_taux_heure, graph_charge_affid_stellair
from support import metrics_support
import plotly.graph_objects as go

#import yaml
#from yaml.loader import SafeLoader


st.set_page_config(
    page_title= " :bar_chart: Dashboard support partenaires",
    layout= "wide",
    initial_sidebar_state="collapsed",
    )


PAGES = {
    "Partenaires": "partenaires",
    "Support": "support"
    }



if __name__ == "__main__": 

    selection_page = st.sidebar.selectbox("Choix de la page", list(PAGES.keys()), key="unique_page_selection")

    if selection_page == "Partenaires":
        from partenaires import read_df_jira
        from partenaires import parameters
        from partenaires import df_selection
        from partenaires import bar_chart_category_delai
        from partenaires import metrics

        def partenaires (): 
            st.title(" :bar_chart: Dashboard support partenaires")
            
            df = read_df_jira()
            df2 = df.copy()
            df3 = df.copy()


            defaut_val = 'All'
            selection = [defaut_val] + list(df['Partenaires'].unique())
            choix_formulaire = [defaut_val] + list(df['Customer Request Type'].unique())
            options_partenaire, options_formulaire, values, metric = parameters (selection, choix_formulaire)

            df, df2, df3 = df_selection(df, df2, df3, values, metric)

            [mean_delai_before, df_formulaire,metric_nb_ticket, metric_nb_ticket_n2, tendance_ticket, tendance_n2, mean_delai, 
            tendance_delai, metric_nb_ticket_presta, metric_nb_ticket_presta_before, 
            tendance_presta, filtered_df_describe, df_superieur_2h, count_superieur_2h, 
            tendance_superieur_2h, nb_appel_direct, tendance_appel_direct, fig_box_delai] = metrics(df, df3, options_partenaire, options_formulaire, defaut_val)

        

            col1, col2, col3 = st.columns(3)
            col1.metric("Nombre de ticket", metric_nb_ticket, tendance_ticket, delta_color="inverse")
            #col1.metric("Nombre de ticket", metric_nb_ticket, tendance_ticket)
            col2.metric("Nombre de ticket N2",metric_nb_ticket_n2, tendance_n2, delta_color="inverse")
            col3.metric("Nombre de ticket prestation", metric_nb_ticket_presta, tendance_presta)
            
            col_1, col_2, col_3 = st.columns(3)
            col_1.metric("Nombre de ticket > 2h", count_superieur_2h, tendance_superieur_2h, delta_color="inverse")
            col_2.metric("Nombre appel direct", nb_appel_direct, tendance_appel_direct, delta_color="inverse")
            col_3.metric("Délai moyen - Prise en charge", mean_delai,tendance_delai, delta_color="inverse")
            #col_3.metric("Délai moyen - Prise en charge", (f"{int(mean_delai)} min"), (f"{round(tendance_delai,2):.2f}%"), delta_color="inverse")


            fig_category, fig_ticket, fig_category_ticket, metric_nb_ticket = bar_chart_category_delai(df, df2, options_partenaire, options_formulaire, defaut_val)
        
            col_plot1, col_plot2 = st.columns(2) 

            with col_plot1:
                st.plotly_chart(fig_box_delai)
                st.plotly_chart(fig_category)

            with col_plot2:
                st.plotly_chart(fig_category_ticket)
                #st.plotly_chart(fig_delai)


            st.dataframe(df_formulaire)

            #st.dataframe(df_group_delai)


        partenaires()

    elif selection_page == "Support":
        from support import read_df_aircall
        from partenaires import read_df_jira
        from support import parameters_support
        from support import df_selection_support
        from support import metrics_support
        from support import tickets_support
        from Data_support import graph_activite , graph_taux_jour , graph_taux_heure, graph_charge_affid_stellair
        import plotly.graph_objects as go

        def support():
            st.title("Autre Page")
            st.write("Contenu de la page Autre Page")

            df_support = read_df_aircall()
            df2 = read_df_aircall()

            #df_tickets = read_df_jira()
            #df3 = read_df_jira()


            defaut_val = 'All'

            #selection = [defaut_val] + list(df_tickets['line'].unique())
            values = parameters_support()

            df_support, df2 = df_selection_support(df_support,df2,values)

            [Taux_de_service , tendance_taux, Entrant, tendance_entrant, Numero_unique, 
            tendance_unique, temps_moy_appel, tendance_appel, Nombre_appel_jour_agent] = metrics_support(df_support, df2)

            #df_grouped_ticket = tickets_support(df_tickets, option_pipeline, defaut_val)

            col1, col2, col3 = st.columns(3)
            col1.metric("Taux de service en %", Taux_de_service, tendance_taux)
            col2.metric("Appels entrant / Jour",Entrant, tendance_entrant)
            col3.metric("Numéros unique", Numero_unique, tendance_unique)
            #col4.metric("Délai moyen - Prise en charge", (f"{int(mean_delai)} min"), (f"{round(tendance_delai,2):.2f}%"))

            col_1, col_2, col_3 = st.columns(3)
            col_1.metric("Temps Moy / Appel", temps_moy_appel, tendance_appel)
            col_2.metric("Nombre appels jour / agent", Nombre_appel_jour_agent)

            st.plotly_chart(graph_activite(df_support), use_container_width=True)

            col_graph1, col_graph2 = st.columns(2)
            col_graph1.plotly_chart(graph_taux_jour(df_support))
            col_graph2.plotly_chart(graph_taux_heure(df_support))

            col_graph11, col_graph22 = st.columns(2)
            col_graph11.plotly_chart(graph_charge_affid_stellair(df_support))

        support()

        
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
