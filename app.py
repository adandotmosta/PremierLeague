import streamlit as st
from src.data.loader import DataLoader
from src.data.playersLoader import PlayerLoader
from src.data.processor import DataProcessor
from src.visualization.pitch import PitchVisualizer  
from src.visualization.charts import ChartCreator    

# Configuration de la page
st.set_page_config(page_title="Match Analysis", layout="wide")
st.title("Team Performance Analysis")

# Initialisation des classes
EVENTS_PATH = "Events"
PLAYERS_PATH = "Players"
LOGOS_PATH = "Logos"
events_loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
players_loader = PlayerLoader(PLAYERS_PATH)
processor = DataProcessor()

try:
    # Chargement des matches disponibles
    match_files = events_loader.load_match_files()
    
    # Sélection du match
    selected_match = st.selectbox(
        "Select Match",
        match_files
    )
    
    # Chargement des données du match sélectionné
    df_events = events_loader.load_match_data(selected_match + "- Events.csv")
    df_players = players_loader.load_player_data(selected_match + "- Players.csv")
    teams = events_loader.get_teams(df_events)
    logo_team1 = events_loader.load_logos(teams[0])
    logo_team2 = events_loader.load_logos(teams[1])

    # Calcul des statistiques
    team_stats = processor.get_team_stats(df_events, teams)

    # Affichage du score finale et des logos
    col1, col2, col3 = st.columns([1, 1, 1],vertical_alignment= "center")

    with col1:
        if logo_team1 is not None:
            # Convertir l'image OpenCV en base64 avec correction BGR → RGB
            import base64
            import cv2
            
            # Convertir BGR en RGB
            rgb_image = cv2.cvtColor(logo_team1, cv2.COLOR_BGR2RGB)
            
            # Encoder l'image RGB en PNG
            success, encoded_image = cv2.imencode('.png', rgb_image)
            if success:
                base64_img = base64.b64encode(encoded_image).decode('utf-8')
                
                # Afficher l'image centrée avec HTML
                st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                        <img src="data:image/png;base64,{base64_img}" width="100">
                    </div>
                """, unsafe_allow_html=True)
        
        st.write(f"<h3 style='text-align: center;'>{teams[0]}</h3>", unsafe_allow_html=True)

    with col2:
        team1_score = team_stats[teams[0]].score if hasattr(team_stats[teams[0]], 'score') else 0
        team2_score = team_stats[teams[1]].score if hasattr(team_stats[teams[1]], 'score') else 0
        st.write(f"<h1 style='text-align: center;'>{team1_score} - {team2_score}</h1>", unsafe_allow_html=True)

    with col3:
        if logo_team2 is not None:
            # Convertir l'image OpenCV en base64 avec correction BGR → RGB
            import base64
            import cv2
            
            # Convertir BGR en RGB
            rgb_image = cv2.cvtColor(logo_team2, cv2.COLOR_BGR2RGB)
            
            # Encoder l'image RGB en PNG
            success, encoded_image = cv2.imencode('.png', rgb_image)
            if success:
                base64_img = base64.b64encode(encoded_image).decode('utf-8')
                
                # Afficher l'image centrée avec HTML
                st.markdown(f"""
                    <div style="display: flex; justify-content: center;">
                        <img src="data:image/png;base64,{base64_img}" width="100">
                    </div>
                """, unsafe_allow_html=True)
        
        st.write(f"<h3 style='text-align: center;'>{teams[1]}</h3>", unsafe_allow_html=True)
    
    # Préparation des données pour les visualisations
    stats_data = {
        team: stats.to_dict() for team, stats in team_stats.items()
    }

    # Création du graphique des statistiques
    chart_creator = ChartCreator()
    stats_chart = chart_creator.create_centered_bar_chart(stats_data)
    st.plotly_chart(stats_chart, use_container_width=True)

    # Get goal scorers for each team
    goal_scorers_team1 = processor.get_goal_scorers(df_players, df_events, teams[0])
    goal_scorers_team2 = processor.get_goal_scorers(df_players, df_events, teams[1])

    # Header for Goal Scorers
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>🎯 Goal Scorers</h2>", unsafe_allow_html=True)

    # Create two columns for the teams
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<h3 style='text-align: center; color: #3498db;'>{teams[0]}</h3>", unsafe_allow_html=True)
        if goal_scorers_team1:
            for scorer in goal_scorers_team1:
                # Create a formatted string for the goal times
                goal_times = ', '.join([f"{int(goal_time)}'" for goal_time in scorer[1]])
                st.markdown(f"""
                    <div style="
                        background-color: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 10px;
                        text-align: center;
                        font-size: 18px;
                        font-weight: bold;
                        color: #2c3e50;">
                        {scorer[0]}: {goal_times}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center; font-style: italic; color: gray;'>No goals</p>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<h3 style='text-align: center; color: #e74c3c;'>{teams[1]}</h3>", unsafe_allow_html=True)
        if goal_scorers_team2:
            for scorer in goal_scorers_team2:
                # Create a formatted string for the goal times
                goal_times = ', '.join([f"{int(goal_time)}'" for goal_time in scorer[1]])
                st.markdown(f"""
                    <div style="
                        background-color: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 10px;
                        text-align: center;
                        font-size: 18px;
                        font-weight: bold;
                        color: #2c3e50;">
                        {scorer[0]}: {goal_times}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align: center; font-style: italic; color: gray;'>No goals</p>", unsafe_allow_html=True)


    
    # Sélection de l'équipe
    selected_team = st.selectbox("Select Team", teams)
    
    # Choix du type de données à visualiser
    data_choice = st.radio("Choose Data to Visualize", ["Shots", "Passes"])
    
    # Sélection de la mi-temps
    half_choice = st.radio("Choose Half", [1, 2])
    
    # Calcul et sélection de la plage de temps
    max_minute = processor.get_max_minute(df_events, half_choice-1)
    selected_minute = st.slider("Select Time zone", 0, max_minute, 1)
    
    # Création de la visualisation du terrain
    pitch_viz = PitchVisualizer()
    if data_choice == "Shots":
        filtered_events = processor.get_events_by_time(
            df_events, selected_team, processor.shot_types, 
            selected_minute, half_choice - 1
        )
        pitch_plot = pitch_viz.create_shots_plot(filtered_events)
    else:
        filtered_events = processor.get_events_by_time(
            df_events, selected_team, processor.pass_types, 
            selected_minute, half_choice - 1
        )
        pitch_plot = pitch_viz.create_passes_plot(filtered_events)
    
    st.plotly_chart(pitch_plot, use_container_width=True)
    
    # Affichage des données brutes si demandé
    if st.checkbox("Show Raw Data"):
        st.dataframe(
            df_events[["Event Name", "Player1 Team", "Possession Loss"]]
            .style.highlight_null()
        )


    # 
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