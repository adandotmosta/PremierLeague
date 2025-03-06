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

    def _create_base_pitch(self, background_color: str = "rgb(0, 32, 100)") -> go.Figure:
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

        # Rond central
        fig.add_shape(
            type="circle",
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
    
    def create_vector_plot(self, df: pd.DataFrame, title: str) -> go.Figure:
        fig = self._create_base_pitch()
        if not df.empty:
            for _, row in df.iterrows():
                # Normaliser les coordonnées
                start_x, start_y = self._normalize_coordinates(row['X'], row['Y'])
                end_x, end_y = self._normalize_coordinates(row['end_x'], row['end_y'])

                # Ajouter la trajectoire
                fig.add_trace(go.Scatter(
                    x=[start_x, end_x],
                    y=[start_y, end_y],
                    mode='lines+markers',
                    line=dict(width=2, color='white'),
                    marker=dict(
                        symbol="arrow",
                        size=15,
                        angleref="previous",
                    ),
                    hoverinfo='none'
                ))

                # Ajouter les points de départ
                fig.add_trace(go.Scatter(
                    x=[self._normalize_coordinates(row['X'], row['Y'])[0] for _, row in df.iterrows()],
                    y=[self._normalize_coordinates(row['X'], row['Y'])[1] for _, row in df.iterrows()],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=df['Half'].map({1: 'yellow', 0: 'green'}),
                        opacity=0.7
                    ),
                    text=df['Player1 Name'] + '<br>Half: ' + df['Half'].astype(str) +
                        '<br>Time: ' + df['Time'].astype(str) +
                        '<br>Event: ' + df['Event Name'],
                    hoverinfo='text'
                ))
        self._update_layout(fig, title + ' Locations')
        return fig
    
    def create_point_plot(self, df: pd.DataFrame, title: str) -> go.Figure:
        fig = self._create_base_pitch()
        if not df.empty:
            # Normaliser les coordonnées une seule fois pour tout le DataFrame
            normalized_coords = [self._normalize_coordinates(row['X'], row['Y']) for _, row in df.iterrows()]
            x_coords = [coord[0] for coord in normalized_coords]
            y_coords = [coord[1] for coord in normalized_coords]
            
            # Créer une seule trace avec tous les points
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='markers',
                marker=dict(
                    size=8,
                    color=df['Half'].map({1: 'yellow', 0: 'green'}),
                    opacity=0.7
                ),
                text=df['Player1 Name'] + '<br>Half: ' + df['Half'].astype(str) +
                    '<br>Time: ' + df['Time'].astype(str) +
                    '<br>Event: ' + df['Event Name'],
                hoverinfo='text'
            ))
        self._update_layout(fig, title + ' Locations')
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