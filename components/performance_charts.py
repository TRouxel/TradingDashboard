# components/performance_charts.py
"""
Graphiques de performance des indicateurs (backtesting visuel).
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


# Couleurs pour chaque horizon
HORIZON_COLORS = {
    1: '#00bfff',   # Bleu clair - 1 jour
    2: '#ffa500',   # Orange - 2 jours
    5: '#26a69a',   # Vert - 5 jours
    10: '#9932cc',  # Violet - 10 jours
    20: '#ff6347',  # Rouge tomate - 20 jours
}

HORIZON_NAMES = {
    1: '1 jour',
    2: '2 jours',
    5: '5 jours',
    10: '10 jours',
    20: '20 jours',
}


def create_indicator_performance_chart(perf_df, indicator_name, selected_horizons=[1, 2, 5, 10, 20], accuracy_stats=None):
    """
    Crée un graphique de performance pour un indicateur.
    
    Args:
        perf_df: DataFrame avec colonnes Date, signal, intensity, score_Xd
        indicator_name: Nom de l'indicateur
        selected_horizons: Liste des horizons à afficher
        accuracy_stats: Statistiques de précision pré-calculées
    """
    if perf_df is None or perf_df.empty:
        return html.P(f"Pas de données pour {indicator_name}", className="text-muted")
    
    fig = go.Figure()
    
    # Ajouter une trace pour chaque horizon sélectionné
    for h in selected_horizons:
        score_col = f'score_{h}d'
        if score_col not in perf_df.columns:
            continue
        
        # Filtrer les valeurs valides
        valid_data = perf_df[perf_df[score_col].notna() & (perf_df[score_col] != 0)].copy()
        
        if valid_data.empty:
            continue
        
        # Créer les couleurs basées sur positif/négatif
        colors = [HORIZON_COLORS[h] if v > 0 else _darken_color(HORIZON_COLORS[h], 0.5) 
                  for v in valid_data[score_col]]
        
        # Ajouter les barres
        fig.add_trace(go.Bar(
            x=valid_data['Date'],
            y=valid_data[score_col],
            name=HORIZON_NAMES[h],
            marker_color=HORIZON_COLORS[h],
            opacity=0.7,
            hovertemplate=(
                f"<b>{HORIZON_NAMES[h]}</b><br>"
                "Date: %{x}<br>"
                "Score: %{y:.2f}<br>"
                "<extra></extra>"
            )
        ))
    
    # Ligne de référence à 0
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    
    # Zones colorées pour indiquer correct/incorrect
    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text="✓ Correct", showarrow=False,
        font=dict(size=10, color="#26a69a"),
        bgcolor="rgba(38, 166, 154, 0.2)",
        borderpad=3
    )
    fig.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text="✗ Incorrect", showarrow=False,
        font=dict(size=10, color="#ef5350"),
        bgcolor="rgba(239, 83, 80, 0.2)",
        borderpad=3
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=250,
        margin=dict(l=50, r=50, t=10, b=30),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        ),
        xaxis=dict(title=""),
        yaxis=dict(title="Score (+ = correct, - = incorrect)")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'scrollZoom': True})


def create_accuracy_badges(accuracy_stats, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée les badges de précision pour chaque horizon.
    """
    badges = []
    
    for h in selected_horizons:
        if h not in accuracy_stats:
            continue
        
        stats = accuracy_stats[h]
        accuracy = stats.get('accuracy')
        total = stats.get('total_signals', 0)
        
        if accuracy is None or total == 0:
            badges.append(
                dbc.Badge(
                    f"{HORIZON_NAMES[h]}: N/A",
                    color="secondary",
                    className="me-2",
                    style={'backgroundColor': HORIZON_COLORS[h], 'opacity': 0.5}
                )
            )
            continue
        
        # Couleur selon la précision
        if accuracy >= 55:
            badge_color = "success"
        elif accuracy >= 50:
            badge_color = "warning"
        else:
            badge_color = "danger"
        
        badges.append(
            dbc.Badge(
                f"{HORIZON_NAMES[h]}: {accuracy:.1f}% ({stats['correct']}/{total})",
                color=badge_color,
                className="me-2",
                style={'borderLeft': f'4px solid {HORIZON_COLORS[h]}'}
            )
        )
    
    return html.Div(badges, className="mb-2")


