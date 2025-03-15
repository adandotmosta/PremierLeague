import streamlit as st
from src.data.loader import DataLoader
from src.data.playersLoader import PlayerLoader
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import plotly.graph_objects as go
    

# Initialisation des classes
EVENTS_PATH = "../EPL 2011-12/Events"
LOGOS_PATH = "../EPL 2011-12/Logos"
PLAYERS_PATH = "../EPL 2011-12/Players"


events_loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
players_loader = PlayerLoader(PLAYERS_PATH)




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

    
    scorers, wins = players_loader.get_stats_per_team(selected_team_name)
    st.write(scorers)



    total_games = 38
    losses = total_games - wins

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

























    top_scorers = players_loader.get_top_scorers_yearly(10)

    # Create a markdown header for the top 10 scorers section
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>Top 10 Scorers in the The club</h2>", unsafe_allow_html=True)

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