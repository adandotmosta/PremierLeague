import streamlit as st
from typing import List
import os
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt
import plotly.express as px
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.data.playersLoader import PlayerLoader
from src.visualization.xgScore import visualise_correlation_by_player, visualise_correlation_by_bins
from datetime import datetime, timedelta




EVENTS_PATH = "../EPL 2011-12/Events"
LOGOS_PATH = "../EPL 2011-12/Logos"
PLAYERS_PATH = "../EPL 2011-12/Players"
TOTAL_MJ = 38
TEAM_NB = 20

processor = DataProcessor()

loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
players_loader = PlayerLoader(PLAYERS_PATH)

def load_teams_names() -> List[str]:
    return sorted([
        f[:-4] for f in os.listdir(LOGOS_PATH) 
        if f.endswith('.jpg')
    ])

teams_names = load_teams_names()

# Initialize ranking data properly with correct data types
ranking_data = {
    'Teams': teams_names,
    'Played': [0] * TEAM_NB,
    'Won': [0] * TEAM_NB,
    'Drawn': [0] * TEAM_NB,
    'Lost': [0] * TEAM_NB,
    'GF': [0] * TEAM_NB,
    'GA': [0] * TEAM_NB,
    'GD': [0] * TEAM_NB,
    'Points': [0] * TEAM_NB
}

ranking = pd.DataFrame(ranking_data)

# Function to update ranking table based on match results
def update_ranking(home_team, away_team, home_score, away_score):
    # Get team indices
    home_idx = ranking[ranking['Teams'] == home_team].index[0]
    away_idx = ranking[ranking['Teams'] == away_team].index[0]
    
    # Update matches played
    ranking.at[home_idx, 'Played'] += 1
    ranking.at[away_idx, 'Played'] += 1
    
    # Update goals
    ranking.at[home_idx, 'GF'] += home_score
    ranking.at[home_idx, 'GA'] += away_score
    ranking.at[away_idx, 'GF'] += away_score
    ranking.at[away_idx, 'GA'] += home_score
    
    # Update goal difference
    ranking.at[home_idx, 'GD'] = ranking.at[home_idx, 'GF'] - ranking.at[home_idx, 'GA']
    ranking.at[away_idx, 'GD'] = ranking.at[away_idx, 'GF'] - ranking.at[away_idx, 'GA']
    
    # Update wins, draws, losses and points
    if home_score > away_score:
        # Home team wins
        ranking.at[home_idx, 'Won'] += 1
        ranking.at[home_idx, 'Points'] += 3
        ranking.at[away_idx, 'Lost'] += 1
    elif home_score < away_score:
        # Away team wins
        ranking.at[away_idx, 'Won'] += 1
        ranking.at[away_idx, 'Points'] += 3
        ranking.at[home_idx, 'Lost'] += 1
    else:
        # Draw
        ranking.at[home_idx, 'Drawn'] += 1
        ranking.at[away_idx, 'Drawn'] += 1
        ranking.at[home_idx, 'Points'] += 1
        ranking.at[away_idx, 'Points'] += 1

# Function to calculate final score from match data
def get_final_score(match_data, home_team, away_team):
    # Count goals for each team
    home_goals = len(match_data[(match_data['Event Name'] == 'Goal') & (match_data['Player1 Team'] == home_team)])
    away_goals = len(match_data[(match_data['Event Name'] == 'Goal') & (match_data['Player1 Team'] == away_team)])
    return home_goals, away_goals

# Function to extract date from match name
def extract_date(match_name):
    # Example: '11.08.13 Blackburn Rovers v Wolverhampton Wanderers'
    date_str = match_name.split(' ')[0]
    try:
        return datetime.strptime(date_str, '%y.%m.%d')
    except ValueError:
        return None

