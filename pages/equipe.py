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
    "Select a team",
    list(club_dict.keys())  # Display only names
)

try :
# Display the selected team logo & name
    if selected_team_name:
        st.markdown(f"### {selected_team_name}")
        st.image(club_dict[selected_team_name], caption=selected_team_name, width=150)

    
    scorers,_,wins,draws,losses,a_domicile_wins,a_domicile_draws,a_domicile_looses = players_loader.get_stats_per_team(selected_team_name)
    top3 = scorers.head(3)

    # Ensure there are at least 3 players
    if len(top3) >= 3:
        st.markdown("<h2 style='text-align: center;'>🏆 Top 3 Scorers Podium</h2>", unsafe_allow_html=True)

        # Define player data
        players = {
            "🥇": (top3.iloc[0]['Player'], top3.iloc[0]['Goals']),
            "🥈": (top3.iloc[1]['Player'], top3.iloc[1]['Goals']),
            "🥉": (top3.iloc[2]['Player'], top3.iloc[2]['Goals']),
        }

        # HTML & CSS for podium
        podium_html = f"""
        <div style="display: flex; justify-content: center; align-items: flex-end; gap: 40px; margin-top: 50px;">
            <div style="text-align: center;">
                <p style="font-size: 30px;">🥈</p>
                <div style="background: silver; width: 120px; height: 180px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                    <p style="color: white; font-weight: bold;">{players['🥈'][0]}<br>{players['🥈'][1]} ⚽</p>
                </div>
            </div>
            <div style="text-align: center;">
                <p style="font-size: 35px;">🥇</p>
                <div style="background: gold; width: 140px; height: 220px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                    <p style="color: white; font-weight: bold;">{players['🥇'][0]}<br>{players['🥇'][1]} ⚽</p>
                </div>
            </div>
            <div style="text-align: center;">
                <p style="font-size: 30px;">🥉</p>
                <div style="background: #CD7F32; width: 120px; height: 160px; display: flex; align-items: center; justify-content: center; border-radius: 10px;">
                    <p style="color: white; font-weight: bold;">{players['🥉'][0]}<br>{players['🥉'][1]} ⚽</p>
                </div>
            </div>
        </div>
        """

        st.markdown(podium_html, unsafe_allow_html=True)



    top_scorers = scorers.copy()  # Create a copy to avoid modifying the original dataframe
    top_scorers["ShowName"] = top_scorers["Player"].where(top_scorers["Goals"] > 3)  # Only show names if goals > 5

    # Create the scatter plot
    fig = px.scatter(top_scorers, x="Minutes Played", y="Goals", 
                    text=top_scorers["ShowName"],  # Use the filtered ShowName
                    size="Goals", color="Goals", width=1500, height=1100,
                    title="⏳ Minutes Jouées vs ⚽ Buts Marqués",
                    labels={"Minutes Played": "Minutes Jouées", "Goals": "Buts Marqués"},
                    hover_data={"Player": True, "Goals": False, "Minutes Played": False,"ShowName": False},)

    # Update the trace
    fig.update_traces(textposition='top center')

    # Display the chart
    st.plotly_chart(fig)


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

    # Affichage du graphique avec Streamlit
    st.pyplot(plt)




    total_games = 38
    print(a_domicile_wins)
    print(wins)
    away_wins = wins - a_domicile_wins

        # Prepare the data for the chart
    team_stats = {
        "Wins": wins,
        "Losses": losses
    }

    # Create the figure for the bar chart
    fig = go.Figure()

    # Add the wins and losses as separate bars (centered)
    fig.add_trace(go.Bar(
        y=[selected_team_name],
        x=[wins],
        name="Wins",
        orientation='h',
        marker=dict(color='blue'),
        text=[f"Wins: {wins}"],  # Display wins text
        textposition='inside'
    ))

    fig.add_trace(go.Bar(
        y=[selected_team_name],
        x=[-losses],  # Negative values to display losses to the left
        name="Losses",
        orientation='h',
        marker=dict(color='red'),
        text=[f"Losses: {losses}"],  # Display losses text
        textposition='inside'
    ))

    # Update the layout to center the bars
    fig.update_layout(
        title=f"Premier League: {selected_team_name} - Wins & Losses",
        barmode="relative",  # Ensure the bars are displayed side by side
        xaxis=dict(
            zeroline=True,
            zerolinecolor="black",
            showticklabels=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            title="Team"
        ),
        template="plotly",
        height=400,
        width=700
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig)

    # Prepare the data for the new chart
    home_wins = a_domicile_wins

    team_home_away_stats = {
        "Home Wins": home_wins,
        "Away Wins": away_wins
    }

    # Create the figure for the new bar chart
    fig_home_away = go.Figure()

    # Add the home wins as a bar (positive values)
    fig_home_away.add_trace(go.Bar(
        y=[selected_team_name],
        x=[home_wins],
        name="Home Wins",
        orientation='h',
        marker=dict(color='green'),
        text=[f"Home Wins: {home_wins}"],  # Display home wins text
        textposition='inside'
    ))

    # Add the away wins as a bar (negative values to display on the left)
    fig_home_away.add_trace(go.Bar(
        y=[selected_team_name],
        x=[-away_wins],  # Negative values to display away wins to the left
        name="Away Wins",
        orientation='h',
        marker=dict(color='orange'),
        text=[f"Away Wins: {away_wins}"],  # Display away wins text
        textposition='inside'
    ))

    # Update the layout to center the bars
    fig_home_away.update_layout(
        title=f"Premier League: {selected_team_name} - Home Wins vs Away Wins",
        barmode="relative",  # Ensure the bars are displayed side by side
        xaxis=dict(
            zeroline=True,
            zerolinecolor="black",
            showticklabels=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            title="Team"
        ),
        template="plotly",
        height=400,
        width=700
    )

    # Show the plot in Streamlit
    st.plotly_chart(fig_home_away)






    # Calcul des statistiques pour les matchs à l'extérieur
    en_exterieur_losses = losses - a_domicile_looses
    en_exterieur_wins = wins - a_domicile_wins
    en_exterieur_draws = draws - a_domicile_draws

    # Création de la figure
    fig_bar = go.Figure()

    # Ajout des performances à domicile
    fig_bar.add_trace(go.Bar(
        name="À domicile",
        x=["Victoires", "Matchs nuls", "Défaites"],  # Catégories
        y=[a_domicile_wins, a_domicile_draws, a_domicile_looses],  # Valeurs à domicile
        marker=dict(color="yellow"),  # Vert pour les matchs à domicile
        text=[a_domicile_wins, a_domicile_draws, a_domicile_looses],  # Affichage des valeurs
        textposition="outside"
    ))

    # Ajout des performances à l'extérieur
    fig_bar.add_trace(go.Bar(
        name="À l'extérieur",
        x=["Victoires", "Matchs nuls", "Défaites"],  # Catégories
        y=[en_exterieur_wins, en_exterieur_draws, en_exterieur_losses],  # Valeurs à l'extérieur
        marker=dict(color="black"),  # Rouge pour les matchs à l'extérieur
        text=[en_exterieur_wins, en_exterieur_draws, en_exterieur_losses],  # Affichage des valeurs
        textposition="outside"
    ))

    # Mise en page pour une meilleure visualisation
    fig_bar.update_layout(
        title=f"{selected_team_name}: Comparaison des performances (Domicile vs Extérieur)",
        title_x=0.5,  # Centrer le titre
        xaxis_title="Résultats des matchs",
        yaxis_title="Nombre de matchs",
        barmode="group",  # Histogramme groupé
        height=600,
        width=800
    )

    # Affichage du graphique dans Streamlit
    st.plotly_chart(fig_bar)




    # Update the layout


    # display the top3 players played the most games

    fig = px.pie(scorers, names="Player", values="Goals", 
             hole=0.3, title="🥇 Distribution des Buts des Joueurs")
    st.plotly_chart(fig)




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
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})

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
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

        # Affichage dans Streamlit
        st.pyplot(fig)



    players = processor.get_player_names(selected_team_name)
    selected_player1 = st.selectbox("Select a player", players, key="first_player")

    # Chargement des performances du premier joueur
    player_stats1 = processor.get_player_metrics(selected_player1)

    # Choix de mode: solo ou comparaison
    compare_option = st.radio("Mode d'affichage", ["Solo", "Comparer"])

    if compare_option == "Comparer":
        st.session_state.compare_mode = True
        selected_player2 = st.selectbox("Select second player", players, key="second_player")
        player_stats2 = processor.get_player_metrics(selected_player2)
        plot_radar_chart(player_stats1, selected_player1, player_stats2, selected_player2)
    else:
        st.session_state.compare_mode = False
        plot_radar_chart(player_stats1, selected_player1)

    # chekbox, pour afficher si par match ou par mois
    # si par match, on affiche le nombre de buts par match
    # si par mois, on affiche le nombre de buts par mois
    # Display the aggregation options
