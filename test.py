import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import os
from typing import Dict, List
from dataclasses import dataclass
import plotly.graph_objs as go

@dataclass
class MatchStats:
    shots: int
    passes: int
st.set_page_config(page_title="Match Analysis", layout="wide")

def load_match_files(directory: str) -> List[str]:
    return sorted([f for f in os.listdir(directory) if f.endswith('.csv')])

def load_match_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def calculate_shots(data: pd.DataFrame, team: str) -> int:
    shot_types = {"Shot", "Direct Free Kick Cross", "Header shot"}
    return len(data[data["Event Name"].isin(shot_types) & (data["Player1 Team"] == team)])

def calculate_passes(data: pd.DataFrame, team: str) -> int:
    pass_types = {
        "Pass", "Cross", "Corner Pass", "Clearance", 
        "Direct Free Kick Pass", "Goal Kick", 
        "GoalKeeper kick", "Indirect Free Kick Pass"
    }
    return len(data[
        data["Event Name"].isin(pass_types) & 
        (data["Player1 Team"] == team) & 
        (~data["Possession Loss"])
    ])

def create_centered_bar_chart_with_fixed_scale(shots_data: pd.DataFrame, passes_data: pd.DataFrame) -> go.Figure:
    # Fonction pour normaliser les valeurs
    def normalize_to_fixed_scale(data: pd.DataFrame, total_width: int = 100) -> pd.DataFrame:
        max_value = max(data["Count"])
        data["Normalized Count"] = data["Count"] / max_value * (total_width / 2)  # Divisé par 2 pour centrer
        return data

    # Normaliser les tirs et les passes
    shots_data = normalize_to_fixed_scale(shots_data)
    passes_data = normalize_to_fixed_scale(passes_data)

    fig = go.Figure()

    # Ajouter les barres pour les tirs
    fig.add_trace(go.Bar(
        y=["Shots"] * len(shots_data),  # Catégorie Shots
        x=[-val / 2 if idx == 0 else val/2 for idx, val in enumerate(shots_data["Normalized Count"])],
        name="Shots",
        orientation="h",
        marker=dict(color=['blue', 'red']),  # Couleur par équipe
        text=shots_data["Team"] + ": " + shots_data["Count"].astype(str),
        textposition='inside'
    ))

    # Ajouter les barres pour les passes
    fig.add_trace(go.Bar(
        y=["Passes"] * len(passes_data),  # Catégorie Passes
        x=[-val /2 if idx == 0 else val /2 for idx, val in enumerate(passes_data["Normalized Count"])],
        name="Passes",
        orientation="h",
        marker=dict(color=['blue', 'red']),  # Couleur par équipe
        text=passes_data["Team"] + ": " + passes_data["Count"].astype(str),
        textposition='inside'
    ))

    # Ajustement des axes pour centrer
    fig.update_layout(
        title="Centered Comparison of Shots and Passes",
        xaxis_title="Normalized Count",
        yaxis_title=None,
        xaxis=dict(
            range=[-50, 50],  # La plage totale de l'axe des X est toujours fixée à 100
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=2,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            automargin=True
        ),
        barmode="relative",  # Les barres restent alignées
        template="plotly",
        height=400,
        width=700,  # Largeur bien équilibrée
        legend=dict(orientation="h", y=-0.2, xanchor="center", x=0.5)  # Légende centrée
    )

    return fig


def create_stats_chart(data: pd.DataFrame, title: str) -> px.bar:
    return px.bar(
        data,
        x="Team",
        y="Count",
        color="Team",
        title=title,
        template="plotly_dark"
    )
    
def get_team_stats(df: pd.DataFrame, teams: List[str]) -> Dict[str, MatchStats]:
    return {
        team: MatchStats(
            shots=calculate_shots(df, team),
            passes=calculate_passes(df, team)
        ) for team in teams
    }

