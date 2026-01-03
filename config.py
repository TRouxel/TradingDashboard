# config.py
"""
Configuration centralisée des paramètres du modèle d'analyse technique.
Ces valeurs sont les valeurs par défaut, modifiables via l'interface.
VERSION 2.0 - Intégration des combinaisons d'indicateurs
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
    'squeeze_threshold': 0.05,
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

# === PONDÉRATIONS DES INDICATEURS INDIVIDUELS ===
# Ces poids sont réduits car les indicateurs seuls sont moins fiables
INDIVIDUAL_WEIGHTS = {
    # Indicateurs de momentum (poids réduits - peu fiables seuls)
    'rsi_extreme': 0.8,           # RSI en zone extrême (<30 ou >70)
    'rsi_exit_zone': 0.5,         # RSI sortie de zone
    'stoch_cross': 0.5,           # Croisement stochastique seul
    'stoch_extreme': 0.3,         # Stoch en zone extrême
    
    # MACD (poids modérés)
    'macd_cross': 0.6,            # Croisement MACD seul
    'macd_histogram': 0.3,        # Histogramme MACD
    
    # Tendance (poids importants - la tendance est cruciale)
    'trend_strong': 1.5,          # Tendance forte (strong_bullish/bearish)
    'trend_weak': 0.8,            # Tendance faible (bullish/bearish)
    
    # Divergences RSI (poids élevés - signal fort)
    'rsi_divergence': 2.0,        # Divergence RSI (très fiable)
    
    # Patterns (poids modérés)
    'pattern_signal': 0.8,        # Pattern de chandelier
    
    # Bollinger (poids faibles seuls)
    'bollinger_touch': 0.5,       # Touche de bande
    'bollinger_zone': 0.3,        # Zone proche bande
    
    # ADX/DI (poids modérés)
    'adx_direction': 0.5,         # Direction DI+/DI-
}

# === PONDÉRATIONS DES COMBINAISONS D'INDICATEURS ===
# Ces poids sont plus élevés car les combinaisons sont plus fiables
COMBINATION_WEIGHTS = {
    # === COMBINAISONS D'ACHAT (triées par fiabilité décroissante) ===
    
    # Très haute fiabilité (poids 2.5-3.0)
    'divergence_bullish_stoch': 3.0,          # Divergence Haussière + Stoch
    'triple_confirm_buy': 2.8,                 # Triple Confirm Achat (RSI+Stoch+MACD)
    'macd_cross_rsi_low': 2.5,                # MACD Croisement Haussier + RSI Bas
    
    # Haute fiabilité (poids 2.0-2.4)
    'bollinger_low_rsi_low': 2.3,             # Bollinger Basse + RSI Bas
    'rsi_low_stoch_bullish': 2.2,             # RSI Bas + Stoch Haussier
    'pattern_bullish_rsi_low': 2.2,           # Pattern Haussier + RSI Bas
    'bollinger_low_stoch_bullish': 2.0,       # Bollinger Basse + Stoch Haussier
    
    # Fiabilité moyenne-haute (poids 1.5-1.9)
    'adx_strong_di_plus': 1.8,                # ADX Fort + DI+ Dominant
    'macd_bullish_trend_bullish': 1.8,        # MACD Haussier + Tendance Haussière
    'macd_positive_trend_bullish': 1.7,       # MACD Positif + Tendance Haussière
    'pattern_bullish_trend_bullish': 1.6,     # Pattern Haussier + Tendance Haussière
    'stoch_cross_bullish_rsi_low': 1.6,       # Stoch Croisement Haussier + RSI Bas
    'rsi_exit_oversold_stoch': 1.5,           # RSI Sortie Survente + Stoch
    
    # === COMBINAISONS DE VENTE (triées par fiabilité décroissante) ===
    
    # Très haute fiabilité (poids 2.5-3.0)
    'divergence_bearish_stoch': 3.0,          # Divergence Baissière + Stoch
    'triple_confirm_sell': 2.8,                # Triple Confirm Vente (RSI+Stoch+MACD)
    'macd_cross_bearish_rsi_high': 2.5,       # MACD Croisement Baissier + RSI Haut
    
    # Haute fiabilité (poids 2.0-2.4)
    'bollinger_high_rsi_high': 2.3,           # Bollinger Haute + RSI Haut
    'rsi_high_stoch_bearish': 2.2,            # RSI Haut + Stoch Baissier
    'pattern_bearish_rsi_high': 2.2,          # Pattern Baissier + RSI Haut
    'bollinger_high_stoch_bearish': 2.0,      # Bollinger Haute + Stoch Baissier
    
    # Fiabilité moyenne-haute (poids 1.5-1.9)
    'adx_strong_di_minus': 1.8,               # ADX Fort + DI- Dominant
    'macd_bearish_trend_bearish': 1.8,        # MACD Baissier + Tendance Baissière
    'macd_negative_trend_bearish': 1.7,       # MACD Négatif + Tendance Baissière
    'pattern_bearish_trend_bearish': 1.6,     # Pattern Baissier + Tendance Baissière
    'stoch_cross_bearish_rsi_high': 1.6,      # Stoch Croisement Baissier + RSI Haut
    'rsi_exit_overbought_stoch': 1.5,         # RSI Sortie Surachat + Stoch
    'price_below_mas_macd_negative': 1.5,     # Prix Sous MAs + MACD Négatif
}

# === ANCIENS POIDS (conservés pour compatibilité) ===
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
    'bollinger_lower': 1.5,
    'bollinger_upper': 1.5,
}

# === FILTRES ET SEUILS DE DÉCISION ===
DECISION = {
    'min_conviction_threshold': 2.5,
    'conviction_difference': 0.5,
    'against_trend_penalty': 0.5,
    'adx_confirmation_bonus': 1.2,
    'adx_confirmation_level': 30,
    'max_conviction': 5,
    # Nouveaux paramètres pour le système v2
    'use_combinations': True,           # Utiliser les combinaisons
    'combination_bonus': 1.3,            # Bonus multiplicateur pour combinaisons
    'min_combinations_for_signal': 1,    # Nombre min de combinaisons actives
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

# === PROFILS DE TRADING ===
TRADING_PROFILES = {
    'conservative': {
        'name': 'Conservateur',
        'description': 'Moins de signaux, plus de fiabilité. Privilégie les combinaisons fortes.',
        'min_conviction_threshold': 3.5,
        'conviction_difference': 1.0,
        'combination_bonus': 1.5,
        'min_combinations_for_signal': 2,
        'individual_weight_multiplier': 0.5,
        'combination_weight_multiplier': 1.2,
    },
    'balanced': {
        'name': 'Équilibré',
        'description': 'Équilibre entre nombre de signaux et fiabilité.',
        'min_conviction_threshold': 2.5,
        'conviction_difference': 0.5,
        'combination_bonus': 1.3,
        'min_combinations_for_signal': 1,
        'individual_weight_multiplier': 0.8,
        'combination_weight_multiplier': 1.0,
    },
    'aggressive': {
        'name': 'Agressif',
        'description': 'Plus de signaux, accepte plus de risque.',
        'min_conviction_threshold': 2.0,
        'conviction_difference': 0.3,
        'combination_bonus': 1.1,
        'min_combinations_for_signal': 0,
        'individual_weight_multiplier': 1.0,
        'combination_weight_multiplier': 0.9,
    },
    'trend_following': {
        'name': 'Suivi de Tendance',
        'description': 'Privilégie les signaux dans le sens de la tendance.',
        'min_conviction_threshold': 2.5,
        'conviction_difference': 0.5,
        'combination_bonus': 1.3,
        'min_combinations_for_signal': 1,
        'individual_weight_multiplier': 0.7,
        'combination_weight_multiplier': 1.0,
        'trend_weight_multiplier': 2.0,
        'against_trend_penalty': 0.7,
    },
    'reversal': {
        'name': 'Retournement',
        'description': 'Cherche les retournements de tendance (divergences, patterns).',
        'min_conviction_threshold': 3.0,
        'conviction_difference': 0.8,
        'combination_bonus': 1.4,
        'min_combinations_for_signal': 1,
        'individual_weight_multiplier': 0.6,
        'combination_weight_multiplier': 1.1,
        'divergence_weight_multiplier': 1.5,
        'pattern_weight_multiplier': 1.3,
    },
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
        'individual_weights': INDIVIDUAL_WEIGHTS.copy(),
        'combination_weights': COMBINATION_WEIGHTS.copy(),
        'decision': DECISION.copy(),
        'trend': TREND.copy(),
        'divergence': DIVERGENCE.copy(),
        'optional_filters': OPTIONAL_FILTERS.copy(),
        'trading_profile': 'balanced',
    }


def get_profile_config(profile_name='balanced'):
    """Retourne la configuration pour un profil de trading spécifique."""
    base_config = get_default_config()
    
    if profile_name not in TRADING_PROFILES:
        profile_name = 'balanced'
    
    profile = TRADING_PROFILES[profile_name]
    
    # Appliquer les paramètres du profil
    base_config['decision']['min_conviction_threshold'] = profile['min_conviction_threshold']
    base_config['decision']['conviction_difference'] = profile['conviction_difference']
    base_config['decision']['combination_bonus'] = profile['combination_bonus']
    base_config['decision']['min_combinations_for_signal'] = profile['min_combinations_for_signal']
    
    # Appliquer les multiplicateurs de poids
    ind_mult = profile.get('individual_weight_multiplier', 1.0)
    comb_mult = profile.get('combination_weight_multiplier', 1.0)
    
    for key in base_config['individual_weights']:
        base_config['individual_weights'][key] *= ind_mult
    
    for key in base_config['combination_weights']:
        base_config['combination_weights'][key] *= comb_mult
    
    # Appliquer les multiplicateurs spécifiques
    if 'trend_weight_multiplier' in profile:
        mult = profile['trend_weight_multiplier']
        base_config['individual_weights']['trend_strong'] *= mult
        base_config['individual_weights']['trend_weak'] *= mult
    
    if 'divergence_weight_multiplier' in profile:
        mult = profile['divergence_weight_multiplier']
        base_config['individual_weights']['rsi_divergence'] *= mult
        base_config['combination_weights']['divergence_bullish_stoch'] *= mult
        base_config['combination_weights']['divergence_bearish_stoch'] *= mult
    
    if 'pattern_weight_multiplier' in profile:
        mult = profile['pattern_weight_multiplier']
        base_config['individual_weights']['pattern_signal'] *= mult
    
    if 'against_trend_penalty' in profile:
        base_config['decision']['against_trend_penalty'] = profile['against_trend_penalty']
    
    base_config['trading_profile'] = profile_name
    
    return base_config


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
        
        cursor.execute("DELETE FROM user_assets")
        
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
    if ticker in assets and len(assets) > 1:
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
    Utilisation des combinaisons: {DECISION['use_combinations']}
    """