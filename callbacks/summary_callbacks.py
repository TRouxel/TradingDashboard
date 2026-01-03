# callbacks/summary_callbacks.py
"""
Callbacks pour le tableau récapitulatif des actifs.
"""
from dash import html, Input, Output, State, ALL, ctx, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

from data_handler import fetch_and_prepare_data
from config import load_user_assets
from components.summary_table import create_assets_summary_table


def get_asset_rsi_summary(ticker, config):
    """
    Récupère les informations de divergence RSI pour un actif.
    
    Returns:
        dict: Données résumées pour l'actif
    """
    try:
        # Récupérer les données avec une période suffisante pour détecter les divergences
        df = fetch_and_prepare_data(ticker, period="6mo", config=config)
        
        if df.empty:
            return {
                'ticker': ticker,
                'rsi_divergence': 'none',
                'last_div_date': None,
                'last_div_type': 'none',
                'current_price': None,
                'rsi_value': None,
                'recommendation': 'Neutre',
                'error': True
            }
        
        # Convertir la date si nécessaire
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        
        # Dernière ligne pour les valeurs actuelles
        last_row = df.iloc[-1]
        
        current_price = last_row.get('close', last_row.get('Close', 0))
        rsi_value = last_row.get('rsi', 50)
        current_divergence = last_row.get('rsi_divergence', 'none')
        recommendation = last_row.get('recommendation', 'Neutre')
        
        # Trouver la dernière divergence dans l'historique
        last_div_date = None
        last_div_type = 'none'
        
        if 'rsi_divergence' in df.columns:
            # Filtrer les lignes avec une divergence
            div_df = df[df['rsi_divergence'].isin(['bullish', 'bearish'])].copy()
            
            if not div_df.empty:
                last_div_row = div_df.iloc[-1]
                last_div_date = last_div_row.get('Date', last_div_row.get('date'))
                last_div_type = last_div_row.get('rsi_divergence', 'none')
        
        return {
            'ticker': ticker,
            'rsi_divergence': current_divergence if pd.notna(current_divergence) else 'none',
            'last_div_date': last_div_date,
            'last_div_type': last_div_type if pd.notna(last_div_type) else 'none',
            'current_price': float(current_price) if pd.notna(current_price) else 0,
            'rsi_value': float(rsi_value) if pd.notna(rsi_value) else 50,
            'recommendation': recommendation if pd.notna(recommendation) else 'Neutre',
            'error': False
        }
        
    except Exception as e:
        print(f"Erreur lors de l'analyse de {ticker}: {e}")
        return {
            'ticker': ticker,
            'rsi_divergence': 'none',
            'last_div_date': None,
            'last_div_type': 'none',
            'current_price': None,
            'rsi_value': None,
            'recommendation': 'Neutre',
            'error': True
        }


