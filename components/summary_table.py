# components/summary_table.py
"""
Tableau récapitulatif des divergences RSI pour tous les actifs.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta


def create_assets_summary_table(summary_data, assets_list=None):
    """
    Crée le tableau récapitulatif des actifs avec les divergences RSI.
    
    Args:
        summary_data: Liste de dictionnaires avec les données de chaque actif
        assets_list: Liste des actifs à afficher (pour affichage initial sans données)
    """
    # Si on a des données, les utiliser
    if summary_data:
        rows = []
        for i, asset_data in enumerate(summary_data):
            ticker = asset_data.get('ticker', 'N/A')
            rsi_divergence = asset_data.get('rsi_divergence', 'none')
            last_div_date = asset_data.get('last_div_date')
            last_div_type = asset_data.get('last_div_type', 'none')
            current_price = asset_data.get('current_price', 0)
            rsi_value = asset_data.get('rsi_value', 50)
            recommendation = asset_data.get('recommendation', 'Neutre')
            
            # Badge pour divergence actuelle
            if rsi_divergence == 'bullish':
                div_badge = dbc.Badge("🟢 Achat", color="success", className="me-1")
            elif rsi_divergence == 'bearish':
                div_badge = dbc.Badge("🔴 Vente", color="danger", className="me-1")
            else:
                div_badge = dbc.Badge("— Néant", color="secondary", className="me-1")
            
            # Calcul de l'ancienneté de la dernière divergence
            if last_div_date:
                try:
                    if isinstance(last_div_date, str):
                        last_date = pd.to_datetime(last_div_date)
                    else:
                        last_date = last_div_date
                    
                    days_ago = (datetime.now() - last_date.to_pydatetime().replace(tzinfo=None)).days
                    
                    if days_ago == 0:
                        date_display = "Aujourd'hui"
                        date_color = "success"
                    elif days_ago == 1:
                        date_display = "Hier"
                        date_color = "success"
                    elif days_ago <= 3:
                        date_display = f"-{days_ago} jours"
                        date_color = "success"
                    elif days_ago <= 7:
                        date_display = f"-{days_ago} jours"
                        date_color = "warning"
                    elif days_ago <= 21:
                        date_display = f"-{days_ago} jours"
                        date_color = "info"
                    else:
                        date_display = f"> 21 jours"
                        date_color = "secondary"
                    
                    date_badge = dbc.Badge(date_display, color=date_color, className="me-1")
                except Exception:
                    date_badge = dbc.Badge("N/A", color="secondary", className="me-1")
            else:
                date_badge = dbc.Badge("Aucune", color="secondary", className="me-1")
            
            # Badge pour le type de la dernière divergence
            if last_div_type == 'bullish':
                last_type_badge = dbc.Badge("Achat", color="success", className="me-1")
            elif last_div_type == 'bearish':
                last_type_badge = dbc.Badge("Vente", color="danger", className="me-1")
            else:
                last_type_badge = dbc.Badge("—", color="secondary", className="me-1")
            
            # Badge pour la recommandation globale
            if recommendation == 'Acheter':
                reco_badge = dbc.Badge("🟢 Acheter", color="success")
            elif recommendation == 'Vendre':
                reco_badge = dbc.Badge("🔴 Vendre", color="danger")
            else:
                reco_badge = dbc.Badge("⚪ Neutre", color="secondary")
            
            # Couleur du RSI
            if rsi_value < 30:
                rsi_color = "#26a69a"  # Vert - survente
            elif rsi_value > 70:
                rsi_color = "#ef5350"  # Rouge - surachat
            else:
                rsi_color = "#ffffff"  # Blanc - neutre
            
            rows.append(
                html.Tr([
                    # Checkbox
                    html.Td(
                        dbc.Checkbox(
                            id={'type': 'asset-checkbox', 'index': ticker},
                            value=True,
                            className="form-check-input"
                        ),
                        className="text-center",
                        style={'width': '40px'}
                    ),
                    # Ticker
                    html.Td(
                        html.Strong(ticker),
                        style={'width': '80px'}
                    ),
                    # Prix actuel
                    html.Td(
                        f"${current_price:.2f}" if current_price else "N/A",
                        className="text-end",
                        style={'width': '90px'}
                    ),
                    # RSI
                    html.Td(
                        html.Span(f"{rsi_value:.1f}", style={'color': rsi_color, 'fontWeight': 'bold'}),
                        className="text-center",
                        style={'width': '60px'}
                    ),
                    # Divergence RSI actuelle
                    html.Td(
                        div_badge,
                        className="text-center",
                        style={'width': '100px'}
                    ),
                    # Dernière date de divergence
                    html.Td(
                        date_badge,
                        className="text-center",
                        style={'width': '100px'}
                    ),
                    # Type de la dernière divergence
                    html.Td(
                        last_type_badge,
                        className="text-center",
                        style={'width': '80px'}
                    ),
                    # Recommandation globale
                    html.Td(
                        reco_badge,
                        className="text-center",
                        style={'width': '100px'}
                    ),
                ], id={'type': 'asset-row', 'index': ticker})
            )
    
    # Si on a juste une liste d'actifs (affichage initial sans données)
    elif assets_list:
        rows = []
        for ticker in assets_list:
            rows.append(
                html.Tr([
                    # Checkbox
                    html.Td(
                        dbc.Checkbox(
                            id={'type': 'asset-checkbox', 'index': ticker},
                            value=False,  # Décoché par défaut pour le chargement initial
                            className="form-check-input"
                        ),
                        className="text-center",
                        style={'width': '40px'}
                    ),
                    # Ticker
                    html.Td(
                        html.Strong(ticker),
                        style={'width': '80px'}
                    ),
                    # Prix actuel - non chargé
                    html.Td(
                        html.Span("—", className="text-muted"),
                        className="text-end",
                        style={'width': '90px'}
                    ),
                    # RSI - non chargé
                    html.Td(
                        html.Span("—", className="text-muted"),
                        className="text-center",
                        style={'width': '60px'}
                    ),
                    # Divergence RSI actuelle - non chargé
                    html.Td(
                        dbc.Badge("—", color="secondary", className="me-1"),
                        className="text-center",
                        style={'width': '100px'}
                    ),
                    # Dernière date de divergence - non chargé
                    html.Td(
                        dbc.Badge("—", color="secondary", className="me-1"),
                        className="text-center",
                        style={'width': '100px'}
                    ),
                    # Type de la dernière divergence - non chargé
                    html.Td(
                        dbc.Badge("—", color="secondary", className="me-1"),
                        className="text-center",
                        style={'width': '80px'}
                    ),
                    # Recommandation globale - non chargé
                    html.Td(
                        dbc.Badge("—", color="secondary"),
                        className="text-center",
                        style={'width': '100px'}
                    ),
                ], id={'type': 'asset-row', 'index': ticker}, className="text-muted")
            )
    else:
        return html.Div([
            html.P("Aucun actif configuré.", className="text-muted text-center")
        ])
    
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th(
                dbc.Checkbox(
                    id='select-all-assets',
                    value=False,  # Décoché par défaut
                    className="form-check-input"
                ),
                className="text-center",
                style={'width': '40px'}
            ),
            html.Th("Actif", style={'width': '80px'}),
            html.Th("Prix", className="text-end", style={'width': '90px'}),
            html.Th("RSI", className="text-center", style={'width': '60px'}),
            html.Th("Div. RSI", className="text-center", style={'width': '100px'}),
            html.Th("Dernière Div.", className="text-center", style={'width': '100px'}),
            html.Th("Type", className="text-center", style={'width': '80px'}),
            html.Th("Reco.", className="text-center", style={'width': '100px'}),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", responsive=True, className="mb-0")
    
    return table


def create_summary_section():
    """Crée la section complète du tableau récapitulatif."""
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5("📋 Récapitulatif des Actifs — Divergences RSI", className="mb-0"),
                ], width="auto"),
                dbc.Col([
                    dbc.Button(
                        "🔄 Rafraîchir sélection",
                        id="refresh-summary-btn",
                        color="primary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "🔄 Tout rafraîchir",
                        id="refresh-all-summary-btn",
                        color="info",
                        size="sm",
                        outline=True
                    ),
                ], className="text-end"),
            ], align="center"),
        ]),
        dbc.CardBody([
            dcc.Loading(
                html.Div(
                    id='assets-summary-table',
                    # Le contenu initial sera rempli par le callback
                ),
                type="circle"
            )
        ], className="p-2"),
    ], className="mb-3", color="dark", outline=True)