# Group match files by matchday with a 3-day window
@st.cache_data
def group_matches_by_matchday():
    match_files = loader.load_match_files()
    
    # Dictionary to store matches with their metadata
    match_info = {}
    
    # Extract match info for all matches
    for match_file in match_files:
        match_data = loader.load_match_data(match_file)
        if not match_data.empty and 'Match Name' in match_data.columns:
            match_name = match_data['Match Name'].iloc[0]
            date = extract_date(match_name)
            print(date)
            if date:
                home_team, away_team = loader.get_teams(match_data)
                match_info[match_file] = {
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'match_name': match_name
                }
    
    # Sort matches by date
    sorted_matches = sorted(match_info.items(), key=lambda x: x[1]['date'])
    
    # Group matches that occur within 3 days of each other
    matchdays = []
    current_matchday = []
    reference_date = None
    
    for match_file, info in sorted_matches:
        match_date = info['date']
        
        if reference_date is None or (match_date - reference_date).days > 3:
            # Start a new matchday
            if current_matchday:
                matchdays.append(current_matchday)
            current_matchday = [match_file]
            reference_date = match_date
        else:
            # Add to current matchday
            current_matchday.append(match_file)
    
    # Add the last matchday
    if current_matchday:
        matchdays.append(current_matchday)
    
    # Make sure we have exactly TOTAL_MJ matchdays
    # If we have more, combine some adjacent matchdays
    while len(matchdays) > TOTAL_MJ:
        # Find the smallest matchday
        smallest_idx = min(range(len(matchdays)-1), key=lambda i: len(matchdays[i]))
        # Merge with the next one
        matchdays[smallest_idx].extend(matchdays[smallest_idx + 1])
        del matchdays[smallest_idx + 1]
    
    # If we have fewer, add empty matchdays
    while len(matchdays) < TOTAL_MJ:
        matchdays.append([])
    
    return matchdays

# Process all matches up to the selected matchweek
def process_matches_up_to_matchweek(matchweek):
    # Reset ranking table
    for col in ['Played', 'Won', 'Drawn', 'Lost', 'GF', 'GA', 'GD', 'Points']:
        ranking[col] = 0
    
    # Group matches by matchday
    matchdays = group_matches_by_matchday()
    
    # Process matches up to the selected matchweek
    for i in range(min(matchweek, len(matchdays))):
        for match_file in matchdays[i]:
            # Load match data
            match_data = loader.load_match_data(match_file)
            
            if not match_data.empty:
                # Get team names
                teams = loader.get_teams(match_data)
                if len(teams) >= 2:
                    home_team, away_team = teams[0], teams[1]
                    
                    # Calculate final score
                    home_score, away_score = get_final_score(match_data, home_team, away_team)
                    
                    # Update ranking
                    update_ranking(home_team, away_team, home_score, away_score)
    
    # Sort ranking by points (descending), goal difference (descending), and goals for (descending)
    return ranking.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)

# Streamlit app layout
st.title("EPL 2011-12 Analyse de la Saison")

# Get matchdays for the dropdown
matchdays = group_matches_by_matchday()
total_matchdays = TOTAL_MJ  # Always use 38 matchdays

# Sidebar for controls
st.sidebar.header("Controls")
selected_matchweek = st.sidebar.slider("Sélectionner la semaine ", 0, total_matchdays, 0)

# Show league table by default with initial values
st.subheader(f"Table de la Ligue")
if selected_matchweek == 0:
    # Display initial ranking (sorted) without any matches processed
    initial_ranking = ranking.sort_values(by=['Points', 'GD', 'GF'], ascending=[False, False, False]).reset_index(drop=True)
    st.dataframe(initial_ranking.style.apply(lambda x: ['background-color: #e6f7ff' if i < 4 else
                                          'background-color: #fff0e6' if i > len(initial_ranking) - 4 else '' 
                                          for i in range(len(initial_ranking))], axis=0))
    st.info("Select a matchweek to view updated standings and match results.")
