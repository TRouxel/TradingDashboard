# config.py
"""
Configuration centralisée des paramètres du modèle d'analyse technique.
Ces valeurs sont les valeurs par défaut, modifiables via l'interface.
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# === ACTIFS PAR DÉFAUT ===
DEFAULT_ASSETS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'BTC-USD', 'ETH-USD']

# === ÉCHELLE DE TEMPS POUR LES SIGNAUX ===
SIGNAL_TIMEFRAME = {
    'lookback_days': 1,
    'options': [
        {'label': '1 Jour (Daily)', 'value': 1},
        {'label': '1 Semaine (Weekly)', 'value': 5},
        {'label': '2 Semaines', 'value': 10},
        {'label': '1 Mois (Monthly)', 'value': 20},
    ]
}

# === DESCRIPTIONS DES INDICATEURS ===
INDICATOR_DESCRIPTIONS = {
    'price': 'Évolution du cours avec chandeliers japonais',
    'moving_averages': 'Tendances court/moyen/long terme',
    'bollinger': 'Bandes de volatilité (support/résistance dynamiques)',
    'trend': 'Force et direction de la tendance (ADX/DI)',
    'macd': 'Momentum et croisements de tendance',
    'recommendations': 'Signaux Achat/Vente avec niveau de conviction',
    'volume': 'Activité des échanges sur le marché',
    'rsi': 'Zones de surachat (>70) et survente (<30)',
    'stochastic': 'Retournements potentiels via %K/%D',
    'patterns': 'Figures de chandeliers (Doji, Engulfing...)',
}

# === INDICATEURS DE MOMENTUM ===
RSI = {
    'period': 14,
    'oversold': 30,
    'overbought': 70,
    'exit_oversold_min': 30,
    'exit_oversold_max': 40,
    'exit_overbought_min': 60,
    'exit_overbought_max': 70,
}

STOCHASTIC = {
    'k_period': 14,
    'd_period': 3,
    'smooth': 3,
    'oversold': 20,
    'overbought': 80,
}

# === BANDES DE BOLLINGER ===
BOLLINGER = {
    'period': 20,
    'std_dev': 2.0,
    'squeeze_threshold': 0.05,  # % de largeur pour détecter un squeeze
}

# === INDICATEURS DE TENDANCE ===
MOVING_AVERAGES = {
    'sma_short': 20,
    'sma_medium': 50,
    'sma_long': 200,
    'ema_fast': 12,
    'ema_slow': 26,
}

MACD = {
    'fast': 12,
    'slow': 26,
    'signal': 9,
}

ADX = {
    'period': 14,
    'weak': 20,
    'strong': 25,
    'very_strong': 40,
}

# === PONDÉRATIONS DES SIGNAUX ===
SIGNAL_WEIGHTS = {
    'rsi_exit_oversold': 2.0,
    'stoch_bullish_cross': 1.0,
    'macd_bullish': 1.0,
    'macd_histogram_positive': 0.5,
    'rsi_divergence': 2.0,
    'pattern_bullish': 1.5,
    'trend_bonus': 1.0,
    'rsi_exit_overbought': 2.0,
    'stoch_bearish_cross': 1.0,
    'macd_bearish': 1.0,
    'macd_histogram_negative': 0.5,
    'pattern_bearish': 1.5,
    'bollinger_lower': 1.5,  # Signal achat sur bande basse
    'bollinger_upper': 1.5,  # Signal vente sur bande haute
}

# === FILTRES ET SEUILS DE DÉCISION ===
DECISION = {
    'min_conviction_threshold': 2.5,
    'conviction_difference': 0.5,
    'against_trend_penalty': 0.5,
    'adx_confirmation_bonus': 1.2,
    'adx_confirmation_level': 30,
    'max_conviction': 5,
}

# === CALCUL DE LA TENDANCE ===
TREND = {
    'weights': {
        'price_vs_sma_short': 1,
        'price_vs_sma_medium': 1,
        'price_vs_sma_long': 2,
        'ma_alignment': 2,
        'di_direction': 1,
    },
    'strong_threshold': 5,
    'weak_threshold': 2,
}

# === DÉTECTION DES DIVERGENCES ===
DIVERGENCE = {
    'lookback_period': 14,
    'rsi_low_threshold': 40,
    'rsi_high_threshold': 60,
}

# === FILTRES OPTIONNELS ===
OPTIONAL_FILTERS = {
    'use_volume_confirmation': False,
    'volume_ma_period': 20,
    'volume_multiplier': 1.5,
    'use_atr_filter': False,
    'atr_period': 14,
    'use_weekly_alignment': False,
}


def get_default_config():
    """Retourne la configuration par défaut sous forme de dictionnaire."""
    return {
        'signal_timeframe': SIGNAL_TIMEFRAME['lookback_days'],
        'rsi': RSI.copy(),
        'stochastic': STOCHASTIC.copy(),
        'bollinger': BOLLINGER.copy(),
        'moving_averages': MOVING_AVERAGES.copy(),
        'macd': MACD.copy(),
        'adx': ADX.copy(),
        'signal_weights': SIGNAL_WEIGHTS.copy(),
        'decision': DECISION.copy(),
        'trend': TREND.copy(),
        'divergence': DIVERGENCE.copy(),
        'optional_filters': OPTIONAL_FILTERS.copy(),
    }


# === FONCTIONS DE GESTION DES ACTIFS (PostgreSQL) ===

def load_user_assets():
    """Charge la liste des actifs depuis la base de données."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT ticker FROM user_assets ORDER BY display_order, id")
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if rows:
            return [row[0] for row in rows]
        else:
            # Si la table est vide, initialiser avec les actifs par défaut
            save_user_assets(DEFAULT_ASSETS)
            return DEFAULT_ASSETS.copy()
            
    except Exception as e:
        print(f"Erreur lors du chargement des actifs: {e}")
        return DEFAULT_ASSETS.copy()


