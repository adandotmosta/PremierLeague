from typing import List
import os
import pandas as pd

class DataLoader:
    def __init__(self, events_directory: str):
        self.events_directory = events_directory

    def load_match_files(self) -> List[str]:
        """Liste tous les fichiers CSV dans le répertoire des événements."""
        return sorted([
            f for f in os.listdir(self.events_directory) 
            if f.endswith('.csv')
        ])

    def load_match_data(self, file_name: str) -> pd.DataFrame:
        """Charge les données d'un match spécifique."""
        file_path = os.path.join(self.events_directory, file_name)
        return pd.read_csv(file_path)

    def get_teams(self, data: pd.DataFrame) -> List[str]:
        """Récupère la liste des équipes du match."""
        return data["Player1 Team"].unique().tolist()