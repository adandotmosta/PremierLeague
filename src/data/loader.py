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
            f for f in os.listdir(self.events_directory) 
            if f.endswith('.csv')
        ])
    
    def load_logos(self, team_name):
        """Charge le logo de l'équipe spécifiée."""
        # Convert team_name to string to handle potential float inputs
        team_name_str = str(team_name)
        
        file_path = os.path.join(self.logos_directory, team_name_str + ".jpg")
        
        try:
            img = cv2.imread(file_path)
            
            if img is not None:
                # Convertir BGR en RGB pour Streamlit
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                print(f"Logo not found for team: {team_name_str}")
                return None
        except Exception as e:
            print(f"Error loading logo for {team_name_str}: {e}")
            return None

    def load_match_data(self, file_name: str) -> pd.DataFrame:
        """Charge les données d'un match spécifique."""
        file_path = os.path.join(self.events_directory, file_name)
        return pd.read_csv(file_path)

    def get_teams(self, data: pd.DataFrame) -> List[str]:
        """Récupère la liste des équipes du match."""
        teams = [data['Team A'][0], data['Team B'][0]]
        return teams