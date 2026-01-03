# components/performance_charts.py
"""
Graphiques de performance des indicateurs (backtesting visuel).
VERSION 2.0 - Affichage des rendements réels en % + Performance cumulée
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
    Les barres représentent le rendement réel en % (gain/perte).
    """
    if perf_df is None or perf_df.empty:
        return html.P(f"Pas de données pour {indicator_name}", className="text-muted")
    
    fig = go.Figure()
    
    # Ajouter une trace pour chaque horizon sélectionné
    for h in selected_horizons:
        score_col = f'score_{h}d'
        if score_col not in perf_df.columns:
            continue
        
        # Filtrer les valeurs valides (signaux non-neutres)
        valid_data = perf_df[(perf_df['signal'] != 'neutral') & perf_df[score_col].notna()].copy()
        
        if valid_data.empty:
            continue
        
        # Couleurs: vert si gain, rouge si perte
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
                "Rendement: %{y:.2f}%<br>"
                "<extra></extra>"
            )
        ))
    
    # Ligne de référence à 0
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    
    # Annotations pour indiquer gain/perte
    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text="📈 Gain", showarrow=False,
        font=dict(size=10, color="#26a69a"),
        bgcolor="rgba(38, 166, 154, 0.2)",
        borderpad=3
    )
    fig.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text="📉 Perte", showarrow=False,
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
        yaxis=dict(title="Rendement (%)", ticksuffix="%")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'scrollZoom': True})