def save_user_assets(assets):
    """Sauvegarde la liste des actifs dans la base de données."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer tous les actifs existants
        cursor.execute("DELETE FROM user_assets")
        
        # Insérer les nouveaux actifs
        for i, ticker in enumerate(assets):
            cursor.execute(
                "INSERT INTO user_assets (ticker, display_order) VALUES (%s, %s) ON CONFLICT (ticker) DO UPDATE SET display_order = %s",
                (ticker.upper().strip(), i, i)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des actifs: {e}")
        return False


def add_asset(ticker):
    """Ajoute un actif à la liste."""
    assets = load_user_assets()
    ticker = ticker.upper().strip()
    if ticker and ticker not in assets:
        assets.append(ticker)
        return save_user_assets(assets)
    return False


def remove_asset(ticker):
    """Supprime un actif de la liste."""
    assets = load_user_assets()
    ticker = ticker.upper().strip()
    if ticker in assets and len(assets) > 1:  # Garder au moins 1 actif
        assets.remove(ticker)
        return save_user_assets(assets)
    return False


def get_config_summary():
    """Retourne un résumé lisible de la configuration actuelle."""
    return f"""
    === Configuration Actuelle ===
    
    Échelle de temps: {SIGNAL_TIMEFRAME['lookback_days']} jour(s)
    
    RSI: période={RSI['period']}, survente<{RSI['oversold']}, surachat>{RSI['overbought']}
    Stochastique: K={STOCHASTIC['k_period']}, D={STOCHASTIC['d_period']}
    Bollinger: période={BOLLINGER['period']}, écart-type={BOLLINGER['std_dev']}
    
    Moyennes Mobiles: SMA {MOVING_AVERAGES['sma_short']}/{MOVING_AVERAGES['sma_medium']}/{MOVING_AVERAGES['sma_long']}
    MACD: {MACD['fast']}/{MACD['slow']}/{MACD['signal']}
    ADX: période={ADX['period']}, fort>{ADX['strong']}
    
    Seuil de conviction: {DECISION['min_conviction_threshold']}
    """