import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any

class ChartCreator:
    def __init__(self):
        self.default_width = 700
        self.default_height = 400

    def create_centered_bar_chart(self, stats_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """Crée un graphique à barres centré pour comparer les statistiques des équipes."""
        # Préparer les données
        teams = list(stats_data.keys())
        metrics = list(stats_data[teams[0]].keys())
        metrics.pop()
        metrics.reverse()

        fig = go.Figure()

        for metric in metrics:
            values = [stats_data[team][metric] for team in teams]
            normalized_values = self._normalize_values(values)

            fig.add_trace(go.Bar(
                y=[metric] * len(teams),
                x=[-val if i == 0 else val for i, val in enumerate(values)],
                name=metric,
                orientation='h',
                marker=dict(color=['green', 'red']),
                text=[f"{team}: {values[i]:.1f}" for i, team in enumerate(teams)],
                textposition='inside'
            ))

        self._update_centered_layout(fig)
        return fig

    def _normalize_values(self, values: list[float], total_width: int = 100) -> list[float]:
        """Normalise les valeurs pour l'affichage."""
        max_value = max(values)
        return [val / max_value * (total_width / 2) for val in values]

    def _update_centered_layout(self, fig: go.Figure):
        """Met à jour la mise en page du graphique centré."""
        fig.update_layout(
            title="Team Statistics Comparison",
            yaxis_title=None,
            xaxis=dict(
                zeroline=True,
                zerolinecolor="black",
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
            legend=dict(bordercolor="black", orientation="h", y=-0.2, xanchor="center", x=0.5),
        )