def create_accuracy_badges(accuracy_stats, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée les badges de précision ET de performance cumulée pour chaque horizon.
    """
    badges = []
    
    for h in selected_horizons:
        if h not in accuracy_stats:
            continue
        
        stats = accuracy_stats[h]
        accuracy = stats.get('accuracy')
        total = stats.get('total_signals', 0)
        cumulative = stats.get('cumulative_return', 0)
        
        if accuracy is None or total == 0:
            badges.append(
                dbc.Badge(
                    f"{HORIZON_NAMES[h]}: N/A",
                    color="secondary",
                    className="me-2 mb-1",
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
        
        # Badge de précision
        badges.append(
            dbc.Badge(
                f"{HORIZON_NAMES[h]}: {accuracy:.0f}% ({stats['correct']}/{total})",
                color=badge_color,
                className="me-1 mb-1",
                style={'borderLeft': f'4px solid {HORIZON_COLORS[h]}'}
            )
        )
        
        # Badge de performance cumulée
        cum_color = "success" if cumulative > 0 else "danger" if cumulative < 0 else "secondary"
        cum_sign = "+" if cumulative > 0 else ""
        badges.append(
            dbc.Badge(
                f"Σ {cum_sign}{cumulative:.1f}%",
                color=cum_color,
                className="me-2 mb-1",
                style={'fontSize': '10px'}
            )
        )
    
    return html.Div(badges, className="mb-2", style={'lineHeight': '2'})


def create_performance_summary_badges(accuracy_stats, selected_horizons):
    """
    Crée un résumé compact de la performance.
    """
    total_signals = sum(s.get('total_signals', 0) for h, s in accuracy_stats.items() if h in selected_horizons)
    total_cumulative = sum(s.get('cumulative_return', 0) for h, s in accuracy_stats.items() if h in selected_horizons)
    
    valid_accuracies = [s['accuracy'] for h, s in accuracy_stats.items() 
                       if s.get('accuracy') is not None and h in selected_horizons]
    avg_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
    
    badges = []
    
    if avg_accuracy is not None:
        acc_color = "success" if avg_accuracy >= 55 else "warning" if avg_accuracy >= 50 else "danger"
        badges.append(dbc.Badge(f"Précision: {avg_accuracy:.0f}%", color=acc_color, className="me-2"))
    
    cum_color = "success" if total_cumulative > 0 else "danger" if total_cumulative < 0 else "secondary"
    cum_sign = "+" if total_cumulative > 0 else ""
    badges.append(dbc.Badge(f"Perf. cumulée: {cum_sign}{total_cumulative:.1f}%", color=cum_color, className="me-2"))
    
    badges.append(dbc.Badge(f"{total_signals} signaux", color="info", className="me-2"))
    
    return html.Div(badges)


def create_performance_section(performance_history, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée la section complète avec tous les graphiques de performance.
    """
    if not performance_history:
        return html.P("Aucune donnée de performance disponible. Cliquez sur 'Analyser' pour calculer.", 
                     className="text-muted")
    
    from indicator_performance import calculate_accuracy_stats
    
    sections = []
    
    for indicator_name, perf_df in performance_history.items():
        accuracy_stats = calculate_accuracy_stats(perf_df, selected_horizons)
        accuracy_badges = create_accuracy_badges(accuracy_stats, selected_horizons)
        chart = create_indicator_performance_chart(perf_df, indicator_name, selected_horizons, accuracy_stats)
        
        # Calculer les stats globales
        valid_accuracies = [s['accuracy'] for h, s in accuracy_stats.items() 
                          if s.get('accuracy') is not None and h in selected_horizons]
        global_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
        
        total_cumulative = sum(s.get('cumulative_return', 0) for h, s in accuracy_stats.items() 
                              if h in selected_horizons)
        
        # Badge de précision
        if global_accuracy is not None:
            if global_accuracy >= 55:
                indicator_badge_color = "success"
            elif global_accuracy >= 50:
                indicator_badge_color = "warning"
            else:
                indicator_badge_color = "danger"
            indicator_badge = dbc.Badge(f"{global_accuracy:.0f}%", color=indicator_badge_color, className="ms-2")
        else:
            indicator_badge = dbc.Badge("N/A", color="secondary", className="ms-2")
        
        # Badge de performance cumulée
        cum_color = "success" if total_cumulative > 0 else "danger" if total_cumulative < 0 else "secondary"
        cum_sign = "+" if total_cumulative > 0 else ""
        cum_badge = dbc.Badge(f"Σ {cum_sign}{total_cumulative:.1f}%", color=cum_color, className="ms-2")
        
        section = html.Div([
            html.Div([
                html.H6([
                    f"📊 {indicator_name}",
                    indicator_badge,
                    cum_badge,
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
    Inclut maintenant la performance cumulée.
    """
    from indicator_performance import calculate_accuracy_stats
    
    if not performance_history:
        return []
    
    cards = []
    
    for indicator_name, perf_df in performance_history.items():
        accuracy_stats = calculate_accuracy_stats(perf_df, selected_horizons)
        
        valid_accuracies = [s['accuracy'] for h, s in accuracy_stats.items() 
                          if s.get('accuracy') is not None and h in selected_horizons]
        avg_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
        
        total_signals = sum(s.get('total_signals', 0) for s in accuracy_stats.values())
        total_cumulative = sum(s.get('cumulative_return', 0) for h, s in accuracy_stats.items() 
                              if h in selected_horizons)
        
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
        
        # Couleur de la performance
        perf_color = "#26a69a" if total_cumulative > 0 else "#ef5350" if total_cumulative < 0 else "#6c757d"
        perf_sign = "+" if total_cumulative > 0 else ""
        
        card = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6(indicator_name, className="card-title mb-1", style={'fontSize': '10px', 'height': '30px'}),
                    html.Div([
                        html.Span(f"{icon} {avg_accuracy:.0f}%", style={'fontSize': '16px', 'fontWeight': 'bold'}),
                    ], className="mb-1"),
                    html.Div([
                        html.Span(f"Σ {perf_sign}{total_cumulative:.1f}%", 
                                 style={'fontSize': '12px', 'color': perf_color, 'fontWeight': 'bold'}),
                    ]),
                    html.Small(f"{total_signals} signaux", className="text-muted", style={'fontSize': '9px'}),
                ], className="p-2")
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


def create_combination_ranking_table(combo_summary, selected_horizons=[1, 2, 5, 10, 20]):
    """
    Crée un tableau de classement des combinaisons par performance.
    Inclut maintenant la performance cumulée.
    """
    if not combo_summary:
        return html.P("Aucune combinaison n'a généré de signaux.", className="text-muted")
    
    rows = []
    
    for i, combo in enumerate(combo_summary):
        name = combo['name']
        accuracy = combo['accuracy']
        total_signals = combo['total_signals']
        stats = combo['stats']
        
        # Calculer la performance cumulée moyenne
        total_cumulative = sum(s.get('cumulative_return', 0) for h, s in stats.items() if h in selected_horizons)
        
        # Déterminer la couleur selon la précision
        if accuracy >= 60:
            row_class = "table-success"
            icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "✓"
        elif accuracy >= 55:
            row_class = "table-primary"
            icon = "✓"
        elif accuracy >= 50:
            row_class = "table-warning"
            icon = "~"
        else:
            row_class = "table-danger"
            icon = "✗"
        
        # Créer les badges pour chaque horizon
        horizon_badges = []
        for h in selected_horizons:
            if h in stats and stats[h].get('accuracy') is not None:
                h_acc = stats[h]['accuracy']
                h_total = stats[h]['total_signals']
                h_cum = stats[h].get('cumulative_return', 0)
                
                if h_acc >= 55:
                    badge_color = "success"
                elif h_acc >= 50:
                    badge_color = "warning"
                else:
                    badge_color = "danger"
                
                # Badge précision
                horizon_badges.append(
                    dbc.Badge(
                        f"{h}j: {h_acc:.0f}%",
                        color=badge_color,
                        className="me-1",
                        style={'fontSize': '9px'}
                    )
                )
                
                # Badge performance
                cum_color = "success" if h_cum > 0 else "danger" if h_cum < 0 else "secondary"
                cum_sign = "+" if h_cum > 0 else ""
                horizon_badges.append(
                    dbc.Badge(
                        f"{cum_sign}{h_cum:.1f}%",
                        color=cum_color,
                        className="me-2",
                        style={'fontSize': '8px', 'opacity': '0.8'}
                    )
                )
            else:
                horizon_badges.append(
                    dbc.Badge(f"{h}j: N/A", color="secondary", className="me-2", style={'fontSize': '9px'})
                )
        
        # Type (achat/vente)
        if name.startswith('🟢'):
            type_badge = dbc.Badge("ACHAT", color="success", className="me-2")
        elif name.startswith('🔴'):
            type_badge = dbc.Badge("VENTE", color="danger", className="me-2")
        else:
            type_badge = dbc.Badge("—", color="secondary", className="me-2")
        
        clean_name = name.lstrip('🟢🔴 ')
        
        # Badge performance cumulée totale
        cum_color = "success" if total_cumulative > 0 else "danger" if total_cumulative < 0 else "secondary"
        cum_sign = "+" if total_cumulative > 0 else ""
        
        rows.append(
            html.Tr([
                html.Td(f"{icon} #{i+1}", className="text-center", style={'width': '5%'}),
                html.Td([type_badge], style={'width': '7%'}),
                html.Td(clean_name, style={'fontWeight': 'bold', 'width': '20%', 'fontSize': '12px'}),
                html.Td(f"{accuracy:.0f}%", className="text-center", 
                       style={'fontWeight': 'bold', 'fontSize': '14px', 'width': '8%'}),
                html.Td([
                    html.Span(f"{cum_sign}{total_cumulative:.1f}%", 
                             style={'color': '#26a69a' if total_cumulative > 0 else '#ef5350' if total_cumulative < 0 else '#6c757d',
                                   'fontWeight': 'bold'})
                ], className="text-center", style={'width': '10%'}),
                html.Td(str(total_signals), className="text-center", style={'width': '6%'}),
                html.Td(horizon_badges, style={'width': '44%'}),
            ], className=row_class)
        )
    
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Rang", className="text-center"),
            html.Th("Type"),
            html.Th("Combinaison"),
            html.Th("Précision", className="text-center"),
            html.Th("Perf. Σ", className="text-center"),
            html.Th("Signaux", className="text-center"),
            html.Th("Détail par Horizon"),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", responsive=True)
    
    # Légende
    legend = html.Div([
        html.Small([
            html.Span("Légende: ", className="text-muted me-2"),
            dbc.Badge("≥60%", color="success", className="me-1"), html.Span("Excellent ", className="me-2"),
            dbc.Badge("55-60%", color="primary", className="me-1"), html.Span("Bon ", className="me-2"),
            dbc.Badge("50-55%", color="warning", className="me-1"), html.Span("Moyen ", className="me-2"),
            dbc.Badge("<50%", color="danger", className="me-1"), html.Span("Faible ", className="me-3"),
            html.Span(" | ", className="text-muted"),
            html.Span(" Perf. Σ = Performance cumulée (somme des gains/pertes en %)", className="text-muted"),
        ], className="text-muted")
    ], className="mb-3")
    
    return html.Div([legend, table])


def create_global_performance_summary(performance_history, selected_horizons, initial_price=None):
    """
    Crée un résumé global de la performance de tous les indicateurs.
    """
    from indicator_performance import calculate_accuracy_stats
    
    if not performance_history:
        return html.Div()
    
    # Calculer les stats globales
    all_stats = {}
    for name, perf_df in performance_history.items():
        stats = calculate_accuracy_stats(perf_df, selected_horizons)
        all_stats[name] = stats
    
    # Trouver le meilleur et le pire
    best_perf = None
    worst_perf = None
    best_accuracy = None
    worst_accuracy = None
    
    for name, stats in all_stats.items():
        total_cum = sum(s.get('cumulative_return', 0) for h, s in stats.items() if h in selected_horizons)
        valid_acc = [s['accuracy'] for h, s in stats.items() if s.get('accuracy') is not None and h in selected_horizons]
        avg_acc = np.mean(valid_acc) if valid_acc else 0
        
        if best_perf is None or total_cum > best_perf[1]:
            best_perf = (name, total_cum)
        if worst_perf is None or total_cum < worst_perf[1]:
            worst_perf = (name, total_cum)
        if best_accuracy is None or avg_acc > best_accuracy[1]:
            best_accuracy = (name, avg_acc)
        if worst_accuracy is None or avg_acc < worst_accuracy[1]:
            worst_accuracy = (name, avg_acc)
    
    summary_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("🏆 Meilleure Performance", className="text-success mb-2"),
                    html.P(best_perf[0] if best_perf else "N/A", className="mb-1", style={'fontSize': '11px'}),
                    html.H4(f"+{best_perf[1]:.1f}%" if best_perf and best_perf[1] > 0 else f"{best_perf[1]:.1f}%" if best_perf else "N/A",
                           className="text-success mb-0"),
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("📉 Pire Performance", className="text-danger mb-2"),
                    html.P(worst_perf[0] if worst_perf else "N/A", className="mb-1", style={'fontSize': '11px'}),
                    html.H4(f"{worst_perf[1]:.1f}%" if worst_perf else "N/A",
                           className="text-danger mb-0"),
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("🎯 Meilleure Précision", className="text-primary mb-2"),
                    html.P(best_accuracy[0] if best_accuracy else "N/A", className="mb-1", style={'fontSize': '11px'}),
                    html.H4(f"{best_accuracy[1]:.0f}%" if best_accuracy else "N/A",
                           className="text-primary mb-0"),
                ])
            ], color="dark", outline=True)
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("⚠️ Pire Précision", className="text-warning mb-2"),
                    html.P(worst_accuracy[0] if worst_accuracy else "N/A", className="mb-1", style={'fontSize': '11px'}),
                    html.H4(f"{worst_accuracy[1]:.0f}%" if worst_accuracy else "N/A",
                           className="text-warning mb-0"),
                ])
            ], color="dark", outline=True)
        ], width=3),
    ], className="mb-4")
    
    return summary_cards