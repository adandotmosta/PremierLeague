from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class MatchStats:
    shots: int
    passes: int
    successful_passes: int
    saves : int
    score : int

    @property
    def successful_passes_rate(self) -> float:
        return (self.successful_passes / self.passes) * 100 if self.passes > 0 else 0

    def to_dict(self) -> Dict[str, float]:
        return {
            "shots": self.shots,
            "passes": self.passes,
            "successful_passes_rate": self.successful_passes_rate,
            "saves" : self.saves,
            "score" : self.score
        }
    
class MatchStatsRanking:
    points : int
    wins : int
    draw : int
    lose : int
    bp : int
    bc : int
    db : int
    mj : int

class DataProcessor:
    def __init__(self):
        self.shot_types = {
            "Shot", "Direct Free Kick Cross", "Header shot"
        }
        self.pass_types = {
            "Pass", "Cross", "Corner Pass", "Clearance",
            "Direct Free Kick Pass", "Goal Kick",
            "GoalKeeper kick", "Indirect Free Kick Pass"
        }
        self.saves_types = {
            "Goalkeeper Save", "Goalkeeper Save Catch"
        }

        self.activity_types = {
            'Pass', 'Touch', 'Tackle', 'Block', 'Dribble','Throw In', 'Header', 'Clearance', 'Cross',
            'Goal Kick', 'Goalkeeper Pick Up', 'Goalkeeper Kick', 'Shot',
            'Goalkeeper Save', 'Corner Pass', 'Goal', 'Goalkeeper Throw','Direct Free Kick Pass',
            'Goalkeeper Save Catch', 'Corner Cross', 'Header Shot',
            'Goalkeeper Catch', 'Goalkeeper Punch', 'Direct Free Kick Shot','Penalty Shot'
        }

    def get_events_types(self, data_choice):
        if data_choice == "Shots":
            return self.shot_types
        if data_choice == "Passes":
            return self.pass_types
        if data_choice == "Activity map":
            return self.activity_types

    def calculate_shots(self, data: pd.DataFrame, team: str) -> int:
        """Calcule le nombre de tirs pour une équipe."""
        return len(data[
            data["Event Name"].isin(self.shot_types) & 
            (data["Player1 Team"] == team)
        ])

    def calculate_passes(self, data: pd.DataFrame, team: str) -> int:
        """Calcule le nombre total de passes pour une équipe."""
        return len(data[
            data["Event Name"].isin(self.pass_types) & 
            (data["Player1 Team"] == team)
        ])
    
    def calculate_saves(self, data: pd.DataFrame, team: str) -> int:
        """Calcule le nombre de tirs pour une équipe."""
        return len(data[
            data["Event Name"].isin(self.saves_types) & 
            (data["Player1 Team"] == team)
        ])

    def calculate_possession_loss(self, data: pd.DataFrame, team: str) -> int:
        """Calcule le nombre de pertes de possession."""
        return len(data[
            data["Event Name"].isin(self.pass_types) & 
            (data["Player1 Team"] == team) & 
            data["Possession Loss"]
        ])

    def calculate_successful_passes(self, data: pd.DataFrame, team: str) -> int:
        """Calcule le nombre de passes réussies."""
        return len(data[
            data["Event Name"].isin(self.pass_types) & 
            (data["Player1 Team"] == team) & 
            (~data["Possession Loss"])
        ])

    def get_team_stats(self, data: pd.DataFrame, teams: List[str]) -> Dict[str, MatchStats]:
        """Calcule toutes les statistiques pour chaque équipe."""
        return {
            team: MatchStats(
                shots=self.calculate_shots(data, team),
                passes=self.calculate_passes(data, team),
                successful_passes=self.calculate_successful_passes(data, team),
                saves=self.calculate_saves(data, team),
                score = self.calculate_final_score(data, team)
            ) for team in teams
        }

    def get_events_vector_by_time(self, data: pd.DataFrame, players: list[str], 
                  event_types: set, minutes: int = 90, ) -> pd.DataFrame:
        seconds = minutes * 60
        
        # Créer une copie pour ne pas modifier le DataFrame original
        data_copy = data.copy()
        
        # Ajuster le temps pour que la 2ème mi-temps continue après la 1ère
        # Trouver le temps maximum de la 1ère mi-temps
        if 0 in data_copy["Half"].unique() and 1 in data_copy["Half"].unique():
            max_time_first_half = data_copy[data_copy["Half"] == 0]["Time"].max()
            
            # Ajouter ce temps à toutes les valeurs de la 2ème mi-temps
            data_copy.loc[data_copy["Half"] == 1, "Time"] = data_copy.loc[data_copy["Half"] == 1, "Time"] + max_time_first_half
        
        # Trier le DataFrame par temps ajusté
        data_sorted = data_copy.sort_values("Time")
        
        # Ajouter un index qui nous servira à trouver l'événement suivant
        data_sorted = data_sorted.reset_index(drop=True)
        
        # Construire le masque de filtrage
        mask = (
            (data_sorted["Event Name"].isin(event_types)) & 
            (data_sorted["Player1 Name"].isin(players)) & 
            (data_sorted["Time"] <= seconds)
        )
        
        # Obtenir les indices des événements qui nous intéressent
        filtered_indices = data_sorted[mask].index
        
        # Créer le DataFrame filtré
        filtered_df = data_sorted.loc[filtered_indices].copy()
        
        # Pour chaque événement filtré, trouver les coordonnées du prochain événement
        # dans le jeu de données complet
        filtered_df["end_x"] = filtered_indices.map(
            lambda idx: data_sorted.loc[idx + 1, "X"] if idx + 1 in data_sorted.index else data_sorted.loc[idx, "X"]
        )
        filtered_df["end_y"] = filtered_indices.map(
            lambda idx: data_sorted.loc[idx + 1, "Y"] if idx + 1 in data_sorted.index else data_sorted.loc[idx, "Y"]
        )
        
        return filtered_df
    
    def get_events_point_by_time(self, data: pd.DataFrame, players: list[str], 
                      event_types: set, minutes: int = 90, ) -> pd.DataFrame:
        
        seconds = minutes * 60
        
        # Créer une copie pour ne pas modifier le DataFrame original
        data_copy = data.copy()
        
        # Ajuster le temps pour que la 2ème mi-temps continue après la 1ère
        # Trouver le temps maximum de la 1ère mi-temps
        if 1 in data_copy["Half"].unique() and 2 in data_copy["Half"].unique():
            max_time_first_half = data_copy[data_copy["Half"] == 1]["Time"].max()
            
            # Ajouter ce temps à toutes les valeurs de la 2ème mi-temps
            data_copy.loc[data_copy["Half"] == 2, "Time"] = data_copy.loc[data_copy["Half"] == 2, "Time"] + max_time_first_half
        
        # Trier le DataFrame par temps ajusté
        data_sorted = data_copy.sort_values("Time")
        
        # Ajouter un index qui nous servira à trouver l'événement suivant
        data_sorted = data_sorted.reset_index(drop=True)
        
        # Filtrer les événements selon les critères
        mask = (
            (data_sorted["Event Name"].isin(event_types)) & 
            (data_sorted["Player1 Name"].isin(players)) & 
            (data_sorted["Time"] <= seconds)
        )
        
        # Obtenir les indices des événements qui nous intéressent
        filtered_indices = data_sorted[mask].index
        
        # Créer le DataFrame filtré
        filtered_df = data_sorted.loc[filtered_indices].copy()
        
        return filtered_df

    def get_max_minute(self, data: pd.DataFrame) -> int:
        # Calculer le temps total des deux mi-temps
        # D'abord, trouver le temps maximum pour chaque mi-temps
        max_time_half1 = data[data["Half"] == 0]["Time"].max() if 0 in data["Half"].values else 0
        max_time_half2 = data[data["Half"] == 1]["Time"].max() if 1 in data["Half"].values else 0
        
        # Calculer le temps total en minutes
        total_minutes = int((max_time_half1 + max_time_half2) / 60) + 1
        
        return total_minutes
    
    def calculate_final_score(self, data: pd.DataFrame, team):
        return len(data[(data["Event Name"]=="Goal") & (data["Player1 Team"] == team)])
    
    def get_players(self, data: pd.DataFrame, teams) -> pd.DataFrame:
        result = {}
        
        for team in teams:
            filtered_data = data[data['Player1 Team'] == team]['Player1 Name'].unique()
            result[team] = list(filtered_data)
        
        players_df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in result.items()]))
        
        return players_df



    def get_goal_scorers(self, players: pd.DataFrame, match: pd.DataFrame, team: str) -> List[tuple]:
        """Récupère les noms des joueurs ayant marqué un but et le nombre de buts."""

        # Filter players who scored goals for the given team
        scorers = players[
            (players["Goals"] > 0) & 
            (players["Team"] == team)
        ][["Player Name"]].values.tolist()

        returned_tuples = []

        for scorer in scorers:
            # Find the goal events for the scorer
            goal_minutes = match[
                (match["Player1 Name"] == scorer[0]) & 
                (match["Event Name"] == "Goal")
            ][["Time", "Half"]].values.tolist()

            minutes = []
            
            for goal in goal_minutes:
                # Adjust time based on half
                goal_time = goal[0]/60 if goal[1] == 0 else goal[0]/60 + 45
                minutes.append(goal_time)
                
            returned_tuples.append((scorer[0], minutes))

        returned_tuples.sort(key=lambda x: x[1][0])

        return returned_tuples


    def get_top_scorers_yearly(self, players: pd.DataFrame,top_n : 10) -> List[tuple]:
        """Récupère les noms des joueurs ayant marqué le plus de buts par année.""" 
        # Filter players who scored goals for the given team
        return


    def Missed_oppurtunities(self, match: pd.DataFrame, team: str) -> List[tuple]:
        # filter if there is a post shot
        # if there is shot with a high XgG but no goal after it, it is a missed oppurtunity
        # return the player name and the time of the missed oppurtunity and label(missed shot)
        #if there is post look before it if there is a shot, then return the player name and the time of the post shot and label(post shot)
        # penalty = xg higher than 0.7
        # shot inside the box = xg higher than 0.5

        missed_oppurtunities = match[
            (match["Event Name"] == "Shot") & 
            (match["Player1 Team"] == team) & 
            (match["Goal"] == False) &
            (match["XgG"] > 0.3)
        ][["Player1 Name", "Time"]].values.tolist()


    def get_player_names(self,team):
        players_df = pd.read_csv("players_performance.csv")


        return players_df[(players_df["Team"] == team) & (players_df["DP Passes Made"] <= 0.3)]["Player Name"].unique().tolist()

    def get_player_metrics(self,player_name):
        players_df = pd.read_csv("players_performance.csv")
        return players_df[(players_df["Player Name"] == player_name)]





    


