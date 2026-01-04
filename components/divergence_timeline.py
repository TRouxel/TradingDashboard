# components/divergence_timeline.py
"""
Graphique timeline des divergences RSI pour tous les actifs.
"""
import plotly.graph_objects as go
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib


def generate_color_for_asset(ticker):
    """
    Génère une couleur unique et cohérente pour un asset basée sur son ticker.
    La même couleur sera toujours générée pour le même ticker.
    """
    # Utiliser un hash du ticker pour générer des valeurs RGB cohérentes
    hash_obj = hashlib.md5(ticker.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Extraire des valeurs pour H, S, L (utiliser HSL pour des couleurs plus vives)
    h = int(hash_hex[:2], 16) / 255 * 360  # Hue: 0-360
    s = 0.6 + (int(hash_hex[2:4], 16) / 255) * 0.3  # Saturation: 60-90%
    l = 0.45 + (int(hash_hex[4:6], 16) / 255) * 0.15  # Lightness: 45-60%
    
    # Convertir HSL en RGB
    def hsl_to_rgb(h, s, l):
        h = h / 360
        if s == 0:
            r = g = b = l
        else:
            def hue_to_rgb(p, q, t):
                if t < 0: t += 1
                if t > 1: t -= 1
                if t < 1/6: return p + (q - p) * 6 * t
                if t < 1/2: return q
                if t < 2/3: return p + (q - p) * (2/3 - t) * 6
                return p
            
            q = l * (1 + s) if l < 0.5 else l + s - l * s
            p = 2 * l - q
            r = hue_to_rgb(p, q, h + 1/3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1/3)
        
        return int(r * 255), int(g * 255), int(b * 255)
    
    r, g, b = hsl_to_rgb(h, s, l)
    return f'rgb({r}, {g}, {b})'


def calculate_strategy_stats(all_divergences, holding_period=11):
    """
    Calcule les statistiques de la stratégie basée sur les divergences.
    
    Args:
        all_divergences: Liste de dict avec 'date', 'ticker', 'type'
        holding_period: Nombre de jours de détention (défaut 11: achat J, vente J+10)
    
    Returns:
        dict avec les statistiques
    """
    if not all_divergences:
        return {
            'total_signals': 0,
            'unique_dates': 0,
            'actionable_signals': 0,
            'missed_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'signals_by_ticker': {}
        }
    
    # Convertir en DataFrame pour faciliter l'analyse
    df = pd.DataFrame(all_divergences)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    total_signals = len(df)
    unique_dates = df['date'].nunique()
    buy_signals = len(df[df['type'] == 'bullish'])
    sell_signals = len(df[df['type'] == 'bearish'])
    
    # Calculer les signaux "actionnables" (espacés d'au moins holding_period jours)
    actionable_signals = 0
    missed_signals = 0
    last_action_date = None
    
    for _, row in df.iterrows():
        current_date = row['date']
        
        if last_action_date is None:
            actionable_signals += 1
            last_action_date = current_date
        else:
            days_since_last = (current_date - last_action_date).days
            if days_since_last >= holding_period:
                actionable_signals += 1
                last_action_date = current_date
            else:
                missed_signals += 1
    
    # Signaux par ticker
    signals_by_ticker = df.groupby('ticker').agg({
        'type': 'count',
    }).rename(columns={'type': 'count'}).to_dict()['count']
    
    return {
        'total_signals': total_signals,
        'unique_dates': unique_dates,
        'actionable_signals': actionable_signals,
        'missed_signals': missed_signals,
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'signals_by_ticker': signals_by_ticker,
        'holding_period': holding_period
    }


def create_divergence_timeline_chart(divergence_data, period_label=""):
    """
    Crée le graphique timeline des divergences RSI.
    
    Args:
        divergence_data: Liste de dict avec 'date', 'ticker', 'type', 'price'
        period_label: Label de la période pour le titre
    
    Returns:
        plotly Figure
    """
    if not divergence_data:
        # Retourner un graphique vide avec message
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            text="Aucune divergence RSI détectée sur cette période",
            showarrow=False,
            font=dict(size=16, color="#6c757d")
        )
        fig.update_layout(
            template='plotly_dark',
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    fig = go.Figure()
    
    # Organiser les données par ticker
    df = pd.DataFrame(divergence_data)
    df['date'] = pd.to_datetime(df['date'])
    
    tickers = df['ticker'].unique()
    
    # Générer les couleurs pour chaque ticker
    ticker_colors = {ticker: generate_color_for_asset(ticker) for ticker in tickers}
    
    # Créer une trace par ticker
    for ticker in tickers:
        ticker_data = df[df['ticker'] == ticker]
        color = ticker_colors[ticker]
        
        # Séparer les signaux d'achat et de vente
        bullish = ticker_data[ticker_data['type'] == 'bullish']
        bearish = ticker_data[ticker_data['type'] == 'bearish']
        
        # Barres d'achat (vers le haut)
        if not bullish.empty:
            fig.add_trace(go.Bar(
                x=bullish['date'],
                y=[1] * len(bullish),
                name=f"{ticker} (Achat)",
                marker_color=color,
                opacity=0.8,
                text=[f"{ticker}<br>Achat<br>${p:.2f}" if pd.notna(p) else f"{ticker}<br>Achat" 
                      for p in bullish.get('price', [None] * len(bullish))],
                textposition='outside',
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "Date: %{x}<br>"
                    "Signal: 🟢 ACHAT<br>"
                    "<extra></extra>"
                ),
                showlegend=True,
                legendgroup=ticker,
            ))
        
        # Barres de vente (vers le bas)
        if not bearish.empty:
            fig.add_trace(go.Bar(
                x=bearish['date'],
                y=[-1] * len(bearish),
                name=f"{ticker} (Vente)",
                marker_color=color,
                opacity=0.8,
                text=[f"{ticker}<br>Vente<br>${p:.2f}" if pd.notna(p) else f"{ticker}<br>Vente" 
                      for p in bearish.get('price', [None] * len(bearish))],
                textposition='outside',
                hovertemplate=(
                    f"<b>{ticker}</b><br>"
                    "Date: %{x}<br>"
                    "Signal: 🔴 VENTE<br>"
                    "<extra></extra>"
                ),
                showlegend=True,
                legendgroup=ticker,
            ))
    
    # Ligne de référence à 0
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    
    # Annotations
    fig.add_annotation(
        x=0.02, y=0.95, xref="paper", yref="paper",
        text="↑ ACHAT (Div. Haussière)",
        showarrow=False,
        font=dict(size=10, color="#26a69a"),
        bgcolor="rgba(38, 166, 154, 0.2)",
        borderpad=3
    )
    fig.add_annotation(
        x=0.02, y=0.05, xref="paper", yref="paper",
        text="↓ VENTE (Div. Baissière)",
        showarrow=False,
        font=dict(size=10, color="#ef5350"),
        bgcolor="rgba(239, 83, 80, 0.2)",
        borderpad=3
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        title=dict(
            text=f"📊 Timeline des Divergences RSI — {period_label}" if period_label else "📊 Timeline des Divergences RSI",
            font=dict(size=14)
        ),
        barmode='relative',
        bargap=0.1,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9)
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis=dict(
            title="Date",
            tickformat="%d/%m/%Y",
            tickangle=-45
        ),
        yaxis=dict(
            title="",
            tickvals=[-1, 0, 1],
            ticktext=['Vente', '', 'Achat'],
            range=[-1.5, 1.5]
        ),
        hovermode='x unified'
    )
    
    return fig


