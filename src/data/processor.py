from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass

@dataclass
class MatchStats:
    shots: int
    passes: int
    possession_loss: int
    successful_passes: int

    @property
    def successful_passes_rate(self) -> float:
        return (self.successful_passes / self.passes) * 100 if self.passes > 0 else 0

    def to_dict(self) -> Dict[str, float]:
        return {
            "shots": self.shots,
            "passes": self.passes,
            "possession_loss": self.possession_loss,
            "successful_passes_rate": self.successful_passes_rate
        }

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
                possession_loss=self.calculate_possession_loss(data, team),
                successful_passes=self.calculate_successful_passes(data, team)
            ) for team in teams
        }

    def get_events_by_time(self, data: pd.DataFrame, team: str, 
                          event_types: set, minutes: int = 90, 
                          half: int = 0) -> pd.DataFrame:
        """Filtre les événements par équipe, type et temps."""
        seconds = minutes * 60
        return data[
            (data["Event Name"].isin(event_types)) & 
            (data["Player1 Team"] == team) & 
            (data["Time"] <= seconds) & 
            (data["Half"] == half)
        ]

    def get_max_minute(self, data: pd.DataFrame, half: int) -> int:
        """Calcule la dernière minute de jeu pour une mi-temps donnée."""
        return int(data[data["Half"] == half].iloc[-1]["Time"] / 60) + 1