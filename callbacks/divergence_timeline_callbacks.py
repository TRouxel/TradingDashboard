# callbacks/divergence_timeline_callbacks.py
"""
Callbacks pour le graphique timeline des divergences RSI.
VERSION 2.0 - Filtre par catégorie d'actifs
"""
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

from data_handler import fetch_and_prepare_data
from config import load_user_assets, load_user_assets_with_categories, ASSET_CATEGORIES, get_asset_category
from components.divergence_timeline import (
    create_divergence_timeline_chart,
    create_stats_summary,
    calculate_strategy_stats,
    generate_color_for_asset
)


def get_all_divergences(assets, period, config):
    """
    Récupère toutes les divergences RSI pour tous les actifs sur une période.
    """
    all_divergences = []
    
    for ticker in assets:
        try:
            print(f"📊 Analyse des divergences pour {ticker}...")
            df = fetch_and_prepare_data(ticker, period=period, config=config)
            
            if df.empty:
                continue
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            
            if 'rsi_divergence' in df.columns:
                div_df = df[df['rsi_divergence'].isin(['bullish', 'bearish'])].copy()
                
                for _, row in div_df.iterrows():
                    date_val = row.get('Date', row.get('date'))
                    div_type = row.get('rsi_divergence')
                    price = row.get('close', row.get('Close', None))
                    
                    if pd.notna(date_val) and pd.notna(div_type):
                        all_divergences.append({
                            'date': date_val,
                            'ticker': ticker,
                            'type': div_type,
                            'price': float(price) if pd.notna(price) else None
                        })
                        
        except Exception as e:
            print(f"⚠️ Erreur pour {ticker}: {e}")
            continue
    
    all_divergences.sort(key=lambda x: x['date'])
    
    return all_divergences


def filter_assets_by_category(assets, category_filter):
    """
    Filtre les actifs par catégorie.
    
    Args:
        assets: Liste des tickers
        category_filter: 'all' ou une clé de catégorie
    
    Returns:
        Liste des tickers filtrés
    """
    if category_filter == 'all':
        return assets
    
    assets_with_cats = load_user_assets_with_categories()
    
    filtered = []
    for ticker in assets:
        cat = assets_with_cats.get(ticker, get_asset_category(ticker))
        if cat == category_filter:
            filtered.append(ticker)
    
    return filtered