def create_stats_summary(stats):
    """
    Crée le résumé des statistiques sous forme de badges.
    """
    if not stats or stats['total_signals'] == 0:
        return html.Div([
            html.P("Aucun signal détecté.", className="text-muted")
        ])
    
    holding_period = stats.get('holding_period', 11)
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Total Signaux", className="text-muted mb-1"),
                        html.H4(f"{stats['total_signals']}", className="mb-0 text-info"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📅 Dates Uniques", className="text-muted mb-1"),
                        html.H4(f"{stats['unique_dates']}", className="mb-0 text-primary"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🟢 Achats", className="text-muted mb-1"),
                        html.H4(f"{stats['buy_signals']}", className="mb-0 text-success"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🔴 Ventes", className="text-muted mb-1"),
                        html.H4(f"{stats['sell_signals']}", className="mb-0 text-danger"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"✅ Actionnables ({holding_period}j)", className="text-muted mb-1"),
                        html.H4(f"{stats['actionable_signals']}", className="mb-0 text-success"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"⏭️ Manqués (<{holding_period}j)", className="text-muted mb-1"),
                        html.H4(f"{stats['missed_signals']}", className="mb-0 text-warning"),
                    ], className="p-2")
                ], color="dark", outline=True)
            ], width=2),
        ], className="mb-3"),
        
        # Détail par ticker
        html.Div([
            html.Small("Signaux par actif: ", className="text-muted me-2"),
            *[
                dbc.Badge(
                    f"{ticker}: {count}",
                    style={'backgroundColor': generate_color_for_asset(ticker)},
                    className="me-1 mb-1"
                )
                for ticker, count in sorted(stats['signals_by_ticker'].items(), key=lambda x: -x[1])
            ]
        ], className="mb-2")
    ])


def create_divergence_timeline_section():
    """Crée la section complète du graphique timeline des divergences."""
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        id="collapse-divergence-timeline-btn",
                        color="link",
                        className="text-white text-decoration-none p-0",
                        children=[
                            html.H5("📈 Timeline des Divergences RSI (tous actifs)", className="mb-0 d-inline me-2"),
                        ]
                    ),
                ], width="auto"),
                dbc.Col([
                    dbc.Button(
                        "🔍 Calculer",
                        id="calculate-divergence-timeline-btn",
                        color="success",
                        size="sm",
                        className="me-2"
                    ),
                    html.Span([
                        html.Small("Période de détention: ", className="text-muted me-1"),
                        dbc.Input(
                            id="holding-period-input",
                            type="number",
                            value=11,
                            min=1,
                            max=30,
                            step=1,
                            size="sm",
                            style={'width': '60px', 'display': 'inline-block'}
                        ),
                        html.Small(" jours", className="text-muted ms-1"),
                    ]),
                ], className="d-flex align-items-center justify-content-end"),
            ], align="center"),
        ]),
        dbc.Collapse(
            dbc.CardBody([
                dcc.Loading(
                    html.Div(
                        id='divergence-timeline-content',
                        children=[
                            html.P([
                                "Cliquez sur ",
                                html.Strong("'Calculer'"),
                                " pour analyser les divergences RSI de tous les actifs sur la période sélectionnée. ",
                                html.Br(),
                                html.Small([
                                    "💡 Ce graphique montre quand vous auriez pu appliquer votre stratégie. ",
                                    "Les signaux 'Actionnables' sont espacés d'au moins N jours (période de détention)."
                                ], className="text-muted")
                            ], className="text-muted")
                        ]
                    ),
                    type="circle"
                )
            ], className="p-2"),
            id="collapse-divergence-timeline",
            is_open=False,
        ),
    ], className="mb-3", color="dark", outline=True)