def register_summary_callbacks(app):
    """Enregistre les callbacks du tableau récapitulatif."""
    
    # === CALLBACK INITIAL: Afficher les actifs sans données au chargement ===
    @app.callback(
        Output('assets-summary-table', 'children', allow_duplicate=True),
        [Input('assets-store', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def initialize_summary_table(assets):
        """Affiche le tableau avec les actifs listés mais sans données chargées."""
        if not assets:
            assets = load_user_assets()
        
        # Créer le tableau avec juste les noms des actifs
        table = create_assets_summary_table(None, assets_list=assets)
        
        info_message = html.Div([
            html.Small([
                "💡 Cochez les actifs à analyser puis cliquez sur ",
                html.Strong("'Rafraîchir sélection'"),
                ", ou utilisez ",
                html.Strong("'Tout rafraîchir'"),
                " pour analyser tous les actifs."
            ], className="text-muted")
        ], className="mb-2")
        
        return html.Div([info_message, table])
    
    @app.callback(
        Output('assets-summary-table', 'children'),
        [Input('refresh-summary-btn', 'n_clicks'),
         Input('refresh-all-summary-btn', 'n_clicks')],
        [State({'type': 'asset-checkbox', 'index': ALL}, 'value'),
         State({'type': 'asset-checkbox', 'index': ALL}, 'id'),
         State('assets-store', 'data'),
         State('config-store', 'data'),
         State('summary-store', 'data')],
        prevent_initial_call=True
    )
    def refresh_summary_table(refresh_selection, refresh_all, checkbox_values, checkbox_ids, assets, config, cached_summary):
        """Rafraîchit le tableau récapitulatif."""
        triggered = ctx.triggered_id
        
        if not assets:
            assets = load_user_assets()
        
        # Déterminer quels actifs rafraîchir
        if triggered == 'refresh-all-summary-btn':
            # Rafraîchir tous les actifs
            tickers_to_refresh = assets
        else:
            # Rafraîchir seulement les actifs cochés
            tickers_to_refresh = []
            if checkbox_ids and checkbox_values:
                for checkbox_id, is_checked in zip(checkbox_ids, checkbox_values):
                    if is_checked:
                        tickers_to_refresh.append(checkbox_id['index'])
            
            if not tickers_to_refresh:
                # Réafficher le tableau actuel avec un message d'avertissement
                table = create_assets_summary_table(None, assets_list=assets)
                return html.Div([
                    dbc.Alert("⚠️ Aucun actif sélectionné. Cochez au moins un actif.", color="warning", dismissable=True),
                    table
                ])
        
        # Récupérer les données pour chaque actif
        summary_data = []
        errors = []
        
        for ticker in tickers_to_refresh:
            print(f"📊 Analyse de {ticker}...")
            data = get_asset_rsi_summary(ticker, config)
            summary_data.append(data)
            
            if data.get('error'):
                errors.append(ticker)
        
        # Si on n'a rafraîchi qu'une partie, garder les actifs non rafraîchis dans l'affichage
        # avec les données en cache si disponibles
        if triggered != 'refresh-all-summary-btn':
            refreshed_tickers = set(t['ticker'] for t in summary_data)
            for ticker in assets:
                if ticker not in refreshed_tickers:
                    # Ajouter un placeholder pour les actifs non rafraîchis
                    summary_data.append({
                        'ticker': ticker,
                        'rsi_divergence': 'none',
                        'last_div_date': None,
                        'last_div_type': 'none',
                        'current_price': None,
                        'rsi_value': None,
                        'recommendation': 'Neutre',
                        'not_loaded': True  # Flag pour indiquer que ce n'est pas chargé
                    })
        
        # Trier: d'abord les actifs avec divergences actives, puis par ticker
        def sort_key(x):
            if x.get('not_loaded'):
                return (3, x['ticker'])  # Non chargés en dernier
            if x['rsi_divergence'] == 'bullish':
                return (0, x['ticker'])
            elif x['rsi_divergence'] == 'bearish':
                return (1, x['ticker'])
            else:
                return (2, x['ticker'])
        
        summary_data.sort(key=sort_key)
        
        # Filtrer les actifs non chargés pour l'affichage principal
        loaded_data = [d for d in summary_data if not d.get('not_loaded')]
        not_loaded_tickers = [d['ticker'] for d in summary_data if d.get('not_loaded')]
        
        # Créer le contenu
        if loaded_data:
            content = [create_assets_summary_table(loaded_data)]
        else:
            content = [create_assets_summary_table(None, assets_list=assets)]
        
        # Ajouter un message pour les erreurs
        if errors:
            content.insert(0, dbc.Alert(
                f"⚠️ Erreur pour: {', '.join(errors)}", 
                color="warning", 
                dismissable=True,
                className="mb-2"
            ))
        
        # Ajouter un message pour les actifs non chargés
        if not_loaded_tickers:
            content.append(html.Div([
                html.Small([
                    "📋 Non analysés: ",
                    ", ".join(not_loaded_tickers)
                ], className="text-muted")
            ], className="mt-2"))
        
        # Ajouter un résumé
        num_bullish = sum(1 for d in loaded_data if d['rsi_divergence'] == 'bullish')
        num_bearish = sum(1 for d in loaded_data if d['rsi_divergence'] == 'bearish')
        
        summary_badges = html.Div([
            html.Small([
                f"Analysés: {len(loaded_data)}/{len(assets)} | ",
                html.Span([
                    dbc.Badge(f"🟢 {num_bullish} Achats", color="success", className="me-1"),
                    dbc.Badge(f"🔴 {num_bearish} Ventes", color="danger", className="me-1"),
                ]),
                f" | Dernière màj: {datetime.now().strftime('%H:%M:%S')}"
            ], className="text-muted")
        ], className="mb-2")
        
        content.insert(0, summary_badges)
        
        return html.Div(content)
    
    @app.callback(
        Output({'type': 'asset-checkbox', 'index': ALL}, 'value'),
        Input('select-all-assets', 'value'),
        State({'type': 'asset-checkbox', 'index': ALL}, 'value'),
        prevent_initial_call=True
    )
    def toggle_all_checkboxes(select_all, current_values):
        """Sélectionne ou désélectionne toutes les cases à cocher."""
        if current_values:
            return [select_all] * len(current_values)
        return []