def shots_locations(data, team):
    shot_types = {
        "Shot", "Direct Free Kick Cross", "Header shot"
    }

    shots_list = []

    for i in range(len(data)):
        current_event = data.iloc[i]

        if current_event["Event Name"] in shot_types and current_event["Player1 Team"] == team:
            start_x = current_event["X"]
            start_y = current_event["Y"]

            # Pour les tirs, supposons que les coordonnées d'arrivée (cible) sont le centre du but
            if current_event["Half"] == 1:
                start_x = - start_x
                start_y = - start_y

            shots_list.append({
                "Event Name": current_event["Event Name"],
                "Half": current_event["Half"],
                "Time": current_event["Time"],
                "Player1 Name": current_event["Player1 Name"],
                "Player1 Team": current_event["Player1 Team"],
                "Start X": start_x,
                "Start Y": start_y,
            })

    return pd.DataFrame(shots_list)


def create_shots_plot(shots_df):

    # Transformation des coordonnées
    shots_df['Start X'] = shots_df['Start X'] + 53
    shots_df['Start Y'] = shots_df['Start Y'] + 34.5

    shots_df['Start X'] = shots_df['Start X'] * (100 / 105.8)
    shots_df['Start Y'] = shots_df['Start Y'] * (100 / 68)

    # Create the pitch figure
    fig = go.Figure()

    # Pitch background
    fig.add_shape(
        type="rect",
        x0=1, y0=0, x1=99, y1=100,
        line=dict(color="white"),
        fillcolor="rgb(0, 32, 110)",
        layer="below"
    )

    # Midline
    fig.add_shape(
        type="line",
        x0=50, y0=0, x1=50, y1=100,
        line=dict(color="white", width=2),
        layer="below"
    )

    # Penalty and goal areas
    surfaces = [
        {"x0": 1, "y0": 22, "x1": 16, "y1": 78},  # Left penalty area
        {"x0": 84, "y0": 22, "x1": 99, "y1": 78}  # Right penalty area
    ]

    for surface in surfaces:
        fig.add_shape(
            type="rect",
            x0=surface["x0"], y0=surface["y0"],
            x1=surface["x1"], y1=surface["y1"],
            line=dict(color="white"),
            layer="below"
        )

    # Shot start locations
    fig.add_trace(go.Scatter(
        x=np.clip(shots_df['Start X'], 0, 100),
        y=np.clip(shots_df['Start Y'], 0, 100),
        mode='markers',
        marker=dict(
            size=8,
            color=shots_df['Half'].map({1: 'yellow', 0: 'green'}),
            opacity=0.7
        ),
        text=shots_df['Player1 Name'] + '<br>Half: ' + shots_df['Half'].astype(str) + '<br>Time: ' + shots_df['Time'].astype(str) + '<br>Event: ' + shots_df['Event Name'],
        hoverinfo='text'
    ))

    # Update layout for visualization
    fig.update_layout(
        title='Shot Locations',
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        width=800,
        height=600,
        plot_bgcolor='green',
        paper_bgcolor='white'
    )

    return fig

def passes_locations(data, team):
    pass_types = {
        "Pass", "Cross"
    }

    passes_list = []
    
    for i in range(len(data) - 1):
        current_event = data.iloc[i]
        next_event = data.iloc[i + 1]
        
        if current_event["Event Name"] in pass_types and current_event["Player1 Team"] == team and current_event["Possession Loss"] == False:

            start_x = current_event["X"]
            start_y = current_event["Y"]
            end_x = next_event["X"]
            end_y = next_event["Y"]

            if current_event["Half"] == 0:
                start_x = - start_x
                start_y = - start_y
                end_x = - end_x
                end_y = - end_y
            
            passes_list.append({
                "Event Name": current_event["Event Name"],
                "Half": current_event["Half"],
                "Time": current_event["Time"],
                "Player1 Name": current_event["Player1 Name"],
                "Player1 Team": current_event["Player1 Team"],
                "Start X": start_x,
                "Start Y": start_y,
                "End X": end_x,
                "End Y": end_y,
            })
    
    return pd.DataFrame(passes_list)

