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
    
    def create_vector_plot(self, df: pd.DataFrame, title: str, teams) -> go.Figure:
        fig = self._create_base_pitch()
        
        if df.empty:
            self._update_layout(fig, title + ' Locations')
            return fig
        
        # Préparation des données pour l'affichage
        vectors = []
        start_points = []
        hover_texts = []
        colors = []
        
        for _, row in df.iterrows():
            # Normaliser les coordonnées originales
            start_x, start_y = self._normalize_coordinates(row['X'], row['Y'])
            end_x, end_y = self._normalize_coordinates(row['end_x'], row['end_y'])
            
            # Inverser les coordonnées si les événements sont effectués en deuxième mi-temps
            if row['Half'] == 1:
                # Pour une inversion correcte, nous devons ajuster par rapport au centre du terrain
                start_x = 100 - start_x  # Miroir horizontal (axe central à x=50)
                start_y = 100 - start_y  # Miroir vertical (axe central à y=50)
                end_x = 100 - end_x
                end_y = 100 - end_y
            
            # Ajouter aux listes pour l'affichage
            vectors.append((start_x, start_y, end_x, end_y))
            start_points.append((start_x, start_y))
            hover_texts.append(
                f"{row['Player1 Name']}"
            )
            colors.append('red' if row['Player1 Team'] == teams[1] else 'green')
        
        # Tracer les vecteurs (flèches)
        for start_x, start_y, end_x, end_y in vectors:
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
        
        # Ajouter tous les points de départ en une seule trace
        fig.add_trace(go.Scatter(
            x=[point[0] for point in start_points],
            y=[point[1] for point in start_points],
            mode='markers',
            marker=dict(
                size=8,
                color=colors,
                opacity=0.7
            ),
            text=hover_texts,
            hoverinfo='text'
        ))
        
        self._update_layout(fig, title + ' Locations')
        return fig
    
    def create_point_plot(self, df: pd.DataFrame, title: str, teams) -> go.Figure:
        fig = self._create_base_pitch()
        
        if df.empty:
            self._update_layout(fig, title + ' Locations')
            return fig
        
        # Préparer les listes pour les coordonnées et les informations de survol
        x_coords = []
        y_coords = []
        hover_texts = []
        colors = []
        
        # Normaliser et ajuster les coordonnées pour chaque point
        for _, row in df.iterrows():
            # Normaliser les coordonnées
            x, y = self._normalize_coordinates(row['X'], row['Y'])
            
            # Inverser les coordonnées si l'événement est en deuxième mi-temps
            if row['Half'] == 1:
                # Inversion par rapport au centre du terrain
                x = 100 - x
                y = 100 - y
            
            # Ajouter aux listes
            x_coords.append(x)
            y_coords.append(y)
            hover_texts.append(
                f"{row['Player1 Name']}<br>Half: {row['Half']}<br>Time: {row['Time']}<br>Event: {row['Event Name']}"
            )
            colors.append('red' if row['Player1 Team'] == teams[1] else 'green')
        
        # Créer une seule trace avec tous les points
        fig.add_trace(go.Scatter(
            x=x_coords,
            y=y_coords,
            mode='markers',
            marker=dict(
                size=8,
                color=colors,
                opacity=0.7
            ),
            text=hover_texts,
            hoverinfo='text',
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
            paper_bgcolor='white',
            showlegend=False
        )
