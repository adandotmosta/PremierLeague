import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

class ChartCreator:
    max_shot_this_season = 34
    max_passe_this_season = 928
    max_saves_this_season = 13
    max_fouls_this_season = 25
    
    # Largeur fixe maximum pour chaque type de barre
    bar_max_width = 100
    
    def __init__(self):
        self.default_width = 700
        self.default_height = 400
        # Dictionnaire mapping les métriques avec leurs valeurs max correspondantes
        self.max_values = {
            'Shots': self.max_shot_this_season,
            'Passes': self.max_passe_this_season,
            'Saves': self.max_saves_this_season,
            'Fouls': self.max_fouls_this_season
        }
    
    def create_centered_bar_chart(self, stats_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """Crée un graphique à barres centré pour comparer les statistiques des équipes."""
        # Préparer les données
        teams = list(stats_data.keys())
        metrics = list(stats_data[teams[0]].keys())
        
        # Nettoyer les métriques si nécessaire
        if len(metrics) > 2:
            try:
                metrics.pop(2)
                metrics.pop()
            except IndexError:
                pass
        
        # Assurons-nous que les métriques sont dans l'ordre souhaité
        ordered_metrics = []
        for m in ['Shots', 'Passes', 'Saves', 'Fouls']:
            if m in metrics:
                ordered_metrics.append(m)
        
        # Si certaines métriques ne sont pas dans la liste prédéfinie, les ajouter à la fin
        for m in metrics:
            if m not in ordered_metrics:
                ordered_metrics.append(m)
        
        # Inverser l'ordre pour l'affichage de bas en haut
        ordered_metrics.reverse()
        
        fig = go.Figure()
        
        for metric in ordered_metrics:
            values = [stats_data[team][metric] for team in teams]

            # Utiliser le maximum saisonnier correspondant à cette métrique
            max_season_value = self._get_max_for_metric(metric)
            
            # Créer une trace pour chaque équipe et métrique
            for idx, (team, value) in enumerate(zip(teams, values)):
                # Calcul de la proportion (en pourcentage)
                proportion = value / max_season_value
                
                # Valeur active (colorée) et valeur inactive (grisée)
                active_value = proportion * self.bar_max_width
                inactive_value = self.bar_max_width - active_value
                
                # Direction (négatif pour la première équipe, positif pour la seconde)
                direction = -1 if idx == 0 else 1
                
                # Texte à afficher
                text = f"{value:.1f}"
                
                # Ajouter la partie active (colorée) de la barre
                fig.add_trace(go.Bar(
                    y=[metric],
                    x=[direction * active_value],
                    name=team if metric == ordered_metrics[0] else None,
                    orientation='h',
                    marker=dict(color='green' if idx == 0 else 'red'),
                    text=text,
                    textposition='inside',
                    hoverinfo='text',
                    showlegend=metric == ordered_metrics[0],  # Montrer la légende seulement pour la première métrique
                    legendgroup=team,
                ))
                
                # Ajouter la partie inactive (grisée) de la barre
                if inactive_value > 0:
                    # Position de départ pour la partie grisée
                    start_position = direction * active_value
                    
                    fig.add_trace(go.Bar(
                        y=[metric],
                        x=[direction * inactive_value],
                        base=start_position,  # Commence là où se termine la partie active
                        name=f"{team} (inactive)" if metric == ordered_metrics[0] else None,
                        orientation='h',
                        marker=dict(color='lightgrey', opacity=0.5),
                        hoverinfo='none',
                        showlegend=False,
                        legendgroup=team,
                    ))
        
        self._update_centered_layout(fig, teams)
        return fig
    
    def _get_max_for_metric(self, metric: str) -> float:
        """Retourne la valeur maximale saisonnière pour une métrique donnée."""
        # Si la métrique n'existe pas dans le dictionnaire, utiliser une valeur par défaut
        lower_metric = metric.lower()
        
        if 'shot' in lower_metric:
            return self.max_shot_this_season
        elif 'pass' in lower_metric:
            return self.max_passe_this_season
        elif 'save' in lower_metric:
            return self.max_saves_this_season
        elif 'foul' in lower_metric:
            return self.max_fouls_this_season
        else:
            # Valeur par défaut si la métrique ne correspond à aucune des catégories connues
            return 100.0
    
    def _update_centered_layout(self, fig: go.Figure, teams: List[str]):
        """Met à jour la mise en page du graphique centré."""
        fig.update_layout(
            title="Statistiques des équipes",
            yaxis_title=None,
            xaxis=dict(
                zeroline=True,
                zerolinecolor="black",
                showticklabels=False,
                zerolinewidth=2,
                range=[-self.bar_max_width * 1.1, self.bar_max_width * 1.1],  # S'assurer que l'axe X couvre l'ensemble des barres
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=True,
                automargin=True
            ),
            barmode="relative",
            template="plotly",
            height=self.default_height,
            width=self.default_width,
            legend=dict(
                borderwidth=1,
                orientation="h",
                y=-0.2,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.8)",
                itemsizing="constant",
                traceorder="normal",
                font=dict(size=10),
                itemwidth=40,
                yanchor="top"
            ),
        )