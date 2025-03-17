import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

class ChartCreator:
    max_shot_this_season = 34
    max_passe_this_season = 928
    max_saves_this_season = 13
    
    def __init__(self):
        self.default_width = 700
        self.default_height = 400
        # Dictionnaire mapping les métriques avec leurs valeurs max correspondantes
        self.max_values = {
            'Shots': self.max_shot_this_season,
            'Passes': self.max_passe_this_season,
            'Saves': self.max_saves_this_season
        }
    
    def create_centered_bar_chart(self, stats_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """Crée un graphique à barres centré pour comparer les statistiques des équipes."""
        # Préparer les données
        teams = list(stats_data.keys())
        metrics = list(stats_data[teams[0]].keys())
        metrics.pop()
        
        # Assurons-nous que les métriques sont dans l'ordre souhaité
        ordered_metrics = []
        for m in ['Shots', 'Passes', 'Saves', 'Successful Pass Rate']:
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
            
            # Pour Successful Pass Rate, ne pas normaliser (déjà un pourcentage)
            if metric == 'Successful Pass Rate':
                normalized_values = [val / 100 * 50 for val in values]  # Normaliser à 50% de la largeur totale
            else:
                # Utiliser le maximum saisonnier correspondant à cette métrique
                max_season_value = self._get_max_for_metric(metric)
                normalized_values = self._normalize_values_with_max(values, max_season_value)
            
            # Créer une trace pour chaque équipe et métrique
            for idx, (team, value, norm_value) in enumerate(zip(teams, values, normalized_values)):
                # Formater le texte différemment pour les pourcentages
                if metric == 'Successful Pass Rate':
                    text = f"{value:.1f}%"
                else:
                    text = f"{value:.1f}"
                    
                fig.add_trace(go.Bar(
                    y=[metric],
                    x=[-norm_value] if idx == 0 else [norm_value],  # Négatif pour la première équipe
                    name=team,
                    orientation='h',
                    marker=dict(color='green' if idx == 0 else 'red'),
                    text=text,
                    textposition='inside',
                    showlegend=metric == ordered_metrics[0]  # Montrer la légende seulement pour la première métrique
                ))
        
        self._update_centered_layout(fig, teams)
        return fig
    
    def _get_max_for_metric(self, metric: str) -> float:
        """Retourne la valeur maximale saisonnière pour une métrique donnée."""
        # Si la métrique n'existe pas dans le dictionnaire, utiliser une valeur par défaut
        lower_metric = metric.lower()
        
        if 'shot' in lower_metric:
            return self.max_shot_this_season
        elif 'pass' in lower_metric and 'rate' not in lower_metric:
            return self.max_passe_this_season
        elif 'save' in lower_metric:
            return self.max_saves_this_season
        elif 'rate' in lower_metric:
            return 100.0  # Pour les pourcentages
        else:
            # Valeur par défaut si la métrique ne correspond à aucune des catégories connues
            return 100.0
    
    def _normalize_values_with_max(self, values: List[float], max_season_value: float, total_width: int = 100) -> List[float]:
        """Normalise les valeurs en fonction du maximum saisonnier."""
        # Normaliser par rapport au maximum saisonnier plutôt qu'au maximum local
        return [val / max_season_value * (total_width / 2) for val in values]
    
    def _update_centered_layout(self, fig: go.Figure, teams: List[str]):
        """Met à jour la mise en page du graphique centré."""
        fig.update_layout(
            title="Team Statistics Comparison",
            yaxis_title=None,
            xaxis=dict(
                zeroline=True,
                zerolinecolor="black",
                showticklabels=False,
                zerolinewidth=2,
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
