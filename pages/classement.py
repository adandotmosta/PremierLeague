import streamlit as st
from typing import List
import os
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import plotly.express as px
from src.data.loader import DataLoader
from src.data.playersLoader import PlayerLoader
from src.visualization.xgScore import visualise_correlation_by_player, visualise_correlation_by_bins




EVENTS_PATH = "../EPL 2011-12/Events"
LOGOS_PATH = "../EPL 2011-12/Logos"
PLAYERS_PATH = "../EPL 2011-12/Players"
TOTAL_MJ = 38
TEAM_NB = 20

loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
players_loader = PlayerLoader(PLAYERS_PATH)

def load_match_files() -> List[str]:
    """Liste tous les fichiers CSV dans le répertoire des événements."""
    return sorted([
        f for f in os.listdir(EVENTS_PATH) 
        if f.endswith('.csv')
    ])

match_files = load_match_files()

def load_teams_names() -> List[str]:
    return sorted([
        f for f in os.listdir(LOGOS_PATH) 
        if f.endswith('.jpg')
    ])

teams_names = [i[:-4] for i in load_teams_names()]

print(teams_names)

zeros = np.zeros(TEAM_NB, dtype=np.int8)

dict = {
    'Teams' : teams_names,
    'Played'  : zeros,
    'Won' : zeros,
    'Drawn' : zeros,
    'Lost' : zeros,
    'GF' : zeros,
    'GA' : zeros,
    'GD' : zeros,
    'Points' : zeros
}
selected_minute = st.slider("Select Matchweek", 0, TOTAL_MJ)

ranking = pd.DataFrame(dict)

st.table(ranking)

# visualizing the correlation between angle of shoot and xgscore


df_shots_aggregated_by_player_shots = loader.get_angle_xg()

visualise_correlation_by_player(df_shots_aggregated_by_player_shots)

df_shots_by_bins = loader.get_angle_bins()
visualise_correlation_by_bins(df_shots_by_bins)



top_scorers = players_loader.get_top_scorers_yearly(20)

st.markdown("<h2 style='text-align: center; font-weight: bold;'>Top 10 Scorers in the Club</h2>", unsafe_allow_html=True)

# Prepare the table data
table_data = ""
player_names = []
goals_data = []
for rank, (player, stats) in enumerate(top_scorers.items(), 1):
    goals = stats["goals"]
    xg = stats["xG"]
    player_names.append(player)
    goals_data.append(goals)
    table_data += f"<tr><td style='padding: 8px; text-align: center;'>{rank}</td>\
                    <td style='padding: 8px; text-align: left;'>{player}</td>\
                    <td style='padding: 8px; text-align: center;'>{goals}</td>\
                    <td style='padding: 8px; text-align: center;'>{xg:.2f}</td></tr>"

# Display the table
html_table = f"""
<table style="width: 100%; border-collapse: collapse; margin-top: 20px; border: 1px solid #ddd;">
    <thead>
        <tr style='background-color: #f1f1f1;'>
            <th style='padding: 10px; text-align: center;'>Rank</th>
            <th style='padding: 10px; text-align: left;'>Player</th>
            <th style='padding: 10px; text-align: center;'>Goals</th>
            <th style='padding: 10px; text-align: center;'>xG (Expected Goals)</th>
        </tr>
    </thead>
    <tbody>
        {table_data}
    </tbody>
</table>
"""
st.markdown(html_table, unsafe_allow_html=True)

