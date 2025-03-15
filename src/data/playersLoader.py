from typing import List
import os
import pandas as pd
import cv2


class PlayerLoader:
    def __init__(self, players_directory: str):
        self.players_directory = players_directory

    def load_match_files(self) -> List[str]:
        """Liste tous les fichiers CSV dans le répertoire des événements."""
        return sorted([
            f.replace("- Players.csv", "").replace("- Events.csv", "") 
            for f in os.listdir(self.players_directory) if f.endswith('.csv')
        ])
    def load_player_data(self, file_name: str) -> pd.DataFrame:
        """Charge les données des joueurs pour un match spécifique."""
        file_path = os.path.join(self.players_directory, file_name)
        return pd.read_csv(file_path)


    def get_top_scorers_yearly(self, top_n: int) -> dict:
        """Récupère la liste des meilleurs buteurs de l'année avec leurs xG."""

        # Load match files
        files = self.load_match_files()  # Assuming 'self' context for 'load_match_files'
        
        # Load player data for each match
        matches = [self.load_player_data(file + "- Players.csv") for file in files]
        
        # Initialize a dictionary to store player names, goals, and xG counts
        players = {}

        # Iterate through each match to accumulate goals and xG per player
        for match in matches:
            for _, player in match.iterrows():  # Assuming match is a DataFrame
                player_name = player["Player Name"]
                goals = player["Goals"]
                xg = player["xGoals Shot"]

                if player_name in players:
                    players[player_name]["goals"] += goals  # Increment goal count
                    players[player_name]["xG"] += xg  # Increment xG count
                else:
                    players[player_name] = {"goals": goals, "xG": xg}  # Initialize player stats

        # Sort players by goal count (highest first)
        sorted_players = sorted(players.items(), key=lambda x: x[1]["goals"], reverse=True)
        
        # Return the top N players
        return dict(sorted_players[:top_n])



    def get_players(self, data: pd.DataFrame, team_name: str) -> List[str]:
        """Récupère la liste des joueurs d'une équipe spécifique."""
        return data[data["Team"] == team_name]["Player Name"].unique().tolist()


    def get_stats_per_team(self, team: str) -> pd.DataFrame:
        """Récupère les statistiques d'une équipe spécifique."""
        players = {}
        wins = 0
        for match in self.load_match_files():
            if team in match : 
                data = self.load_player_data(match + "- Players.csv")
                team_data = data[data['Team'] == team]
                if team_data.iloc[0]['Result'] == 'W':
                    wins += 1
                for _, player in team_data.iterrows():
                    player_name = player['Player Name']
                    goals = player['Goals']
                    if player_name in players:
                        players[player_name] += goals
                    else:
                        players[player_name] = goals
        return pd.DataFrame(players.items(), columns=['Player', 'Goals']).sort_values(by='Goals', ascending=False), wins