else:
    # Sample match details
    if selected_matchweek <= len(matchdays) and matchdays[selected_matchweek-1]:
        # Get a sample match from the selected matchweek
        sample_match_file = matchdays[selected_matchweek-1][0]
        sample_match_data = loader.load_match_data(sample_match_file)
        
        if not sample_match_data.empty and 'Match Name' in sample_match_data.columns:
            sample_match_name = sample_match_data['Match Name'].iloc[0]

    sorted_ranking = process_matches_up_to_matchweek(selected_matchweek)
    
    st.subheader(f"League Table after Matchweek {selected_matchweek}")
    
    # Display ranking table
    st.dataframe(sorted_ranking.style.apply(lambda x: ['background-color: #e6f7ff' if i < 4 else
                                              'background-color: #fff0e6' if i > len(sorted_ranking) - 4 else '' 
                                              for i in range(len(sorted_ranking))], axis=0))
    
    # Display top 5 teams with their logos
    st.subheader("Top 5 Teams")
    top_teams = sorted_ranking.head(5)
    
    cols = st.columns(5)
    for i, (idx, team) in enumerate(top_teams['Teams'].items()):
        logo = loader.load_logos(team)
        if logo is not None:
            cols[i].image(logo, width=100, caption=f"{i+1}. {team}")
        else:
            cols[i].write(f"{i+1}. {team}")
    
    # Show matches in the current matchweek
    if selected_matchweek <= len(matchdays):
        st.subheader(f"Matches in Matchweek {selected_matchweek}")
        
        matches_in_week = matchdays[selected_matchweek-1]
        
        if matches_in_week:  # Check if there are matches for this matchweek
            for match_file in matches_in_week:
                match_data = loader.load_match_data(match_file)
                
                if not match_data.empty:
                    teams = loader.get_teams(match_data)
                    if len(teams) >= 2:
                        home_team, away_team = teams[0], teams[1]
                        home_score, away_score = get_final_score(match_data, home_team, away_team)
                        
                        # Display match result
                        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                        
                        home_logo = loader.load_logos(home_team)
                        away_logo = loader.load_logos(away_team)
                        
                        with col1:
                            st.write(home_team)
                            if home_logo is not None:
                                st.image(home_logo, width=50)
                        
                        with col2:
                            st.write(f"{home_score}")
                        
                        with col3:
                            st.write("vs")
                        
                        with col4:
                            st.write(f"{away_score}")
                        
                        with col5:
                            st.write(away_team)
                            if away_logo is not None:
                                st.image(away_logo, width=50)
                        
                        st.write("---")
        else:
            st.info("No matches available for this matchweek.")


#st.table(ranking)

# visualizing the correlation between angle of shoot and xgscore


df_shots_aggregated_by_player_shots = loader.get_angle_xg()

#visualise_correlation_by_player(df_shots_aggregated_by_player_shots)

df_shots_by_bins = loader.get_angle_bins()
#visualise_correlation_by_bins(df_shots_by_bins)



top_scorers = players_loader.get_top_scorers_yearly(20)

#st.markdown("<h2 style='text-align: center; font-weight: bold;'>Top 10 Scorers in the Club</h2>", unsafe_allow_html=True)

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
#st.markdown(html_table, unsafe_allow_html=True)