# Utilisation de boutons pour la sélection de l'agrégation
    aggregation = None

    col1, col2 = st.columns(2)

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
            # Convertir "month" en chaîne de caractères pour l'affichage
            if aggregation == "month":
                evolutionary_stat['match'] = evolutionary_stat['month'].astype(str)  # Assurez-vous que 'month' est une chaîne
            else:
                evolutionary_stat['match'] = evolutionary_stat['Match'].astype(str)  # Si l'agrégation est "match", utilisez 'match'

            # Ajouter une colonne pour la somme cumulative des buts
            evolutionary_stat['Cumulative Goals'] = evolutionary_stat['Goals']

            # Afficher le titre pour le graphique
            st.markdown("<h3 style='text-align: center; font-weight: bold;'>Evolution of Cumulative Goals</h3>", unsafe_allow_html=True)
            
            # Tracer l'évolution des buts cumulés avec Plotly
            fig = px.line(evolutionary_stat, x='match', y='Cumulative Goals', 
                        title="Cumulative Goals Over Time", markers=True)

            # Mettre à jour la disposition du graphique
            fig.update_layout(xaxis_title="match", yaxis_title="Cumulative Goals")
            
            # Afficher le graphique
            st.plotly_chart(fig)
    else:
        st.write("Selectionner Un mode Pour visualiser l'evolution selon les buts (Month or Match).")

# Assuming the class is saved in this file

    # Sample data - Replace this with your actual data


    # Create a DataFrame from the data
    # make slider pour les matches
    match_files = events_loader.load_match_files()
    extension = " - Events.csv"
    matches = [file.replace(extension,'') for file in match_files if selected_team_name in file]



    selected_file = st.select_slider("Sélectionnez un match", options=matches)
    
    # Get the selected match based on the slider's index

    df = processor.get_shots_cords(selected_player1,selected_file + extension)



    # Initialize the pitch visualizer
    pitch_visualizer = PitchVisualizer()

    # Set up the Streamlit app
    st.title('Football Shot Locations Heatmap')
    st.write('This app visualizes shot locations on a football pitch.')

    # Create and display the heatmap
    fig = pitch_visualizer.creat_heat_map(df, 'Shot Locations')

    # Display the plotly chart using Streamlit
    st.plotly_chart(fig)



#evolution par match


except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)