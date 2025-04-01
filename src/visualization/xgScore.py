import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def visualise_correlation_by_player(df_shots_aggregated_by_player_shots):

    fig, ax = plt.subplots(figsize=(12, 8))

    sns.scatterplot(
        x="xG Score", 
        y="Angle", 
        data=df_shots_aggregated_by_player_shots, 
        hue="color", 
        palette={"red": "red", "blue": "blue"}, 
        legend=None, 
        ax=ax
    )

 
    handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Top Players'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Other Players')
    ]
    ax.legend(handles=handles, title="Player Categories", fontsize=14)


    ax.set_xlabel("xG Score", fontsize=16)
    ax.set_ylabel("Angle (degrees)", fontsize=16)
    ax.set_title("Shot Angle vs xG Score", fontsize=18)

 
    st.pyplot(fig)



def visualise_correlation_by_bins(df_shots_aggregated_by_bins):

    fig, ax = plt.subplots(figsize=(30, 20))

    sns.barplot(
        x="AngleBins", 
        y="Total_xG", 
        data=df_shots_aggregated_by_bins, 
        palette="viridis", 
        ax=ax
    )

 
    ax.set_xlabel("Angle Bins", fontsize=20)
    ax.set_ylabel("Total xG", fontsize=20)
    ax.set_title("Average xG Score by Angle Bins", fontsize=24)


    ax.tick_params(axis='x', labelsize=30, rotation=45) 
    ax.tick_params(axis='y', labelsize=30)


    st.pyplot(fig)

