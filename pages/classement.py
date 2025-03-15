import streamlit as st
from typing import List
import os
import pandas as pd
import numpy as np
import cv2

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

