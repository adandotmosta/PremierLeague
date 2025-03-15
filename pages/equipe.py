import streamlit as st
from src.data.loader import DataLoader
from src.data.playersLoader import PlayerLoader
from src.data.processor import DataProcessor
from src.visualization.pitch import PitchVisualizer  
from src.visualization.charts import ChartCreator  
    

# Initialisation des classes
PLAYERS_PATH = "../Players"
LOGOS_PATH = "Logos"
players_loader = PlayerLoader(PLAYERS_PATH)
processor = DataProcessor()
try:
    top_scorers = players_loader.get_top_scorers_yearly(10)

    # Create a markdown header for the top 10 scorers section
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>Top 10 Scorers in the The club</h2>", unsafe_allow_html=True)

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