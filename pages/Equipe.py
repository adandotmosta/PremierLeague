import streamlit as st
from src.data.loader import DataLoader
from src.data.playersLoader import PlayerLoader
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
from src.data.processor import DataProcessor

from src.visualization.pitch import PitchVisualizer  




# Initialisation des classes
EVENTS_PATH = "../EPL 2011-12/Events"
LOGOS_PATH = "../EPL 2011-12/Logos"
PLAYERS_PATH = "../EPL 2011-12/Players"


events_loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
players_loader = PlayerLoader(PLAYERS_PATH)


processor = DataProcessor()




clubs = []
for club_name in os.listdir(LOGOS_PATH):
    if club_name.endswith((".png", ".jpg", ".jpeg")):  # Ensure valid image files
        club_logo = os.path.join(LOGOS_PATH, club_name)
        club_name = club_name.split(".")[0]  # Remove file extension
        clubs.append((club_name, club_logo))  # Store as (name, logo path)

# Create a dictionary for easy lookup
club_dict = {name: logo for name, logo in clubs}

# Function to format the dropdown display
def format_team(team_name):
    logo_path = club_dict[team_name]
    return f'<img src="{logo_path}" width="20"/> {team_name}'

# Use st.selectbox with names only
selected_team_name = st.selectbox(
    "Selectionner une équipe",
    list(club_dict.keys()),  # Display only names,
    index = 5

)

