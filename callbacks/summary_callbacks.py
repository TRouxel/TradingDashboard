# summary_callbacks.py
"""
Callbacks pour le tableau récapitulatif des actifs.
VERSION 2.0 - Optimisation du téléchargement des données
"""
from dash import html, Input, Output, State, ALL, ctx, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

from config import load_user_assets, get_default_config, RSI, DIVERGENCE
from components.summary_table import create_assets_summary_table


def fetch_minimal_data_for_divergence(ticker, config=None):
    """
    Télécharge uniquement les données nécessaires pour calculer la divergence RSI.
    Beaucoup plus léger que fetch_and_prepare_data car:
    - Période courte (3 mois max au lieu de 6mo+)
    - Calcule seulement RSI et divergence (pas MACD, Bollinger, patterns, etc.)
    
    Args:
        ticker: Symbole de l'actif
        config: Configuration (optionnel)
    
    Returns:
        dict avec les infos nécessaires ou None si erreur
    """
    if config is None:
        config = get_default_config()
    
    try:
        # Télécharger seulement 3 mois de données (suffisant pour RSI 14 + divergence lookback 14*2 + marge)
        df = yf.download(ticker, period="3mo", auto_adjust=True, progress=False)
        
        if df.empty or len(df) < 50:  # Minimum nécessaire pour des calculs fiables
            return None
        
        # Normaliser les colonnes
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df.columns = df.columns.str.lower()
        
        # Renommer pour cohérence
        df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }, inplace=True)
        
        # Calculer le RSI (minimal)
        rsi_cfg = config.get('rsi', RSI)
        rsi_period = rsi_cfg.get('period', 14)
        
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()
        
        # Éviter division par zéro
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Détecter les divergences RSI (version simplifiée)
        df['rsi_divergence'] = detect_rsi_divergence_fast(df, config)
        
        # Calculer la recommandation simplifiée basée sur RSI et divergence
        df['recommendation'] = calculate_simple_recommendation(df, config)
        
        # Réinitialiser l'index pour avoir la colonne Date
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date', 'date': 'Date'}, inplace=True)
        if 'Date' not in df.columns and df.index.name:
            df = df.reset_index()
        
        return df
        
    except Exception as e:
        print(f"⚠️ Erreur fetch_minimal_data_for_divergence pour {ticker}: {e}")
        return None


def detect_rsi_divergence_fast(df, config):
    """
    Version optimisée de la détection de divergence RSI.
    Ne regarde que les derniers jours (pas tout l'historique).
    """
    div_cfg = config.get('divergence', DIVERGENCE)
    rsi_low = div_cfg.get('rsi_low_threshold', 40)
    rsi_high = div_cfg.get('rsi_high_threshold', 60)
    lookback = div_cfg.get('lookback_period', 14)
    
    divergences = ['none'] * len(df)
    
    # Ne calculer que sur les 30 derniers jours (suffisant pour détecter une divergence récente)
    start_idx = max(lookback * 2 + 5, len(df) - 30)
    
    def find_local_min(series, idx, window=5):
        if idx < window or idx >= len(series) - window:
            return False
        val = series.iloc[idx]
        left_vals = series.iloc[idx-window:idx]
        right_vals = series.iloc[idx+1:idx+window+1]
        return val <= left_vals.min() and val <= right_vals.min()
    
    def find_local_max(series, idx, window=5):
        if idx < window or idx >= len(series) - window:
            return False
        val = series.iloc[idx]
        left_vals = series.iloc[idx-window:idx]
        right_vals = series.iloc[idx+1:idx+window+1]
        return val >= left_vals.max() and val >= right_vals.max()
    
    window = 5
    min_distance = 5
    max_distance = lookback * 2
    
    for i in range(start_idx, len(df) - window):
        try:
            rsi = df['rsi'].iloc[i]
            price = df['Close'].iloc[i]
            
            if pd.isna(rsi):
                continue
            
            # Divergence haussière
            if find_local_min(df['Close'], i, window) and rsi < rsi_low:
                for j in range(i - min_distance, max(i - max_distance, lookback), -1):
                    if find_local_min(df['Close'], j, window):
                        prev_price = df['Close'].iloc[j]
                        prev_rsi = df['rsi'].iloc[j]
                        
                        if pd.isna(prev_rsi):
                            continue
                        
                        if price < prev_price and rsi > prev_rsi:
                            divergences[i] = 'bullish'
                            break
            
            # Divergence baissière
            elif find_local_max(df['Close'], i, window) and rsi > rsi_high:
                for j in range(i - min_distance, max(i - max_distance, lookback), -1):
                    if find_local_max(df['Close'], j, window):
                        prev_price = df['Close'].iloc[j]
                        prev_rsi = df['rsi'].iloc[j]
                        
                        if pd.isna(prev_rsi):
                            continue
                        
                        if price > prev_price and rsi < prev_rsi:
                            divergences[i] = 'bearish'
                            break
                            
        except (IndexError, KeyError):
            continue
    
    return divergences


