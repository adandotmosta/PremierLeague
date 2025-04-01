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



    def get_angle_xg(self) -> pd.DataFrame:
        """Calcule l'angle de tir et le xG pour chaque événement."""
        df_shots = pd.read_csv("shots.csv")
        df_shots["TotalShots"] = 1
        df_shots_aggregated_by_player = df_shots.groupby(["playerName", "playerTeam"]).agg({"xG Score": "sum", "Angle": "mean","TotalShots" :"sum"}).reset_index()
        top_scorers = ["Robin VAN PERSIE", "Wayne ROONEY", "Sergio AGUERO", "Clint DEMPSEY", "Emmanuel ADEBAYOR", "Demba BA", "Yakubu AYEGBENI", "Grant HOLT", "Edin DZEKO", "Mario BALOTELLI"]
        df_shots_aggregated_by_player_shots = df_shots_aggregated_by_player[df_shots_aggregated_by_player["TotalShots"] >50]
        df_shots_aggregated_by_player_shots["color"] = df_shots_aggregated_by_player["playerName"].apply(
        lambda x: "red" if x in top_scorers else "blue"
)
        return df_shots_aggregated_by_player_shots
    def get_angle_bins(self) :
        df_shots_aggregated_by_player_shots = self.get_angle_xg()
        df_shots_aggregated_by_player_shots["AngleBins"] = pd.cut(df_shots_aggregated_by_player_shots["Angle"], bins=20)
        df_shots_aggregated_by_bins = df_shots_aggregated_by_player_shots.groupby("AngleBins") \
            .agg({"xG Score": "mean"}) \
            .reset_index()

        # Rename column for clarity
        df_shots_aggregated_by_bins.rename(columns={"xG Score": "Total_xG"}, inplace=True)

        return df_shots_aggregated_by_bins