def create_performance_section(performance_history, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée la section complète avec tous les graphiques de performance.
    """
    if not performance_history:
        return html.P("Aucune donnée de performance disponible. Cliquez sur 'Analyser' pour calculer.", 
                     className="text-muted")
    
    # Importer ici pour éviter les imports circulaires
    from indicator_performance import calculate_accuracy_stats
    
    sections = []
    
    for indicator_name, perf_df in performance_history.items():
        # Calculer les stats de précision
        accuracy_stats = calculate_accuracy_stats(perf_df, selected_horizons)
        
        # Créer les badges de précision
        accuracy_badges = create_accuracy_badges(accuracy_stats, selected_horizons)
        
        # Créer le graphique
        chart = create_indicator_performance_chart(perf_df, indicator_name, selected_horizons, accuracy_stats)
        
        # Score global (moyenne pondérée des précisions)
        valid_accuracies = [s['accuracy'] for h, s in accuracy_stats.items() 
                          if s.get('accuracy') is not None and h in selected_horizons]
        global_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
        
        if global_accuracy is not None:
            if global_accuracy >= 55:
                indicator_badge_color = "success"
            elif global_accuracy >= 50:
                indicator_badge_color = "warning"
            else:
                indicator_badge_color = "danger"
            indicator_badge = dbc.Badge(f"{global_accuracy:.1f}%", color=indicator_badge_color, className="ms-2")
        else:
            indicator_badge = dbc.Badge("N/A", color="secondary", className="ms-2")
        
        # Section pour cet indicateur
        section = html.Div([
            html.Div([
                html.H6([
                    f"📊 {indicator_name}",
                    indicator_badge
                ], className="mb-1 d-flex align-items-center"),
                accuracy_badges,
            ], className="mb-2"),
            chart,
            html.Hr(className="my-3"),
        ])
        
        sections.append(section)
    
    return html.Div(sections)


def create_performance_summary_cards(performance_history, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée des cartes résumé pour tous les indicateurs.
    """
    from indicator_performance import calculate_accuracy_stats
    
    if not performance_history:
        return []
    
    cards = []
    
    for indicator_name, perf_df in performance_history.items():
        accuracy_stats = calculate_accuracy_stats(perf_df, selected_horizons)
        
        # Calculer la moyenne des précisions
        valid_accuracies = [s['accuracy'] for h, s in accuracy_stats.items() 
                          if s.get('accuracy') is not None and h in selected_horizons]
        avg_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
        
        # Total des signaux
        total_signals = sum(s.get('total_signals', 0) for s in accuracy_stats.values())
        
        if avg_accuracy is not None:
            if avg_accuracy >= 55:
                card_color = "success"
                icon = "✓"
            elif avg_accuracy >= 50:
                card_color = "warning"
                icon = "~"
            else:
                card_color = "danger"
                icon = "✗"
        else:
            card_color = "secondary"
            icon = "?"
            avg_accuracy = 0
        
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(indicator_name, className="card-title mb-1", style={'fontSize': '11px'}),
                    html.H4(f"{icon} {avg_accuracy:.1f}%" if avg_accuracy else "N/A", 
                           className="mb-0", style={'fontSize': '18px'}),
                    html.Small(f"{total_signals} signaux", className="text-muted"),
                ])
            ], color=card_color, outline=True, className="h-100")
        ], width=2, className="mb-2")
        
        cards.append(card)
    
    return dbc.Row(cards, className="mb-3")


def _darken_color(hex_color, factor=0.5):
    """Assombrit une couleur hex."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    darkened = tuple(int(c * factor) for c in rgb)
    return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'