# Create the Pie Chart for Goals Distribution
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(goals_data, labels=player_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
ax.set_title("⚽ Goals Distribution of Top Scorers", fontsize=16)

# Display the pie chart
st.pyplot(fig)

top_scorers,top_passers,top_shooters,top_defenders = players_loader.get_top_performers(3)
st.table(top_scorers[['Player Name']])

players = {
    "🥇": (top_scorers.iloc[0]['Player Name'], top_scorers.iloc[0]['Goals']),
    "🥈": (top_scorers.iloc[1]['Player Name'], top_scorers.iloc[1]['Goals']),
    "🥉": (top_scorers.iloc[2]['Player Name'], top_scorers.iloc[2]['Goals']),
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

# Display the podium in Streamlit
st.markdown(podium_html, unsafe_allow_html=True)



fig, ax = plt.subplots(figsize=(4, 5))
ax.barh(top_defenders['Player Name'], top_defenders['IPD'], color='skyblue')
ax.set_xlabel('IPD (Interceptions par match)')
ax.set_title('Top 3 Défenseurs Basés sur IPD')

# Afficher le graphique dans Streamlit
st.pyplot(fig)



# Create the pie chart
fig_pie = px.pie(
    top_passers,
    names="Player Name",  # Categories (player names)
    values="Pass",  # Values (number of passes)
    title="Top Passers Distribution",
    hole=0.3  # Optional: Creates a donut chart by adding a hole in the middle
)

# Update layout for better visualization
fig_pie.update_traces(textposition='inside', textinfo='percent+label')  # Show percentage and labels inside the slices
fig_pie.update_layout(
    height=500,
    width=700
)

# Display the chart in Streamlit
st.plotly_chart(fig_pie)


if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

def plot_radar_chart(player_row, player_name, second_player_row=None, second_player_name=None):
    """
    Génère un radar chart pour un joueur et optionnellement pour un second joueur en comparaison.

    Parameters:
        player_row (pd.Series): Données du premier joueur.
        player_name (str): Nom du premier joueur.
        second_player_row (pd.Series, optional): Données du deuxième joueur.
        second_player_name (str, optional): Nom du deuxième joueur.
    """
    if player_row is None or player_row.empty:
        st.error("Données du joueur introuvables.")
        return

    # Sélection des attributs pertinents
    selected_attributes = ['Goalkeeper Save', 'Goalkeeper Catch', 'Goalkeeper Punch', 'Goalkeeper Drop Catch', 
                           'Goalkeeper Pick Up', 'Goalkeeper Kick', 'Goalkeeper Throw', 'Goal Kick']

    # Extraction des valeurs du joueur principal
    player_values = player_row[selected_attributes].values.flatten()

    # Création des angles pour le radar chart
    angles = np.linspace(0, 2 * np.pi, len(selected_attributes), endpoint=False).tolist()
    angles += angles[:1]  # Fermer le polygone

    # Ajouter la première valeur à la fin pour fermer le polygone
    values1 = np.concatenate((player_values, [player_values[0]]))

    # Création du radar chart
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})

    # Tracer le joueur 1 (toujours affiché)
    ax.fill(angles, values1, color='blue', alpha=0.3, label=player_name)
    ax.plot(angles, values1, color='blue', linewidth=2)

    # Vérifier si un deuxième joueur est sélectionné pour la comparaison
    if second_player_row is not None and not second_player_row.empty:
        second_player_values = second_player_row[selected_attributes].values.flatten()

        # Ajouter la première valeur à la fin pour fermer le polygone
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

# Sélection du premier gardien
gks = players_loader.goalkeepers_names()
selected_player1 = st.selectbox("Select a goalkeeper", gks, key="first_gk")

# Chargement des performances du premier joueur
gk_stats1 = players_loader.goalkeeper_performance(selected_player1)

# Bouton pour activer la comparaison
if st.button("Compare with another goalkeeper"):
    st.session_state.compare_mode = True  # Active le mode comparaison

# Vérifier si le mode comparaison est activé
if st.session_state.compare_mode:
    selected_player2 = st.selectbox("Select second goalkeeper", gks, key="second_gk")

    # Chargement des performances du deuxième joueur
    gk_stats2 = players_loader.goalkeeper_performance(selected_player2)

    # Affichage du radar chart avec comparaison
    plot_radar_chart(gk_stats1, selected_player1, gk_stats2, selected_player2)
else:
    # Affichage du radar chart unique
    plot_radar_chart(gk_stats1, selected_player1)