try :
    # Display the selected team logo & name
    # Créer une mise en page en 2 colonnes
    col1, col2,col3,col4 = st.columns([1,2, 2,1])  # Première colonne pour le logo, deuxième pour le podium

    with col2:
        if selected_team_name:
            st.markdown(f"<h3 >   {selected_team_name}</h3>", unsafe_allow_html=True)
            st.image(club_dict[selected_team_name], caption=selected_team_name, width=300)

    with col3:
        scorers, _, wins, draws, losses, a_domicile_wins, a_domicile_draws, a_domicile_looses = players_loader.get_stats_per_team(selected_team_name)
        top3 = scorers.head(3)

        # S'assurer qu'il y a au moins 3 buteurs
        if len(top3) >= 3:
            st.markdown("<h2 style='text-align: center;'>🏆 Meilleurs 3 buteurs</h2>", unsafe_allow_html=True)

            # Définir les joueurs du podium
            players = {
                "🥇": (top3.iloc[0]['Player'], top3.iloc[0]['Goals']),
                "🥈": (top3.iloc[1]['Player'], top3.iloc[1]['Goals']),
                "🥉": (top3.iloc[2]['Player'], top3.iloc[2]['Goals']),
            }

            # HTML & CSS pour le podium
            podium_html = f"""
            <div style="display: flex; justify-content: center; align-items: flex-end; gap: 30px; margin-top: 20px;">
                <div style="text-align: center;">
                    <p style="font-size: 25px;">🥈</p>
                    <div style="background: silver; width: 100px; height: 150px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                        <p style="color: white; font-weight: bold;">{players['🥈'][0]}<br>{players['🥈'][1]} ⚽</p>
                    </div>
                </div>
                <div style="text-align: center;">
                    <p style="font-size: 30px;">🥇</p>
                    <div style="background: gold; width: 120px; height: 180px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                        <p style="color: white; font-weight: bold;">{players['🥇'][0]}<br>{players['🥇'][1]} ⚽</p>
                    </div>
                </div>
                <div style="text-align: center;">
                    <p style="font-size: 25px;">🥉</p>
                    <div style="background: #CD7F32; width: 100px; height: 130px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                        <p style="color: white; font-weight: bold;">{players['🥉'][0]}<br>{players['🥉'][1]} ⚽</p>
                    </div>
                </div>
            </div>
            """
            st.markdown(podium_html, unsafe_allow_html=True)




    # Création d'une copie des scorers pour éviter de modifier le dataframe original
    top_scorers = scorers.copy()

    # Afficher le nom du joueur seulement si les buts sont supérieurs à 3
    top_scorers["ShowName"] = top_scorers["Player"].where(top_scorers["Goals"] > 3)

    # Création du graphique de dispersion
    fig = px.scatter(
        top_scorers, 
        x="Minutes Played", 
        y="Goals", 
        text=top_scorers["ShowName"],  # Afficher le nom seulement si les buts > 3
        size="Goals", 
        color="Goals", 
        color_continuous_scale="YlOrRd", 
        width=800,  # Largeur fixe pour le graphique
        height=900,  # Hauteur modérée
        title="⏳ Minutes Jouées vs ⚽ Buts Marqués",
        labels={"Minutes Played": "Minutes Jouées", "Goals": "Buts Marqués"},
        hover_data={"Player": True, "Goals": False, "Minutes Played": False, "ShowName": False},
    )

    # Mise à jour de la trace pour centrer le texte au-dessus des points
    fig.update_traces(textposition='top center')

    # Affichage sans colonnes, directement dans Streamlit
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)  # Centrage du graphique
    st.plotly_chart(fig)  # Affichage du graphique Plotly
    st.markdown("</div>", unsafe_allow_html=True)




    df = scorers.copy()
    # Calcul de 'efficacité (buts par minute)
    df["Efficacité"] = df["Goals"] / df["Minutes Played"]

    # Création du graphique
    df = df.sort_values(by="Efficacité", ascending=True)

    # Création du graphique
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df.iloc[-10 : ], x="Player", y="Efficacité", palette="coolwarm")

    # Ajout du titre et des labels
    plt.title("⚡ Efficacité des Joueurs (Buts par Minute)", fontsize=16)
    plt.xlabel("Joueur", fontsize=12)
    plt.ylabel("Efficacité (Buts par Minute)", fontsize=12)

    # Rotation des labels des joueurs pour une meilleure lisibilité
    plt.xticks(rotation=45, ha="right")




    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.pyplot(plt)

    #
    col1, col2 = st.columns(2)
    en_exterieur_losses = losses - a_domicile_looses
    en_exterieur_wins = wins - a_domicile_wins
    en_exterieur_draws = draws - a_domicile_draws
    # SECTION 2.1 - Nombre total de victoires et défaites
    with col1:
        st.markdown("## ⚽ Section 2.1 - Victoires & Défaites")

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=[selected_team_name],
            x=[wins],
            name="Victoires",
            orientation='h',
            marker=dict(color='blue'),
            text=[f"{wins} Wins"],
            textposition='inside'
        ))

        fig.add_trace(go.Bar(
            y=[selected_team_name],
            x=[-losses],  # Négatif pour afficher à gauche
            name="Défaites",
            orientation='h',
            marker=dict(color='red'),
            text=[f"{losses} Losses"],
            textposition='inside'
        ))

        fig.update_layout(
            title=f"Premier League: {selected_team_name} - Wins & Losses",
            barmode="relative",
            xaxis=dict(zeroline=True, zerolinecolor="black", showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title="Team"),
            template="plotly",
            height=400, width=600
        )

        st.plotly_chart(fig)

    # SECTION 2.2 - Comparaison Domicile vs Extérieur
    with col2:
        st.markdown("## 🏠✈️ Section 2.2 - Performance a Domicile vs Extérieur ")

        fig_bar = go.Figure()

        fig_bar.add_trace(go.Bar(
            name="À domicile",
            x=["Victoires", "Matchs nuls", "Défaites"],
            y=[a_domicile_wins, a_domicile_draws, a_domicile_looses],
            marker=dict(color="green"),
            text=[a_domicile_wins, a_domicile_draws, a_domicile_looses],
            textposition="outside"
        ))

        fig_bar.add_trace(go.Bar(
            name="À l'extérieur",
            x=["Victoires", "Matchs nuls", "Défaites"],
            y=[en_exterieur_wins, en_exterieur_draws, en_exterieur_losses],
            marker=dict(color="orange"),
            text=[en_exterieur_wins, en_exterieur_draws, en_exterieur_losses],
            textposition="outside"
        ))

        fig_bar.update_layout(
            title=f"{selected_team_name}: Domicile vs Extérieur",
            title_x=0.5,
            xaxis_title="Résultats des matchs",
            yaxis_title="Nombre de matchs",
            barmode="group",
            height=600, width=700
        )

        st.plotly_chart(fig_bar)



    # Update the layout


    # display the top3 players played the most games
    #fig = px.pie(scorers, names="Player", values="Goals", 
     #        hole=0.3, title="🥇 Distribution des Buts des Joueurs")
    #st.plotly_chart(fig)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    # Espacement pour séparer les sections

    st.title("⚽ Aperçu du Joueur : Analyse des Statistiques et Visualisations")
    st.markdown("<br>", unsafe_allow_html=True)





    if "compare_mode" not in st.session_state:
        st.session_state.compare_mode = False

    def plot_radar_chart(player_row, player_name, second_player_row=None, second_player_name=None):
        """
        Génère un radar chart pour un joueur et optionnellement un second en comparaison.

        Parameters:
            player_row (pd.Series): Données du premier joueur.
            player_name (str): Nom du premier joueur.
            second_player_row (pd.Series, optional): Données du deuxième joueur.
            second_player_name (str, optional): Nom du deuxième joueur.
        """
        if player_row is None or player_row.empty:
            st.error("Données du joueur introuvables.")
            return

        # Sélection des attributs pertinents (pas de normalisation appliquée)
        selected_attributes = [
            "Goals", "Shot", "Pass", "Dribble", "Block",
            "Foul", "Tackle", "Clearance", "Cross", "Touch"
        ]

        # Extraction des valeurs du premier joueur
        player_values = player_row[selected_attributes].values.flatten()
        angles = np.linspace(0, 2 * np.pi, len(selected_attributes), endpoint=False).tolist()
        angles += angles[:1]  # Fermer le polygone
        values1 = np.concatenate((player_values, [player_values[0]]))

        # Création du radar chart
        fig, ax = plt.subplots(figsize=(5, 5), subplot_kw={"polar": True})

        # Tracer le joueur 1 (en bleu)
        ax.fill(angles, values1, color='blue', alpha=0.3, label=player_name)
        ax.plot(angles, values1, color='blue', linewidth=2)

        # Vérifier si un deuxième joueur est sélectionné pour la comparaison
        if second_player_row is not None and not second_player_row.empty:
            second_player_values = second_player_row[selected_attributes].values.flatten()
            values2 = np.concatenate((second_player_values, [second_player_values[0]]))

            # Tracer le joueur 2 (en rouge)
            ax.fill(angles, values2, color='red', alpha=0.3, label=second_player_name)
            ax.plot(angles, values2, color='red', linewidth=2)

        # Ajouter les labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(selected_attributes, fontsize=10, rotation=30, ha='right')
        ax.set_yticklabels([])  # Masquer les valeurs des axes

        # Ajouter une légende
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.2))

        # Affichage dans Streamlit
        st.pyplot(fig,use_container_width=True)



    players = processor.get_player_names(selected_team_name)
    selected_player1 = st.selectbox("Select a player", players, key="first_player")


    # afficher les stats generales de chaque joueur
    stats = processor.get_stats_by_player(selected_player1)

    yellow_cards = stats["Yellow Card"].values[0]
    red_cards = stats["Red Card"].values[0]
    # Centrer le texte et les icônes avec du CSS
    st.markdown("""
        <style>
            .center-text {
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)













###


    # Utiliser la classe CSS pour centrer les éléments
    st.markdown('<div class="center-text">### Statistiques de {}</div>'.format(selected_player1), unsafe_allow_html=True)
    st.markdown('<div class="center-text">🟨 Cartes jaunes : {}</div>'.format(yellow_cards), unsafe_allow_html=True)
    st.markdown('<div class="center-text">🟥 Cartes rouges : {}</div>'.format(red_cards), unsafe_allow_html=True)
    # stats, containg
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>Radar des performances du joueur</h2>", unsafe_allow_html=True)



 
    player_stats1 = processor.get_player_metrics(selected_player1)

    # Choix de mode: solo ou comparaison
    col1, col2 = st.columns(2)
    with col2:
        compare_option = st.radio("Mode d'affichage", ["Solo", "Comparer"])


    if compare_option == "Comparer":
        st.session_state.compare_mode = True
        selected_player2 = st.selectbox("Select second player", players, key="second_player")
        player_stats2 = processor.get_player_metrics(selected_player2)
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            plot_radar_chart(player_stats1, selected_player1, player_stats2, selected_player2)
    else:
        st.session_state.compare_mode = False
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            plot_radar_chart(player_stats1, selected_player1)




    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center;'>📈 Évolution des buts du joueur au fil du temps</h2>", unsafe_allow_html=True)


    # chekbox, pour afficher si par match ou par mois
    # si par match, on affiche le nombre de buts par match
    # si par mois, on affiche le nombre de buts par mois
    # Display the aggregation options
# Utilisation de boutons pour la sélection de l'agrégation
    aggregation = None

    col0,col1, col2,col3 = st.columns([3,2,2,3])

    with col1:
        if st.button("Month"):
            aggregation = "month"

    with col2:
        if st.button("Match"):
            aggregation = "match"

    # Si l'agrégation est sélectionnée, récupère les statistiques

    if aggregation:
        evolutionary_stat = players_loader.evolution_by_month_match(selected_player1, selected_team_name, aggregation=aggregation)



        if evolutionary_stat.empty:
            st.write("No data available for the player.")
        else:
            title = ""
            # Convertir "month" en chaîne de caractères pour l'affichage
            if aggregation == "month":
                evolutionary_stat['match'] = evolutionary_stat['month'].astype(str)  # Assurez-vous que 'month' est une chaîne
                title = "mois"
            else:
                evolutionary_stat['match'] = evolutionary_stat['Match'].astype(str)  # Si l'agrégation est "match", utilisez 'match'
                title = "match"

            # Ajouter une colonne pour la somme cumulative des buts
            evolutionary_stat['Cumulative Goals'] = evolutionary_stat['Goals']

            # Afficher le titre pour le graphique
            st.markdown("<h3 style='text-align: center; font-weight: bold;'>Evolution des Buts marqués </h3>", unsafe_allow_html=True)
            
            # Tracer l'évolution des buts cumulés avec Plotly
            fig = px.line(evolutionary_stat, x='match', y='Cumulative Goals', 
                        title="Cumulative Goals Over Time", markers=True)

            # Mettre à jour la disposition du graphique
            fig.update_layout(xaxis_title=title, yaxis_title="Buts marqués")
            
            # Afficher le graphique
            st.plotly_chart(fig)
    else:
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            st.write("Selectionner Un mode Pour visualiser l'evolution selon les buts (Month or Match).")

# Assuming the class is saved in this file

    # Sample data - Replace this with your actual data


    # Create a DataFrame from the data
        # make slider for the matches

    # Centering the page with custom CSS
# Centering the page with custom CSS
    st.markdown("""
        <style>
            .centered {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                flex-direction: column;
            }
        </style>
    """, unsafe_allow_html=True)

    # Create a container for centering everything
    with st.container():
        # Add some padding at the top to separate from the header
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Center the title
        st.markdown("<h2 style='text-align: center;'>⚽ Analyse des tirs et des distributions</h2>", unsafe_allow_html=True)

        # Chargement des fichiers de match
        match_files = events_loader.load_match_files()
        extension = " - Events.csv"
        matches = [file.replace(extension, '') for file in match_files if selected_team_name in file]

        # Sélecteur pour choisir entre analyse globale ou par match
        col1,col2,col3 = st.columns([1,2,1])
        with col2:
            st.markdown("## 🌍 Sélectionnez le mode d'analyse")
            analysis_mode = st.radio("Choisissez l'analyse :", ("Globale", "Par match"), horizontal=True)

            if analysis_mode == "Par match":
                # Sélecteur du match avec un slider
                st.markdown("## 📅 Sélectionnez un match spécifique")
                selected_file = st.select_slider("Match", options=matches, format_func=lambda x: f"📅 {x}")
                st.success(f"✅ Match sélectionné : {selected_file}")

                # Chargement des données du match sélectionné
                file = selected_file + extension
                df_shots = processor.get_shots_cords(selected_player1, by="match", match_name=file)
                df_touches = processor.get_touch_cords(selected_player1, by="match", match_name=file)

            else:
                # Chargement des données globales
                df_shots = processor.get_shots_cords(selected_player1, by="total")
                df_touches = processor.get_touch_cords(selected_player1, by="total")

            # Initialiser le visualisateur
            pitch_visualizer = PitchVisualizer()

            # Sélecteur pour choisir entre tirs et distributions
            st.markdown("---")
            st.markdown("## 📊 Sélectionnez le type de visualisation")
            option = st.radio("Choisissez l'affichage :", ('Tirs', 'Distributions'), horizontal=True)

            # Créer un conteneur pour la visualisation
            with st.container():
                # Fixer les dimensions du graphique
                fig_width = 800  # Largeur fixe
                fig_height = 600  # Hauteur fixe

                # Affichage des heatmaps
                if option == 'Tirs':
                    st.subheader(f'🔥 Heatmap des tirs ({analysis_mode})')
                    fig = pitch_visualizer.creat_heat_map(df_shots, 'Shot Locations')

                    # Définir la taille du graphique
                    fig.update_layout(
                        width=fig_width,
                        height=fig_height
                    )

                    st.plotly_chart(fig, use_container_width=False)
                    st.info("Les zones les plus chaudes indiquent les endroits où les tirs sont les plus fréquents.")

                elif option == 'Distributions':
                    st.subheader(f'📌 Heatmap des touches de balle ({analysis_mode})')
                    fig = pitch_visualizer.creat_heat_map(df_touches, 'Touch Locations')

                    # Définir la taille du graphique
                    fig.update_layout(
                        width=fig_width,
                        height=fig_height
                    )

                    st.plotly_chart(fig, use_container_width=False)
                    st.info("Les zones les plus chaudes montrent où les joueurs touchent le plus souvent le ballon.")




#evolution par match


except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)