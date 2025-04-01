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
    


def plot_radar_chart(player_row):
    """
    Génère un radar chart et l'affiche dans Streamlit.
    
    Parameters:
        player_row (pd.Series): Ligne contenant les données normalisées du joueur.
    """
    if player_row is None or player_row.empty:
        st.error("Données du joueur introuvables.")
        return

    # Sélection des attributs pertinents (déjà normalisés)
    selected_attributes = [
        "Goals", "DP Passes Made", "Cr Crosses Made",
        "CA Regains", "HP Regains",
        "ST Involvement", "BU Involvement", "Ma Involvement"
    ]

    # Extraction des valeurs du joueur
    player_values = player_row[selected_attributes].values.flatten()

    # Création des angles pour le radar chart
    angles = np.linspace(0, 2 * np.pi, len(selected_attributes), endpoint=False).tolist()
    values = np.concatenate((player_values, [player_values[0]]))  # Ferme le polygone
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.fill(angles, values, color='blue', alpha=0.4)
    ax.plot(angles, values, color='blue', linewidth=2)

    # Ajout des labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(selected_attributes, fontsize=10, rotation=30, ha='right')
    ax.set_yticklabels([])  # Masquer les valeurs des axes



    # Affichage dans Streamlit
    st.pyplot(fig)

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

    
    scorers, wins,_,a_domicile = players_loader.get_stats_per_team(selected_team_name)
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
    losses = total_games - wins
    print(a_domicile)
    print(wins)
    away_wins = wins - a_domicile

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
    home_wins = a_domicile

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


    # display the top3 players played the most games

    fig = px.pie(scorers, names="Player", values="Goals", 
             hole=0.3, title="🥇 Distribution des Buts des Joueurs")
    st.plotly_chart(fig)






    # prendre la liste des joueurs
    players = processor.get_player_names(selected_team_name)
    selected_player = st.selectbox("Select a player", players)
    player_stats = processor.get_player_metrics(selected_player)
    plot_radar_chart(player_stats)

    # chekbox, pour afficher si par match ou par mois
    # si par match, on affiche le nombre de buts par match
    # si par mois, on affiche le nombre de buts par mois
    # Display the aggregation options
    aggregation = st.selectbox("Aggregation", ["month", "match"])

    # Retrieve the evolutionary statistics based on the selected aggregation type
    evolutionary_stat = players_loader.evolution_by_month_match(selected_player, selected_team_name, aggregation=aggregation)

    # Display the table if data is available
    st.table(evolutionary_stat)

    if evolutionary_stat.empty:
        st.write("No data available for the player.")
    else:
        # Convert "month" to string for plotting
        if aggregation == "month":
            evolutionary_stat['match'] = evolutionary_stat['month'].astype(str)  # Ensure 'match' is a string (month)
        else:
            evolutionary_stat['match'] = evolutionary_stat['Match'].astype(str)  # If aggregation is "match", use 'match'

        # Add a column for the cumulative sum of goals
        evolutionary_stat['Cumulative Goals'] = evolutionary_stat['Goals']

        # Display the title for the graph
        st.markdown("<h3 style='text-align: center; font-weight: bold;'>Evolution of Cumulative Goals</h3>", unsafe_allow_html=True)
        
        # Plot the cumulative goals evolution using Plotly
        fig = px.line(evolutionary_stat, x='match', y='Cumulative Goals', 
                    title="Cumulative Goals Over Time", markers=True)

        # Update the layout of the graph
        fig.update_layout(xaxis_title="match", yaxis_title="Cumulative Goals")
        
        # Display the plot
        st.plotly_chart(fig)








except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)