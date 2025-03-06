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
LOGOS_PATH = "Logos"
loader = DataLoader(EVENTS_PATH, LOGOS_PATH)
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
    logo_team1 = loader.load_logos(teams[0])
    logo_team2 = loader.load_logos(teams[1])
    

    # Calcul des statistiques
    team_stats = processor.get_team_stats(df, teams)

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
    
    # Chargement des effectifs
    players = processor.get_players(df, teams)
    # Séparation des joueurs en deux tableaux
    team1, team2 = players.columns
    players_team1 = players[[team1]].dropna()
    players_team2 = players[[team2]].dropna()

    # Séparation en titulaires et remplaçants
    Team1_titu = players_team1.head(11)
    Team2_titu = players_team2.head(11)
    Team1_sub = players_team1.iloc[11:]
    Team2_sub = players_team2.iloc[11:]

    # Sélection des joueurs avec checkboxes en affichant les équipes en parallèle
    selected_players = []

    col1, col2, col3 = st.columns([1, 2, 1], border=True)

    with col1:

        st.write(f"## {team1}")

        team1_selections = []

        # Checkbox pour sélectionner toute l'équipe
        select_all_team1 = st.checkbox(f"Sélectionner toute l'équipe.", key=f"{team1}select_all")
        
        with st.container(border=True):

            st.write(f"### Titulaires")

            for player in Team1_titu[team1].dropna():
                if st.checkbox(player, key=f"{team1}_titu_{player}"):
                    team1_selections.append(player)
            
            st.write(f"### Remplaçants")
            for player in Team1_sub[team1].dropna():
                if st.checkbox(player, key=f"{team1}_sub_{player}"):
                    team1_selections.append(player)

            if select_all_team1:
                all_team1_players = list(Team1_titu[team1].dropna()) + list(Team1_sub[team1].dropna())
                for player in all_team1_players:
                    if player not in team1_selections:
                        team1_selections.append(player)
    
    with col3:
        st.write(f"## {team2}")

        team2_selections = []
        
        # Checkbox pour sélectionner toute l'équipe
        select_all_team2 = st.checkbox(f"Sélectionner toute l'équipe.", key=f"{team2}select_all")
        
        with st.container(border=True):
            st.write(f"### Titulaires")

            for player in Team2_titu[team2].dropna():
                player_selected = st.checkbox(player, key=f"{team2}_titu_{player}", value=select_all_team2)
                if player_selected and player not in team2_selections:
                    team2_selections.append(player)
            
            st.write(f"### Remplaçants")
            for player in Team2_sub[team2].dropna():
                player_selected = st.checkbox(player, key=f"{team2}_sub_{player}", value=select_all_team2)
                if player_selected and player not in team2_selections:
                    team2_selections.append(player)

            if select_all_team2:
                all_team2_players = list(Team2_titu[team2].dropna()) + list(Team2_sub[team2].dropna())
                for player in all_team2_players:
                    if player not in team2_selections:
                        team2_selections.append(player)
    
    selected_players = (team1_selections + team2_selections)

    with col2:

        # Selection de la visualisation
        data_choice = st.selectbox("Choose Data to Visualize", ["Shots", "Passes", "Activity map"])
        
        # Calcul et sélection de la plage de temps
        max_minute = processor.get_max_minute(df)
        print(max_minute)
        selected_minute = st.slider("Select Time zone", 0, max_minute, 1)

        # Création de la visualisation du terrain
        pitch_viz = PitchVisualizer()

        events_type = processor.get_events_types(data_choice)
        
        if data_choice in (['Shots', 'Passes']):
            filtered_events = processor.get_events_vector_by_time(
                df, selected_players, events_type,
                selected_minute
            )
            pitch_plot = pitch_viz.create_vector_plot(filtered_events, data_choice)
        else :
            filtered_events = processor.get_events_point_by_time(
                df, selected_players, events_type,
                selected_minute
            )    
            pitch_plot = pitch_viz.create_point_plot(filtered_events, data_choice)
    
        st.plotly_chart(pitch_plot, use_container_width=True)

except Exception as e:
    st.error(f"Error occurred: {str(e)}")
    st.exception(e)