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
        """Récupère les statistiques d'une équipe spécifique, y compris les buts, le score xG et les minutes jouées."""
        players = {}
        wins = 0
        a_domicile = 0
        total_xg = 0  # Variable to accumulate total xG
        for match in self.load_match_files():
            if team in match:
                data = self.load_player_data(match + "- Players.csv")
                team_data = data[data['Team'] == team]
                home_team = match.split(" v ")[0].split()[-1]  # Get the last word before "v"
                away_team = match.split(" v ")[1].split()[0]  # Get the first word after "v"

                # Increment a_domicile if the team is the home team

                
                # Count wins
                if team_data.iloc[0]['Result'] == 'W':
                    wins += 1

                    if home_team == team:
                        a_domicile += 1
                
                # Iterate through the players' data
                for _, player in team_data.iterrows():
                    player_name = player['Player Name']
                    goals = player['Goals']
                    xg = player['xGoals Shot']  # Assuming 'xG' is a column in your dataset
                    minutes = player['Minutes Played']
                    
                    # Update player stats: goals, xG, and minutes played
                    if player_name in players:
                        players[player_name]['Goals'] += goals
                        players[player_name]['xG'] += xg
                        players[player_name]['Minutes Played'] += minutes
                    else:
                        players[player_name] = {'Goals': goals, 'xG': xg, 'Minutes Played': minutes}
                    
                    total_xg += xg  # Accumulate total xG for the team

        # Convert to DataFrame and include Minutes Played in the table
        player_stats = pd.DataFrame([(player, stats['Goals'], stats['xG'], stats['Minutes Played']) 
                                    for player, stats in players.items()],
                                    columns=['Player', 'Goals', 'xG', 'Minutes Played'])

        # Sort by goals
        player_stats = player_stats.sort_values(by='Goals', ascending=False)
        
        # Return both player stats and the total wins, total xG
        return player_stats, wins, total_xg,a_domicile


    def evolutionary_stat(self, player_name, team_name):
        """
        Returns the evolution of the player's stats over time.
        
        Args:
        - player_name (str): Name of the player
        - team_name (str): Name of the team
        
        Returns:
        - DataFrame containing the player's stats over time
        """
        # Load match files
        files = self.load_match_files()
        
        # Initialize an empty list to accumulate the player's stats over time
        player_stats = []
        
        # Iterate through each match to accumulate the player's stats
        for match in files:
            if team_name in match:
                # Load player data for the current match
                data = self.load_player_data(match + "- Players.csv")
                
                # Filter data to get the player's stats
                player_data = data[data['Player Name'] == player_name]
              
                if not player_data.empty:
                    goals = player_data['Goals'].values[0]
                    xg = player_data['xGoals Shot'].values[0]
                    minutes = player_data['Minutes Played'].values[0]
                    
                    # Append the player's stats for the match to the list
                    player_stats.append({'Match': match, 'Goals': goals, 'xG': xg, 'Minutes Played': minutes})
        
        # Convert the list of stats into a DataFrame
        player_stats_df = pd.DataFrame(player_stats)
        
        return player_stats_df

    def evolution_by_month_match(self, player_name, team_name, aggregation="month"):
        # Retrieve the player's stats over time
        df = self.evolutionary_stat(player_name, team_name)

        # Custom month order (from August to May)
        month_order = [
            "August", "September", "October", "November", "December", 
            "January", "February", "March", "April", "May"
        ]
        
        if aggregation == "month":
            try:
                # Extract the date part from the match names (e.g., "12.03.12" from "12.03.12 Arsenal v Newcastle United")
                df["Match"] = df["Match"].str.extract(r"(\d{2}\.\d{2}\.\d{2})")[0]

                # Convert the extracted date into a datetime object
                df["Match"] = pd.to_datetime(df["Match"], format="%d.%m.%y")

                # Extract only the month in full name (e.g., "January", "February")
                df["month"] = df["Match"].dt.strftime("%B")  # Full month name

                # Set the custom order for months
                df["month"] = pd.Categorical(df["month"], categories=month_order, ordered=True)

                # Select only the numeric columns for aggregation
                numeric_cols = df.select_dtypes(include=["number"]).columns
                df = df.groupby("month")[numeric_cols].sum().reset_index()

                # Return the aggregated dataframe
                return df
            except Exception as e:
                # Print the error message if aggregation fails
                print("Error during aggregation:", e)
                return df

        elif aggregation == "match":
            # Return the stats without aggregation
            return df












def extract_home_away_teams(match_str: str):

    # Remove the date at the beginning of the string using regex
    match_str_cleaned = re.sub(r'^\d{2}\.\d{2}\.\d{2,4} ', '', match_str.split(" -")[0])  # Removing the date part
    
    # Split the cleaned string based on ' v '
    match_split = match_str_cleaned.split(" v ")
    
    if len(match_split) == 2:
        home_team = match_split[0].strip()  # Home team
        away_team = match_split[1].strip()  # Away team
        return home_team, away_team