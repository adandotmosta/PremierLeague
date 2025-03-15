import streamlit as st
from typing import List
import os
import pandas as pd
import numpy as np
import cv2
from src.data.playersLoader import PlayerLoader

EVENTS_PATH = "../Events"
LOGOS_PATH = "../Logos"
TOTAL_MJ = 38
TEAM_NB = 20

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


# Initialisation des classes
PLAYERS_PATH = "../Players"
players_loader = PlayerLoader(PLAYERS_PATH)
try:
    top_scorers = players_loader.get_top_scorers_yearly(10)

    # Create a markdown header for the top 10 scorers section
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>Top 10 Scorers in the League</h2>", unsafe_allow_html=True)

    table_data = ""
    for rank, (player, stats) in enumerate(top_scorers.items(), 1):
        goals = stats["goals"]
        xg = stats["xG"]
        table_data += f"<tr><td style='padding: 8px; text-align: center;'>{rank}</td>\
                        <td style='padding: 8px; text-align: left;'>{player}</td>\
                        <td style='padding: 8px; text-align: center;'>{goals}</td>\
                        <td style='padding: 8px; text-align: center;'>{xg:.2f}</td></tr>"

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

    # Display the table in Streamlit
    st.markdown(html_table, unsafe_allow_html=True)



except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)