# Create the Pie Chart for Goals Distribution
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(goals_data, labels=player_names, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
ax.set_title("⚽ Goals Distribution of Top Scorers", fontsize=16)

# Display the pie chart
#st.pyplot(fig)
top_n = 10
top_scorers,top_passers,top_shooters,top_defenders = players_loader.get_top_performers(top_n)
#st.table(top_scorers[['Player Name']])



# Génération dynamique des images des joueurs
photos = [f"players/{player}.jpg" for player in top_scorers["Player Name"][0:3]]
print(f" photos are ={photos}")

# Vérifier si les images existent sinon utiliser une image par défaut
photos = [photo if os.path.exists(photo) else "players/default.jpg" for photo in photos]
print("real photos are = ", photos)
top_scorers = top_scorers.reset_index(drop=True)

# Vérification des trois meilleurs joueurs
print(f"Top scorers names and goals:")
print(top_scorers[["Player Name", "Goals"]].head(3))

# Récupération des trois meilleurs joueurs
players = {
    "🥇": (top_scorers.loc[0, "Player Name"], top_scorers.loc[0, "Goals"], photos[0]),
    "🥈": (top_scorers.loc[1, "Player Name"], top_scorers.loc[1, "Goals"], photos[1]),
    "🥉": (top_scorers.loc[2, "Player Name"], top_scorers.loc[2, "Goals"], photos[2]),
}

# Affichage du podium
st.markdown("<h2 style='text-align: center;'>🏆 Podium des Meilleurs Buteurs</h2>", unsafe_allow_html=True)

# Création de trois colonnes pour les joueurs
col1, col2, col3 = st.columns(3)

# 🥈 Deuxième place
with col1:
    st.image(players["🥈"][2], caption=f"{players['🥈'][0]} - {players['🥈'][1]} ⚽", width=200)
    st.markdown(f"### 🥈 {players['🥈'][0]}")
    st.write(f"{players['🥈'][1]} Goals")

# 🥇 Première place (au centre)
with col2:
    #centrer l'image
    st.image(players["🥇"][2], caption=f"{players['🥇'][0]} - {players['🥇'][1]} ⚽", width=250)

    st.markdown(f"### 🥇 {players['🥇'][0]}")
    st.write(f"{players['🥇'][1]} Goals")

# 🥉 Troisième place
with col3:
    st.image(players["🥉"][2], caption=f"{players['🥉'][0]} - {players['🥉'][1]} ⚽", width=200)
    st.markdown(f"### 🥉 {players['🥉'][0]}")
    st.write(f"{players['🥉'][1]} Goals")

# Ajout d'un espace pour séparer les sections
st.markdown("<br><br><br>", unsafe_allow_html=True)




######################################### meilleurs defendeurs


# Couleurs automatiques (matplotlib choisit aléatoirement)
colors = plt.cm.tab10.colors[:len(top_defenders)]

# 🟢 Graphique des défenseurs (barres verticales)
fig, ax = plt.subplots(figsize=(6, 4))  # Taille réduite

bars = ax.bar(
    top_defenders["Player Name"],
    top_defenders["IPD"],
    color=colors,  # Couleurs automatiques
    edgecolor="black"
)

# Personnalisation du graphique
ax.set_ylabel("IPD (Interceptions par match)", fontsize=12, fontweight="bold")
ax.set_xlabel("Joueurs", fontsize=12, fontweight="bold")
ax.set_title(f"Meilleurs {top_n} Défenseurs Basés sur IPD", fontsize=14, fontweight="bold", color="darkred")

# Rotation des noms des joueurs pour éviter le chevauchement
ax.set_xticklabels(top_defenders["Player Name"], rotation=20)

# 🎯 Affichage centré et ajusté
col1, col2, col3 = st.columns([1, 3, 1])  # Centre avec la colonne du milieu
with col2:
    st.pyplot(fig, use_container_width=False)

# 🟢 Espacement entre les deux graphiques
st.markdown("<br><br>", unsafe_allow_html=True)

# 🟢 Graphique des passeurs (barres horizontales)
fig_bar = px.bar(
    top_passers,
    x="Pass",
    y="Player Name",
    text="Pass",
    orientation="h",  # Barres horizontales
    title="Meilleurs Passeurs Basés sur le Nombre de Passes",
    color="Pass",  # Gradient basé sur les passes
    color_continuous_scale="Blues"
)

# Ajustements du design et taille réduite
fig_bar.update_traces(textfont_size=12, textposition="inside")  # Taille texte réduite
fig_bar.update_layout(
    height=600,  # Hauteur ajustée
    width=800,   # Largeur optimisée
    xaxis_title="Nombre de Passes",
    yaxis_title="Joueurs",
    showlegend=False
)

# 🎯 Affichage centré
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.plotly_chart(fig_bar, use_container_width=False)



# Données fictives
stats = [
    {"icon": "🏃‍♂️", "value": 380, "label": "Matches played"},
    {"icon": "⚽", "value": 1066, "label": "Goals / game"},
    {"icon": "🟨", "value": 1176, "label": "Cards / match"},
    {"icon": "🟥", "value": 65, "label": "Cards / match"}
]

results = [
    {"label": "Home wins", "value": "171 (45%)"},
    {"label": "Away wins", "value": "116 (31%)"},
    {"label": "Draws", "value": "93 (24%)"}
]

highlights = [
    {"label": "Most common result", "value": "1 - 1 (45 times)"},
    {"label": "Match with most goals", "value": "8 - 2 (Manchester United - Arsenal)"}
]






# gk stats, 

# Convertir les données en DataFrame

df = processor.get_top_gks(20)
# Trier les gardiens par le coefficient (plus bas étant meilleur)
df_sorted = df.sort_values(by='gk_coef', ascending=True)

# Créer une visualisation avec matplotlib
fig, ax = plt.subplots(figsize=(10, 6))

# Tracer un graphique à barres
ax.barh(df_sorted['Player Name'], df_sorted['gk_coef'], color='lightblue')

# Ajouter des labels et un titre
# nombre de buts reçus par match
ax.set_xlabel('Coefficient 1/(Nombre de buts reçus par match)', fontsize=12)
ax.set_ylabel('Gardien', fontsize=12)
ax.set_title('Les meilleurs gardiens', fontsize=14)

# Afficher le graphique
# 🎯 Affichage centré
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.pyplot(fig)


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
selected_player1 = st.selectbox("Sélectionner un gardien", gks, key="first_gk")

# Chargement des performances du premier joueur
gk_stats1 = players_loader.goalkeeper_performance(selected_player1)

# Bouton pour activer la comparaison
if st.button("Comparer avec un autre gardien"):
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












# Titre principal
#st.title("⚽ Football Statistics Dashboard")