def create_pitch_plot(passes_df):

    passes_df['Start X'] = passes_df['Start X'] + 53
    passes_df['End X'] = passes_df['End X'] + 53
    passes_df['Start Y'] = passes_df['Start Y'] + 34.5
    passes_df['End Y'] = passes_df['End Y'] + 34.5

    # Transformation des coordonnées (si nécessaire)

    passes_df['Start X'] = passes_df['Start X'] * (100 / 105.8)
    passes_df['End X'] = passes_df['End X'] * (100 / 105.8)
    passes_df['Start Y'] = passes_df['Start Y'] * (100 / 68)
    passes_df['End Y'] = passes_df['End Y'] * (100 / 68)

    # Create the pitch figure
    fig = go.Figure()

    # Pitch background (adjust to fit the proportions)
    fig.add_shape(
        type="rect",
        x0=1, y0=0, x1=99.5, y1=100,
        line=dict(color="white"),
        fillcolor= "blue",
        layer="below"  # Ensure the background is below all other elements
    )

    # Midline
    fig.add_shape(
        type="line",
        x0=50, y0=0, x1=50, y1=100,
        line=dict(color="white", width=2),
        layer="below"
    )

    # Penalty and goal areas
    surfaces = [
        {"x0": 1, "y0": 22, "x1": 16, "y1": 78},  # Left penalty area
        {"x0": 84, "y0": 22, "x1": 99, "y1": 78}  # Right penalty area
    ]

    for surface in surfaces:
        fig.add_shape(
            type="rect",
            x0=surface["x0"], y0=surface["y0"], 
            x1=surface["x1"], y1=surface["y1"],
            line=dict(color="white"),
            layer="below"
        )

    # Pass start locations
    fig.add_trace(go.Scatter(
        x=np.clip(passes_df['Start X'], 0, 100),
        y=np.clip(passes_df['Start Y'], 0, 100),
        mode='markers',
        marker=dict(
            size=7,
            color=passes_df['Half'].map({1: 'blue', 0: 'red'}),
            opacity=0.7
        ),
        text=passes_df['Player1 Name'] + '<br>Half' + passes_df['Half'].astype(str) + '<br>Time: ' + passes_df['Time'].astype(str) + '<br>Event:' + passes_df['Event Name'],
        hoverinfo='text'
    ))

    # Pass direction arrows
    for _, row in passes_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[np.clip(row['Start X'], 0, 100), np.clip(row['End X'], 0, 100)],
            y=[np.clip(row['Start Y'], 0, 100), np.clip(row['End Y'], 0, 100)],
            mode='lines',
            line=dict(width=2, color='white'),
            hoverinfo='none'
        ))

    # Update layout for proper visualization
    fig.update_layout(
        title='Pass Locations',
        xaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True  # Prevent zooming
        ),
        yaxis=dict(
            range=[0, 100],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        width=800,
        height=600,
        plot_bgcolor='green',
        paper_bgcolor='white'
    )

    return fig


st.title("Team Performance Analysis")

EVENTS_PATH = "C:/Users/remis/Documents/L3/projet/EPL_2011-12/Events"

try:
    match_files = load_match_files(EVENTS_PATH)
    
    selected_match = st.selectbox(
        "Select Match",
        match_files,
        format_func=lambda x: x.replace('.csv', '')
    )
    
    df = load_match_data(os.path.join(EVENTS_PATH, selected_match))
    teams = df["Player1 Team"].unique()
    team_stats = get_team_stats(df, teams)
    
    # Préparer les données pour les tirs et les passes
    shots_df = pd.DataFrame([
        {"Team": team, "Count": stats.shots}
        for team, stats in team_stats.items()
    ])

    passes_df = pd.DataFrame([
        {"Team": team, "Count": stats.passes}
        for team, stats in team_stats.items()
    ])
    
    # Créer le graphique combiné centré avec une échelle fixe
    centered_bar_chart = create_centered_bar_chart_with_fixed_scale(shots_df, passes_df)
    st.plotly_chart(centered_bar_chart, use_container_width=True)
    
    # Sélection de l'équipe
    selected_team = st.selectbox("Select Team", teams)
    
    # Choisir entre les tirs et les passes pour la visualisation
    data_choice = st.radio("Choose Data to Visualize", ["Shots", "Passes"])

    if data_choice == "Shots":
        shots_df = shots_locations(df, selected_team)
        pitch_plot = create_shots_plot(shots_df)
    else:
        passes_df = passes_locations(df, selected_team)
        pitch_plot = create_pitch_plot(passes_df)

    st.plotly_chart(pitch_plot, use_container_width=True)

    if st.checkbox("Show Raw Data"):
        st.dataframe(
            df[["Event Name", "Player1 Team", "Possession Loss"]].style.highlight_null()
        )
except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)