def calculate_simple_recommendation(df, config):
    """
    Calcul simplifié de la recommandation basé principalement sur RSI et divergence.
    Pour le tableau récapitulatif, on n'a pas besoin de tous les indicateurs.
    """
    rsi_cfg = config.get('rsi', RSI)
    recommendations = []
    
    for i in range(len(df)):
        rsi = df['rsi'].iloc[i] if 'rsi' in df.columns else None
        div = df['rsi_divergence'].iloc[i] if 'rsi_divergence' in df.columns else 'none'
        
        if pd.isna(rsi):
            recommendations.append('Neutre')
            continue
        
        # Priorité à la divergence
        if div == 'bullish':
            recommendations.append('Acheter')
        elif div == 'bearish':
            recommendations.append('Vendre')
        # Sinon basé sur RSI extrême
        elif rsi <= rsi_cfg.get('oversold', 30):
            recommendations.append('Acheter')
        elif rsi >= rsi_cfg.get('overbought', 70):
            recommendations.append('Vendre')
        else:
            recommendations.append('Neutre')
    
    return recommendations


def get_asset_rsi_summary(ticker, config):
    """
    Récupère les informations de divergence RSI pour un actif.
    VERSION OPTIMISÉE: Utilise fetch_minimal_data_for_divergence au lieu de fetch_and_prepare_data
    
    Returns:
        dict: Données résumées pour l'actif
    """
    try:
        # Utiliser la fonction optimisée au lieu de fetch_and_prepare_data
        df = fetch_minimal_data_for_divergence(ticker, config)
        
        if df is None or df.empty:
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
        
        current_price = last_row.get('Close', 0)
        rsi_value = last_row.get('rsi', 50)
        current_divergence = last_row.get('rsi_divergence', 'none')
        recommendation = last_row.get('recommendation', 'Neutre')
        
        # Trouver la dernière divergence dans l'historique (3 derniers mois)
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
                " pour analyser tous les actifs. ",
                html.Span("(Calcul optimisé: ~3 mois de données)", className="text-info")
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
        
        # Récupérer les données pour chaque actif (VERSION OPTIMISÉE)
        summary_data = []
        errors = []
        
        import time
        start_time = time.time()
        
        for ticker in tickers_to_refresh:
            print(f"📊 Analyse rapide de {ticker}...")
            data = get_asset_rsi_summary(ticker, config)
            summary_data.append(data)
            
            if data.get('error'):
                errors.append(ticker)
        
        elapsed = time.time() - start_time
        print(f"✅ Analyse de {len(tickers_to_refresh)} actifs en {elapsed:.2f}s")
        
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
                f" | ⚡ {elapsed:.1f}s | Dernière màj: {datetime.now().strftime('%H:%M:%S')}"
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