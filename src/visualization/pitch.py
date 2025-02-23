import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict

class PitchVisualizer:
    def __init__(self):
        self.pitch_width = 100
        self.pitch_height = 100
        self.real_pitch_width = 105.8
        self.real_pitch_height = 68

    def _create_base_pitch(self, background_color: str = "rgb(0, 32, 110)") -> go.Figure:
        """Crée un terrain de base avec les lignes et surfaces."""
        fig = go.Figure()

        # Fond du terrain
        fig.add_shape(
            type="rect",
            x0=1, y0=0, x1=99, y1=100,
            line=dict(color="white"),
            fillcolor=background_color,
            layer="below"
        )

        # Ligne médiane
        fig.add_shape(
            type="line",
            x0=50, y0=0, x1=50, y1=100,
            line=dict(color="white", width=2),
            layer="below"
        )

        # Surfaces de réparation
        surfaces = [
            {"x0": 1, "y0": 22, "x1": 16, "y1": 78},  # Surface gauche
            {"x0": 84, "y0": 22, "x1": 99, "y1": 78}  # Surface droite
        ]

        for surface in surfaces:
            fig.add_shape(
                type="rect",
                x0=surface["x0"], y0=surface["y0"],
                x1=surface["x1"], y1=surface["y1"],
                line=dict(color="white"),
                layer="below"
            )

        return fig

    def _normalize_coordinates(self, x: float, y: float) -> tuple[float, float]:
        """Normalise les coordonnées du terrain réel vers l'affichage."""
        norm_x = (x + 53) * (self.pitch_width / self.real_pitch_width)
        norm_y = (y + 34.5) * (self.pitch_height / self.real_pitch_height)
        return np.clip(norm_x, 0, 100), np.clip(norm_y, 0, 100)

    def create_shots_plot(self, shots_df: pd.DataFrame) -> go.Figure:
        """Crée une visualisation des tirs sur le terrain."""
        fig = self._create_base_pitch()

        if not shots_df.empty:
            # Normaliser les coordonnées
            shots_df['norm_x'], shots_df['norm_y'] = zip(*[
                self._normalize_coordinates(row['Start X'], row['Start Y'])
                for _, row in shots_df.iterrows()
            ])

            # Ajouter les marqueurs de tirs
            fig.add_trace(go.Scatter(
                x=shots_df['norm_x'],
                y=shots_df['norm_y'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=shots_df['Half'].map({1: 'yellow', 0: 'green'}),
                    opacity=0.7
                ),
                text=shots_df['Player1 Name'] + '<br>Half: ' + shots_df['Half'].astype(str) +
                     '<br>Time: ' + shots_df['Time'].astype(str) +
                     '<br>Event: ' + shots_df['Event Name'],
                hoverinfo='text'
            ))

        self._update_layout(fig, 'Shot Locations')
        return fig

    def create_passes_plot(self, passes_df: pd.DataFrame) -> go.Figure:
        """Crée une visualisation des passes sur le terrain."""
        fig = self._create_base_pitch(background_color="blue")

        if not passes_df.empty:
            for _, row in passes_df.iterrows():
                # Normaliser les coordonnées de début et fin
                start_x, start_y = self._normalize_coordinates(row['Start X'], row['Start Y'])
                end_x, end_y = self._normalize_coordinates(row['End X'], row['End Y'])

                # Ajouter la flèche de la passe
                fig.add_trace(go.Scatter(
                    x=[start_x, end_x],
                    y=[start_y, end_y],
                    mode='lines',
                    line=dict(width=2, color='white'),
                    hoverinfo='none'
                ))

            # Ajouter les points de départ des passes
            fig.add_trace(go.Scatter(
                x=[self._normalize_coordinates(row['Start X'], row['Start Y'])[0] for _, row in passes_df.iterrows()],
                y=[self._normalize_coordinates(row['Start X'], row['Start Y'])[1] for _, row in passes_df.iterrows()],
                mode='markers',
                marker=dict(
                    size=7,
                    color=passes_df['Half'].map({1: 'blue', 0: 'red'}),
                    opacity=0.7
                ),
                text=passes_df['Player1 Name'] + '<br>Half: ' + passes_df['Half'].astype(str) +
                     '<br>Time: ' + passes_df['Time'].astype(str) +
                     '<br>Event: ' + passes_df['Event Name'],
                hoverinfo='text'
            ))

        self._update_layout(fig, 'Pass Locations')
        return fig

    def _update_layout(self, fig: go.Figure, title: str):
        """Met à jour la mise en page de la figure."""
        fig.update_layout(
            title=title,
            xaxis=dict(
                range=[0, 100],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True
            ),
            yaxis=dict(
                range=[0, 100],
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                fixedrange=True
            ),
            width=800,
            height=600,
            plot_bgcolor='green',
            paper_bgcolor='white'
        )