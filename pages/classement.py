import streamlit as st
from typing import List
import os
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt

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
