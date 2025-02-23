import streamlit as st
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.visualization.pitch import PitchVisualizer  
from src.visualization.charts import ChartCreator    

# Configuration de la page
st.set_page_config(page_title="Match Analysis", layout="wide")
st.title("Team Performance Analysis")

# Initialisation des classes
EVENTS_PATH = "Events"
loader = DataLoader(EVENTS_PATH)
processor = DataProcessor()

try:
    # Chargement des matches disponibles
    match_files = loader.load_match_files()
    
    # Sélection du match
    selected_match = st.selectbox(
        "Select Match",
        match_files,
        format_func=lambda x: x.replace('.csv', '')
    )
    
    # Chargement des données du match sélectionné
    df = loader.load_match_data(selected_match)
    teams = loader.get_teams(df)
    
    # Calcul des statistiques
    team_stats = processor.get_team_stats(df, teams)
    
    # Préparation des données pour les visualisations
    stats_data = {
        team: stats.to_dict() for team, stats in team_stats.items()
    }
    
    # Création du graphique des statistiques
    chart_creator = ChartCreator()
    stats_chart = chart_creator.create_centered_bar_chart(stats_data)
    st.plotly_chart(stats_chart, use_container_width=True)
    
    # Sélection de l'équipe
    selected_team = st.selectbox("Select Team", teams)
    
    # Choix du type de données à visualiser
    data_choice = st.radio("Choose Data to Visualize", ["Shots", "Passes"])
    
    # Sélection de la mi-temps
    half_choice = st.radio("Choose Half", [1, 2])
    
    # Calcul et sélection de la plage de temps
    max_minute = processor.get_max_minute(df, half_choice-1)
    selected_minute = st.slider("Select Time zone", 0, max_minute, 1)
    
    # Création de la visualisation du terrain
    pitch_viz = PitchVisualizer()
    if data_choice == "Shots":
        filtered_events = processor.get_events_by_time(
            df, selected_team, processor.shot_types, 
            selected_minute, half_choice - 1
        )
        pitch_plot = pitch_viz.create_shots_plot(filtered_events)
    else:
        filtered_events = processor.get_events_by_time(
            df, selected_team, processor.pass_types, 
            selected_minute, half_choice - 1
        )
        pitch_plot = pitch_viz.create_passes_plot(filtered_events)
    
    st.plotly_chart(pitch_plot, use_container_width=True)
    
    # Affichage des données brutes si demandé
    if st.checkbox("Show Raw Data"):
        st.dataframe(
            df[["Event Name", "Player1 Team", "Possession Loss"]]
            .style.highlight_null()
        )

except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)