def register_divergence_timeline_callbacks(app):
    """Enregistre les callbacks pour la timeline des divergences."""
    
    @app.callback(
        Output("collapse-divergence-timeline", "is_open"),
        Input("collapse-divergence-timeline-btn", "n_clicks"),
        State("collapse-divergence-timeline", "is_open"),
        prevent_initial_call=True
    )
    def toggle_divergence_timeline(n_clicks, is_open):
        return not is_open
    
    @app.callback(
        Output('divergence-timeline-content', 'children'),
        [Input('calculate-divergence-timeline-btn', 'n_clicks')],
        [State('assets-store', 'data'),
         State('period-dropdown', 'value'),
         State('config-store', 'data'),
         State('holding-period-input', 'value'),
         State('timeline-category-filter', 'value')],
        prevent_initial_call=True
    )
    def calculate_divergence_timeline(n_clicks, assets, period, config, holding_period, category_filter):
        if not assets:
            assets = load_user_assets()
        
        if not assets:
            return html.P("Aucun actif configuré.", className="text-muted")
        
        if holding_period is None or holding_period < 1:
            holding_period = 11
        
        if category_filter is None:
            category_filter = 'all'
        
        # Filtrer les actifs par catégorie
        filtered_assets = filter_assets_by_category(assets, category_filter)
        
        if not filtered_assets:
            cat_info = ASSET_CATEGORIES.get(category_filter, ASSET_CATEGORIES['custom'])
            return html.Div([
                dbc.Alert([
                    f"Aucun actif dans la catégorie ",
                    html.Strong(f"{cat_info['icon']} {cat_info['name']}"),
                    ". Ajoutez des actifs de cette catégorie ou sélectionnez 'Tous les actifs'."
                ], color="warning")
            ])
        
        # Mapper la période pour l'affichage
        period_labels = {
            '1mo': '1 Mois',
            '3mo': '3 Mois',
            '6mo': '6 Mois',
            '1y': '1 An',
            '2y': '2 Ans',
            '5y': '5 Ans',
            '10y': '10 Ans',
            'max': 'Maximum'
        }
        period_label = period_labels.get(period, period)
        
        # Construire le label complet
        if category_filter == 'all':
            full_label = f"{period_label} — Tous les actifs ({len(filtered_assets)})"
        else:
            cat_info = ASSET_CATEGORIES.get(category_filter, ASSET_CATEGORIES['custom'])
            full_label = f"{period_label} — {cat_info['icon']} {cat_info['name']} ({len(filtered_assets)} actifs)"
        
        # Récupérer toutes les divergences
        all_divergences = get_all_divergences(filtered_assets, period, config)
        
        if not all_divergences:
            return html.Div([
                dbc.Alert([
                    html.Strong("Aucune divergence RSI détectée "),
                    f"sur la période {period_label} pour les actifs sélectionnés: ",
                    html.Br(),
                    html.Small(', '.join(filtered_assets), className="text-muted")
                ], color="info"),
                html.P([
                    "Cela peut signifier que le marché n'a pas présenté de conditions de retournement ",
                    "identifiables par la divergence RSI sur cette période."
                ], className="text-muted small")
            ])
        
        # Calculer les statistiques
        stats = calculate_strategy_stats(all_divergences, holding_period)
        
        # Créer le graphique
        fig = create_divergence_timeline_chart(all_divergences, full_label)
        
        # Créer le contenu
        content = html.Div([
            # Info sur le filtre
            dbc.Alert([
                html.Strong("📊 Analyse: "),
                f"{len(filtered_assets)} actifs analysés",
                html.Span(" | ", className="text-muted"),
                f"Catégorie: ",
                html.Strong(
                    "Tous" if category_filter == 'all' 
                    else f"{ASSET_CATEGORIES.get(category_filter, {}).get('icon', '')} {ASSET_CATEGORIES.get(category_filter, {}).get('name', category_filter)}"
                ),
            ], color="dark", className="mb-3 py-2"),
            
            # Résumé des stats
            create_stats_summary(stats),
            
            # Explication de la stratégie
            dbc.Alert([
                html.Strong(f"📋 Stratégie simulée: "),
                f"Achat/Vente le jour du signal, clôture {holding_period-1} jours plus tard. ",
                html.Br(),
                html.Small([
                    f"Sur {stats['total_signals']} signaux, ",
                    html.Strong(f"{stats['actionable_signals']} sont actionnables", className="text-success"),
                    f" (espacés d'au moins {holding_period} jours). ",
                    html.Strong(f"{stats['missed_signals']} seraient manqués", className="text-warning"),
                    " car ils tombent pendant une position ouverte."
                ])
            ], color="dark", className="mb-3"),
            
            # Graphique
            dcc.Graph(
                figure=fig,
                config={'displayModeBar': True, 'scrollZoom': True}
            ),
            
            # Liste des actifs analysés
            html.Div([
                html.Hr(),
                html.Small([
                    html.Strong("Actifs analysés: "),
                    ', '.join(filtered_assets)
                ], className="text-muted")
            ], className="mt-3"),
            
            # Légende détaillée
            html.Div([
                html.Hr(),
                html.Small([
                    html.Strong("💡 Comment lire ce graphique: "),
                    "Chaque barre représente un signal de divergence RSI. ",
                    "Les barres vers le haut indiquent une divergence haussière (signal d'achat), ",
                    "les barres vers le bas indiquent une divergence baissière (signal de vente). ",
                    "Les couleurs distinguent les différents actifs."
                ], className="text-muted")
            ], className="mt-3")
        ])
        
        return content