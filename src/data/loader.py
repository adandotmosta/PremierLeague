from typing import List
import os
import pandas as pd
import cv2

class DataLoader:
    def __init__(self, events_directory: str, logos_directory):
        self.events_directory = events_directory
        self.logos_directory = logos_directory

    def load_match_files(self) -> List[str]:
        """Liste tous les fichiers CSV dans le répertoire des événements."""
        return sorted([
            f.replace("- Players.csv", "").replace("- Events.csv", "") 
            for f in os.listdir(self.events_directory) if f.endswith('.csv')
        ])
    
    def load_logos(self, team_name: str):
        """Charge le logo de l'équipe spécifiée."""
        file_path = os.path.join(self.logos_directory, team_name + ".jpg")
        img = cv2.imread(file_path)
        
        if img is not None:
            # Convertir BGR en RGB pour Streamlit
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return None
    


    def load_match_data(self, file_name: str) -> pd.DataFrame:
        """Charge les données d'un match spécifique."""
        file_path = os.path.join(self.events_directory, file_name)
        return pd.read_csv(file_path)

    def get_teams(self, data: pd.DataFrame) -> List[str]:
        """Récupère la liste des équipes du match."""
        return data["Player1 Team"].unique().tolist()

