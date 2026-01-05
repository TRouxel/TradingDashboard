# config.py - VERSION MISE À JOUR avec tous les actifs EUR
"""
Configuration centralisée des paramètres du modèle d'analyse technique.
VERSION 3.2 - Liste complète des actifs EUR (Forex, Crypto, Actions, Indices)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# === ACTIFS PAR DÉFAUT ===
DEFAULT_ASSETS = [
    # === INDICES MAJEURS ===
    '^GSPC',          # S&P 500
    
    # === ETF INDICES (UCITS EUR) ===
    'IWDA.AS',        # iShares MSCI World (EUR)
    'EUNL.DE',        # iShares MSCI World UCITS (EUR)
    'CW8.PA',         # Amundi MSCI World (EUR)
    'EWLD.PA',        # Lyxor MSCI World (EUR)
    'MWRD.DE',        # Amundi MSCI World II (EUR)
    'SXR8.DE',        # iShares S&P 500 UCITS (EUR)
    'VUAA.DE',        # Vanguard S&P 500 UCITS (EUR)
    
    # === ACTIONS EUR (Blue Chips) ===
    'AI.PA',          # Air Liquide
    'MC.PA',          # LVMH
    'OR.PA',          # L'Oréal
    'SAN.PA',         # Sanofi
    'AIR.PA',         # Airbus
    'SAP.DE',         # SAP
    'ASML.AS',        # ASML
    
    # === FOREX EUR - MAJEURES ===
    'EURJPY=X',       # EUR/JPY
    'EURGBP=X',       # EUR/GBP
    'EURCHF=X',       # EUR/CHF
    'EURAUD=X',       # EUR/AUD
    'EURCAD=X',       # EUR/CAD
    'EURNZD=X',       # EUR/NZD
    
    # === FOREX EUR - SECONDAIRES ===
    'EURSEK=X',       # EUR/SEK
    'EURNOK=X',       # EUR/NOK
    'EURDKK=X',       # EUR/DKK
    'EURPLN=X',       # EUR/PLN
    'EURHUF=X',       # EUR/HUF
    'EURCZK=X',       # EUR/CZK
    'EURTRY=X',       # EUR/TRY
    'EURZAR=X',       # EUR/ZAR
    'EURMXN=X',       # EUR/MXN
    'EURSGD=X',       # EUR/SGD
    'EURHKD=X',       # EUR/HKD
    'EURCNY=X',       # EUR/CNY
    'EURINR=X',       # EUR/INR
    'EURKRW=X',       # EUR/KRW
    
    # === CRYPTO EUR - MAJEURES ===
    'BTC-EUR',        # Bitcoin EUR
    'ETH-EUR',        # Ethereum EUR
    'SOL-EUR',        # Solana EUR
    'XRP-EUR',        # Ripple EUR
    'ADA-EUR',        # Cardano EUR
    'DOGE-EUR',       # Dogecoin EUR
    
    # === CRYPTO EUR - AUTRES LIQUIDES ===
    'DOT-EUR',        # Polkadot EUR
    'LINK-EUR',       # Chainlink EUR
    'AVAX-EUR',       # Avalanche EUR
    'MATIC-EUR',      # Polygon EUR
    'UNI-EUR',        # Uniswap EUR
    'LTC-EUR',        # Litecoin EUR
    'BCH-EUR',        # Bitcoin Cash EUR
    'ATOM-EUR',       # Cosmos EUR
    'NEAR-EUR',       # Near Protocol EUR
    'FTM-EUR',        # Fantom EUR
    'ALGO-EUR',       # Algorand EUR
    'XLM-EUR',        # Stellar EUR
    'AAVE-EUR',       # Aave EUR
    'MKR-EUR',        # Maker EUR
    'CRV-EUR',        # Curve EUR
    'SHIB-EUR',       # Shiba Inu EUR
    'PEPE-EUR',       # Pepe EUR
]

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

BOLLINGER = {
    'period': 20,
    'std_dev': 2.0,
    'squeeze_threshold': 0.05,
}

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

# === POIDS PAR DÉFAUT (BASE) ===
INDIVIDUAL_WEIGHTS = {
    'rsi_extreme': 0.8,
    'rsi_exit_zone': 0.5,
    'stoch_cross': 0.5,
    'stoch_extreme': 0.3,
    'macd_cross': 0.6,
    'macd_histogram': 0.3,
    'trend_strong': 1.5,
    'trend_weak': 0.8,
    'rsi_divergence': 2.0,
    'pattern_signal': 0.8,
    'bollinger_touch': 0.5,
    'bollinger_zone': 0.3,
    'adx_direction': 0.5,
}

COMBINATION_WEIGHTS = {
    # Combinaisons d'achat
    'divergence_bullish_stoch': 3.0,
    'triple_confirm_buy': 2.8,
    'macd_cross_rsi_low': 2.5,
    'bollinger_low_rsi_low': 2.3,
    'rsi_low_stoch_bullish': 2.2,
    'pattern_bullish_rsi_low': 2.2,
    'bollinger_low_stoch_bullish': 2.0,
    'adx_strong_di_plus': 1.8,
    'macd_bullish_trend_bullish': 1.8,
    'macd_positive_trend_bullish': 1.7,
    'pattern_bullish_trend_bullish': 1.6,
    'stoch_cross_bullish_rsi_low': 1.6,
    'rsi_exit_oversold_stoch': 1.5,
    # Combinaisons de vente
    'divergence_bearish_stoch': 3.0,
    'triple_confirm_sell': 2.8,
    'macd_cross_bearish_rsi_high': 2.5,
    'bollinger_high_rsi_high': 2.3,
    'rsi_high_stoch_bearish': 2.2,
    'pattern_bearish_rsi_high': 2.2,
    'bollinger_high_stoch_bearish': 2.0,
    'adx_strong_di_minus': 1.8,
    'macd_bearish_trend_bearish': 1.8,
    'macd_negative_trend_bearish': 1.7,
    'pattern_bearish_trend_bearish': 1.6,
    'stoch_cross_bearish_rsi_high': 1.6,
    'rsi_exit_overbought_stoch': 1.5,
    'price_below_mas_macd_negative': 1.5,
}

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

DECISION = {
    'min_conviction_threshold': 2.5,
    'conviction_difference': 0.5,
    'against_trend_penalty': 0.5,
    'adx_confirmation_bonus': 1.2,
    'adx_confirmation_level': 30,
    'max_conviction': 5,
    'use_combinations': True,
    'combination_bonus': 1.3,
    'min_combinations_for_signal': 1,
}

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

DIVERGENCE = {
    'lookback_period': 14,
    'rsi_low_threshold': 40,
    'rsi_high_threshold': 60,
}

OPTIONAL_FILTERS = {
    'use_volume_confirmation': False,
    'volume_ma_period': 20,
    'volume_multiplier': 1.5,
    'use_atr_filter': False,
    'atr_period': 14,
    'use_weekly_alignment': False,
}


# ============================================================
# === CATÉGORIES D'ASSETS ===
# ============================================================

ASSET_CATEGORIES = {
    'blue_chip': {
        'name': 'Blue Chip',
        'description': 'Actions stables de grandes entreprises (AAPL, MSFT, JNJ, KO, MCD...)',
        'icon': '🏛️',
        'color': '#0d6efd',
        'weight_modifiers': {
            'rsi_divergence': 1.3,
            'trend_strong': 1.4,
            'trend_weak': 1.2,
            'pattern_signal': 1.1,
            'rsi_extreme': 1.0,
            'macd_cross': 1.1,
            'bollinger_touch': 1.2,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.2,
            'divergence_bearish_stoch': 1.2,
            'macd_bullish_trend_bullish': 1.3,
            'macd_bearish_trend_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.5,
            'conviction_difference': 0.5,
            'against_trend_penalty': 0.6,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'blue_chip_eur': {
        'name': 'Blue Chip EUR',
        'description': 'Actions européennes stables (AI.PA, MC.PA, SAN.PA...)',
        'icon': '🇪🇺',
        'color': '#003399',
        'weight_modifiers': {
            'rsi_divergence': 1.3,
            'trend_strong': 1.4,
            'trend_weak': 1.2,
            'pattern_signal': 1.1,
            'rsi_extreme': 1.0,
            'macd_cross': 1.1,
            'bollinger_touch': 1.2,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.2,
            'divergence_bearish_stoch': 1.2,
            'macd_bullish_trend_bullish': 1.3,
            'macd_bearish_trend_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.5,
            'conviction_difference': 0.5,
            'against_trend_penalty': 0.6,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'tech_volatile': {
        'name': 'Tech Volatile',
        'description': 'Actions tech à forte volatilité (TSLA, NVDA, AMD, PLTR...)',
        'icon': '⚡',
        'color': '#6f42c1',
        'weight_modifiers': {
            'rsi_divergence': 0.8,
            'trend_strong': 1.5,
            'trend_weak': 1.0,
            'pattern_signal': 0.7,
            'rsi_extreme': 0.6,
            'macd_cross': 1.3,
            'macd_histogram': 1.4,
            'bollinger_touch': 0.6,
            'adx_direction': 1.5,
        },
        'combination_modifiers': {
            'triple_confirm_buy': 1.3,
            'triple_confirm_sell': 1.3,
            'adx_strong_di_plus': 1.4,
            'adx_strong_di_minus': 1.4,
            'macd_positive_trend_bullish': 1.3,
            'macd_negative_trend_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 3.0,
            'conviction_difference': 0.8,
            'against_trend_penalty': 0.3,
            'adx_confirmation_bonus': 1.4,
        },
        'rsi_thresholds': {
            'oversold': 25,
            'overbought': 75,
        }
    },
    
    'crypto': {
        'name': 'Crypto USD',
        'description': 'Cryptomonnaies vs USD (BTC-USD, ETH-USD, SOL-USD...)',
        'icon': '₿',
        'color': '#f7931a',
        'weight_modifiers': {
            'rsi_divergence': 1.5,
            'trend_strong': 1.6,
            'trend_weak': 0.8,
            'pattern_signal': 0.5,
            'rsi_extreme': 0.5,
            'macd_cross': 1.2,
            'macd_histogram': 1.3,
            'stoch_cross': 1.2,
            'bollinger_touch': 0.5,
            'bollinger_zone': 0.4,
            'adx_direction': 1.4,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.4,
            'divergence_bearish_stoch': 1.4,
            'triple_confirm_buy': 1.2,
            'triple_confirm_sell': 1.2,
            'macd_bullish_trend_bullish': 1.4,
            'macd_bearish_trend_bearish': 1.4,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 3.5,
            'conviction_difference': 1.0,
            'against_trend_penalty': 0.2,
            'adx_confirmation_bonus': 1.5,
        },
        'rsi_thresholds': {
            'oversold': 20,
            'overbought': 80,
        }
    },
    
    'crypto_eur': {
        'name': 'Crypto EUR',
        'description': 'Cryptomonnaies vs EUR (BTC-EUR, ETH-EUR, SOL-EUR...)',
        'icon': '💶',
        'color': '#ff9500',
        'weight_modifiers': {
            'rsi_divergence': 1.5,
            'trend_strong': 1.6,
            'trend_weak': 0.8,
            'pattern_signal': 0.5,
            'rsi_extreme': 0.5,
            'macd_cross': 1.2,
            'macd_histogram': 1.3,
            'stoch_cross': 1.2,
            'bollinger_touch': 0.5,
            'bollinger_zone': 0.4,
            'adx_direction': 1.4,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.4,
            'divergence_bearish_stoch': 1.4,
            'triple_confirm_buy': 1.2,
            'triple_confirm_sell': 1.2,
            'macd_bullish_trend_bullish': 1.4,
            'macd_bearish_trend_bearish': 1.4,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 3.5,
            'conviction_difference': 1.0,
            'against_trend_penalty': 0.2,
            'adx_confirmation_bonus': 1.5,
        },
        'rsi_thresholds': {
            'oversold': 20,
            'overbought': 80,
        }
    },
    
    'forex': {
        'name': 'Forex USD',
        'description': 'Paires de devises vs USD (EURUSD=X, GBPUSD=X...)',
        'icon': '💱',
        'color': '#20c997',
        'weight_modifiers': {
            'rsi_divergence': 1.4,
            'trend_strong': 1.2,
            'trend_weak': 1.0,
            'pattern_signal': 1.2,
            'rsi_extreme': 1.1,
            'stoch_cross': 1.4,
            'stoch_extreme': 1.2,
            'macd_cross': 1.1,
            'bollinger_touch': 1.5,
            'bollinger_zone': 1.3,
        },
        'combination_modifiers': {
            'bollinger_low_rsi_low': 1.4,
            'bollinger_high_rsi_high': 1.4,
            'bollinger_low_stoch_bullish': 1.4,
            'bollinger_high_stoch_bearish': 1.4,
            'rsi_low_stoch_bullish': 1.3,
            'rsi_high_stoch_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.0,
            'conviction_difference': 0.4,
            'against_trend_penalty': 0.5,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'forex_eur': {
        'name': 'Forex EUR',
        'description': 'Paires de devises vs EUR (EURJPY=X, EURGBP=X, EURCHF=X...)',
        'icon': '🇪🇺💱',
        'color': '#17a2b8',
        'weight_modifiers': {
            'rsi_divergence': 1.4,
            'trend_strong': 1.2,
            'trend_weak': 1.0,
            'pattern_signal': 1.2,
            'rsi_extreme': 1.1,
            'stoch_cross': 1.4,
            'stoch_extreme': 1.2,
            'macd_cross': 1.1,
            'bollinger_touch': 1.5,
            'bollinger_zone': 1.3,
        },
        'combination_modifiers': {
            'bollinger_low_rsi_low': 1.4,
            'bollinger_high_rsi_high': 1.4,
            'bollinger_low_stoch_bullish': 1.4,
            'bollinger_high_stoch_bearish': 1.4,
            'rsi_low_stoch_bullish': 1.3,
            'rsi_high_stoch_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.0,
            'conviction_difference': 0.4,
            'against_trend_penalty': 0.5,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'precious_metals': {
        'name': 'Métaux Précieux',
        'description': 'Or, Argent, Platine (GC=F, SI=F, PL=F, GLD, SLV...)',
        'icon': '🥇',
        'color': '#ffc107',
        'weight_modifiers': {
            'rsi_divergence': 1.4,
            'trend_strong': 1.5,
            'trend_weak': 1.1,
            'pattern_signal': 1.0,
            'rsi_extreme': 1.0,
            'macd_cross': 1.2,
            'bollinger_touch': 1.1,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.3,
            'divergence_bearish_stoch': 1.3,
            'macd_bullish_trend_bullish': 1.3,
            'macd_bearish_trend_bearish': 1.3,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.5,
            'conviction_difference': 0.5,
            'against_trend_penalty': 0.6,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'indices': {
        'name': 'Indices',
        'description': 'Indices boursiers (^GSPC, ^DJI, SPY, QQQ, IWDA.AS...)',
        'icon': '📊',
        'color': '#198754',
        'weight_modifiers': {
            'rsi_divergence': 1.5,
            'trend_strong': 1.4,
            'trend_weak': 1.2,
            'pattern_signal': 1.1,
            'rsi_extreme': 1.2,
            'rsi_exit_zone': 1.2,
            'macd_cross': 1.2,
            'bollinger_touch': 1.3,
            'bollinger_zone': 1.1,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.4,
            'divergence_bearish_stoch': 1.4,
            'bollinger_low_rsi_low': 1.3,
            'macd_bullish_trend_bullish': 1.2,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.0,
            'conviction_difference': 0.4,
            'against_trend_penalty': 0.7,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'etf_sector': {
        'name': 'ETF Sectoriels',
        'description': 'ETF sectoriels et thématiques (XLF, XLE, XLK, ARKK...)',
        'icon': '📦',
        'color': '#6c757d',
        'weight_modifiers': {
            'rsi_divergence': 1.3,
            'trend_strong': 1.3,
            'trend_weak': 1.1,
            'pattern_signal': 1.0,
            'rsi_extreme': 1.0,
            'macd_cross': 1.1,
            'bollinger_touch': 1.1,
        },
        'combination_modifiers': {
            'divergence_bullish_stoch': 1.2,
            'divergence_bearish_stoch': 1.2,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 2.5,
            'conviction_difference': 0.5,
            'against_trend_penalty': 0.5,
        },
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
    
    'commodities': {
        'name': 'Matières Premières',
        'description': 'Pétrole, Gaz, Blé, etc. (CL=F, NG=F, ZW=F...)',
        'icon': '🛢️',
        'color': '#dc3545',
        'weight_modifiers': {
            'rsi_divergence': 1.0,
            'trend_strong': 1.4,
            'trend_weak': 0.9,
            'pattern_signal': 0.8,
            'rsi_extreme': 0.7,
            'macd_cross': 1.2,
            'macd_histogram': 1.3,
            'adx_direction': 1.4,
            'bollinger_touch': 0.7,
        },
        'combination_modifiers': {
            'adx_strong_di_plus': 1.4,
            'adx_strong_di_minus': 1.4,
            'triple_confirm_buy': 1.2,
            'triple_confirm_sell': 1.2,
        },
        'decision_modifiers': {
            'min_conviction_threshold': 3.0,
            'conviction_difference': 0.7,
            'against_trend_penalty': 0.3,
            'adx_confirmation_bonus': 1.4,
        },
        'rsi_thresholds': {
            'oversold': 25,
            'overbought': 75,
        }
    },
    
    'custom': {
        'name': 'Personnalisé',
        'description': 'Catégorie par défaut - poids standards',
        'icon': '⚙️',
        'color': '#adb5bd',
        'weight_modifiers': {},
        'combination_modifiers': {},
        'decision_modifiers': {},
        'rsi_thresholds': {
            'oversold': 30,
            'overbought': 70,
        }
    },
}


# === MAPPING AUTOMATIQUE DES TICKERS CONNUS ===

KNOWN_TICKERS = {
    # ============================================================
    # BLUE CHIPS US
    # ============================================================
    'AAPL': 'blue_chip', 'MSFT': 'blue_chip', 'GOOGL': 'blue_chip', 'GOOG': 'blue_chip',
    'AMZN': 'blue_chip', 'META': 'blue_chip', 'JNJ': 'blue_chip', 'JPM': 'blue_chip',
    'V': 'blue_chip', 'MA': 'blue_chip', 'PG': 'blue_chip', 'KO': 'blue_chip',
    'PEP': 'blue_chip', 'MCD': 'blue_chip', 'WMT': 'blue_chip', 'HD': 'blue_chip',
    'DIS': 'blue_chip', 'NFLX': 'blue_chip', 'CSCO': 'blue_chip', 'INTC': 'blue_chip',
    'VZ': 'blue_chip', 'T': 'blue_chip', 'IBM': 'blue_chip', 'GE': 'blue_chip',
    'BA': 'blue_chip', 'CAT': 'blue_chip', 'MMM': 'blue_chip', 'AXP': 'blue_chip',
    'GS': 'blue_chip', 'UNH': 'blue_chip', 'CVX': 'blue_chip', 'XOM': 'blue_chip',
    
    # ============================================================
    # BLUE CHIPS EUROPÉENNES (EUR)
    # ============================================================
    # France (Euronext Paris - .PA)
    'AI.PA': 'blue_chip_eur',      # Air Liquide
    'MC.PA': 'blue_chip_eur',      # LVMH
    'OR.PA': 'blue_chip_eur',      # L'Oréal
    'SAN.PA': 'blue_chip_eur',     # Sanofi
    'TTE.PA': 'blue_chip_eur',     # TotalEnergies
    'BNP.PA': 'blue_chip_eur',     # BNP Paribas
    'ACA.PA': 'blue_chip_eur',     # Crédit Agricole
    'SU.PA': 'blue_chip_eur',      # Schneider Electric
    'AIR.PA': 'blue_chip_eur',     # Airbus
    'SAF.PA': 'blue_chip_eur',     # Safran
    'DG.PA': 'blue_chip_eur',      # Vinci
    'KER.PA': 'blue_chip_eur',     # Kering
    'RI.PA': 'blue_chip_eur',      # Pernod Ricard
    'CAP.PA': 'blue_chip_eur',     # Capgemini
    'CS.PA': 'blue_chip_eur',      # AXA
    'BN.PA': 'blue_chip_eur',      # Danone
    'ENGI.PA': 'blue_chip_eur',    # Engie
    'ORA.PA': 'blue_chip_eur',     # Orange
    'VIV.PA': 'blue_chip_eur',     # Vivendi
    
    # Allemagne (Xetra - .DE)
    'SAP.DE': 'blue_chip_eur',     # SAP
    'SIE.DE': 'blue_chip_eur',     # Siemens
    'ALV.DE': 'blue_chip_eur',     # Allianz
    'BAS.DE': 'blue_chip_eur',     # BASF
    'BAYN.DE': 'blue_chip_eur',    # Bayer
    'BMW.DE': 'blue_chip_eur',     # BMW
    'MBG.DE': 'blue_chip_eur',     # Mercedes-Benz
    'VOW3.DE': 'blue_chip_eur',    # Volkswagen
    'DTE.DE': 'blue_chip_eur',     # Deutsche Telekom
    'DBK.DE': 'blue_chip_eur',     # Deutsche Bank
    'MUV2.DE': 'blue_chip_eur',    # Munich Re
    'ADS.DE': 'blue_chip_eur',     # Adidas
    
    # Pays-Bas (Euronext Amsterdam - .AS)
    'ASML.AS': 'blue_chip_eur',    # ASML
    'PHIA.AS': 'blue_chip_eur',    # Philips
    'UNA.AS': 'blue_chip_eur',     # Unilever
    'INGA.AS': 'blue_chip_eur',    # ING
    'HEIA.AS': 'blue_chip_eur',    # Heineken
    
    # Espagne (.MC)
    'SAN.MC': 'blue_chip_eur',     # Santander
    'BBVA.MC': 'blue_chip_eur',    # BBVA
    'ITX.MC': 'blue_chip_eur',     # Inditex (Zara)
    'IBE.MC': 'blue_chip_eur',     # Iberdrola
    'TEF.MC': 'blue_chip_eur',     # Telefonica
    
    # Italie (.MI)
    'ENI.MI': 'blue_chip_eur',     # Eni
    'ENEL.MI': 'blue_chip_eur',    # Enel
    'ISP.MI': 'blue_chip_eur',     # Intesa Sanpaolo
    'UCG.MI': 'blue_chip_eur',     # UniCredit
    
    # ============================================================
    # TECH VOLATILE
    # ============================================================
    'TSLA': 'tech_volatile', 'NVDA': 'tech_volatile', 'AMD': 'tech_volatile',
    'PLTR': 'tech_volatile', 'SQ': 'tech_volatile', 'SHOP': 'tech_volatile',
    'ROKU': 'tech_volatile', 'SNAP': 'tech_volatile', 'PINS': 'tech_volatile',
    'COIN': 'tech_volatile', 'MARA': 'tech_volatile', 'RIOT': 'tech_volatile',
    'HOOD': 'tech_volatile', 'RIVN': 'tech_volatile', 'LCID': 'tech_volatile',
    'NIO': 'tech_volatile', 'XPEV': 'tech_volatile', 'LI': 'tech_volatile',
    'ARKK': 'tech_volatile', 'ARKG': 'tech_volatile', 'ARKF': 'tech_volatile',
    'SOXL': 'tech_volatile', 'TQQQ': 'tech_volatile', 'UPRO': 'tech_volatile',
    'MU': 'tech_volatile', 'MRVL': 'tech_volatile', 'AVGO': 'tech_volatile',
    'ARM': 'tech_volatile', 'SMCI': 'tech_volatile',
    
    # ============================================================
    # CRYPTO VS USD
    # ============================================================
    'BTC-USD': 'crypto', 'ETH-USD': 'crypto', 'SOL-USD': 'crypto',
    'XRP-USD': 'crypto', 'ADA-USD': 'crypto', 'DOGE-USD': 'crypto',
    'DOT-USD': 'crypto', 'LINK-USD': 'crypto', 'AVAX-USD': 'crypto',
    'MATIC-USD': 'crypto', 'UNI-USD': 'crypto', 'ATOM-USD': 'crypto',
    'LTC-USD': 'crypto', 'BCH-USD': 'crypto', 'NEAR-USD': 'crypto',
    'APT-USD': 'crypto', 'ARB-USD': 'crypto', 'OP-USD': 'crypto',
    'BNB-USD': 'crypto', 'TRX-USD': 'crypto', 'SHIB-USD': 'crypto',
    'FTM-USD': 'crypto', 'ALGO-USD': 'crypto', 'XLM-USD': 'crypto',
    'VET-USD': 'crypto', 'HBAR-USD': 'crypto', 'ICP-USD': 'crypto',
    'FIL-USD': 'crypto', 'AAVE-USD': 'crypto', 'MKR-USD': 'crypto',
    'CRV-USD': 'crypto', 'LDO-USD': 'crypto', 'RPL-USD': 'crypto',
    'PEPE-USD': 'crypto', 'WIF-USD': 'crypto', 'BONK-USD': 'crypto',
    
    # ============================================================
    # CRYPTO VS EUR (pour trading depuis compte EUR)
    # ============================================================
    'BTC-EUR': 'crypto_eur',       # Bitcoin
    'ETH-EUR': 'crypto_eur',       # Ethereum
    'SOL-EUR': 'crypto_eur',       # Solana
    'XRP-EUR': 'crypto_eur',       # Ripple
    'ADA-EUR': 'crypto_eur',       # Cardano
    'DOGE-EUR': 'crypto_eur',      # Dogecoin
    'DOT-EUR': 'crypto_eur',       # Polkadot
    'LINK-EUR': 'crypto_eur',      # Chainlink
    'AVAX-EUR': 'crypto_eur',      # Avalanche
    'MATIC-EUR': 'crypto_eur',     # Polygon
    'UNI-EUR': 'crypto_eur',       # Uniswap
    'LTC-EUR': 'crypto_eur',       # Litecoin
    'BCH-EUR': 'crypto_eur',       # Bitcoin Cash
    'ATOM-EUR': 'crypto_eur',      # Cosmos
    'NEAR-EUR': 'crypto_eur',      # Near Protocol
    'FTM-EUR': 'crypto_eur',       # Fantom
    'ALGO-EUR': 'crypto_eur',      # Algorand
    'XLM-EUR': 'crypto_eur',       # Stellar
    'AAVE-EUR': 'crypto_eur',      # Aave
    'MKR-EUR': 'crypto_eur',       # Maker
    'CRV-EUR': 'crypto_eur',       # Curve
    'SHIB-EUR': 'crypto_eur',      # Shiba Inu
    'PEPE-EUR': 'crypto_eur',      # Pepe
    
    # ============================================================
    # FOREX VS USD (paires classiques)
    # ============================================================
    'EURUSD=X': 'forex', 'GBPUSD=X': 'forex', 'USDJPY=X': 'forex',
    'USDCHF=X': 'forex', 'AUDUSD=X': 'forex', 'USDCAD=X': 'forex',
    'NZDUSD=X': 'forex', 'DX-Y.NYB': 'forex',
    
    # ============================================================
    # FOREX VS EUR (paires liquides sur Interactive Brokers)
    # ============================================================
    # Majeures EUR
    'EURJPY=X': 'forex_eur',       # EUR/JPY - Très liquide
    'EURGBP=X': 'forex_eur',       # EUR/GBP - Très liquide
    'EURCHF=X': 'forex_eur',       # EUR/CHF - Très liquide
    'EURAUD=X': 'forex_eur',       # EUR/AUD - Liquide
    'EURCAD=X': 'forex_eur',       # EUR/CAD - Liquide
    'EURNZD=X': 'forex_eur',       # EUR/NZD - Liquide
    
    # Secondaires EUR (liquides sur IB)
    'EURSEK=X': 'forex_eur',       # EUR/SEK - Couronne suédoise
    'EURNOK=X': 'forex_eur',       # EUR/NOK - Couronne norvégienne
    'EURDKK=X': 'forex_eur',       # EUR/DKK - Couronne danoise
    'EURPLN=X': 'forex_eur',       # EUR/PLN - Zloty polonais
    'EURHUF=X': 'forex_eur',       # EUR/HUF - Forint hongrois
    'EURCZK=X': 'forex_eur',       # EUR/CZK - Couronne tchèque
    'EURTRY=X': 'forex_eur',       # EUR/TRY - Lire turque
    'EURZAR=X': 'forex_eur',       # EUR/ZAR - Rand sud-africain
    'EURMXN=X': 'forex_eur',       # EUR/MXN - Peso mexicain
    'EURSGD=X': 'forex_eur',       # EUR/SGD - Dollar singapourien
    'EURHKD=X': 'forex_eur',       # EUR/HKD - Dollar Hong Kong
    'EURCNY=X': 'forex_eur',       # EUR/CNY - Yuan chinois
    'EURINR=X': 'forex_eur',       # EUR/INR - Roupie indienne
    'EURKRW=X': 'forex_eur',       # EUR/KRW - Won coréen
    
    # ============================================================
    # MÉTAUX PRÉCIEUX
    # ============================================================
    'GC=F': 'precious_metals', 'SI=F': 'precious_metals', 'PL=F': 'precious_metals',
    'PA=F': 'precious_metals', 'GLD': 'precious_metals', 'SLV': 'precious_metals',
    'IAU': 'precious_metals', 'PHYS': 'precious_metals', 'PSLV': 'precious_metals',
    'GOLD': 'precious_metals', 'NEM': 'precious_metals', 'RGLD': 'precious_metals',
    
    # ============================================================
    # INDICES MAJEURS
    # ============================================================
    # Indices US
    '^GSPC': 'indices',            # S&P 500
    '^DJI': 'indices',             # Dow Jones
    '^IXIC': 'indices',            # NASDAQ Composite
    '^NDX': 'indices',             # NASDAQ 100
    '^RUT': 'indices',             # Russell 2000
    '^VIX': 'indices',             # VIX
    
    # Indices Européens
    '^STOXX50E': 'indices',        # Euro Stoxx 50
    '^GDAXI': 'indices',           # DAX
    '^FCHI': 'indices',            # CAC 40
    '^FTSE': 'indices',            # FTSE 100
    '^IBEX': 'indices',            # IBEX 35
    '^FTSEMIB.MI': 'indices',      # FTSE MIB
    '^AEX': 'indices',             # AEX
    '^SSMI': 'indices',            # SMI
    
    # Indices Asiatiques
    '^N225': 'indices',            # Nikkei 225
    '^HSI': 'indices',             # Hang Seng
    '000001.SS': 'indices',        # Shanghai Composite
    '^TWII': 'indices',            # Taiwan
    '^KS11': 'indices',            # KOSPI
    '^AXJO': 'indices',            # ASX 200
    
    # ETF Indices US
    'SPY': 'indices',              # SPDR S&P 500
    'QQQ': 'indices',              # Invesco NASDAQ 100
    'DIA': 'indices',              # SPDR Dow Jones
    'IWM': 'indices',              # iShares Russell 2000
    'VOO': 'indices',              # Vanguard S&P 500
    'VTI': 'indices',              # Vanguard Total Stock Market
    'IVV': 'indices',              # iShares S&P 500
    
    # ETF Indices Mondiaux (UCITS - EUR)
    'IWDA.AS': 'indices',          # iShares MSCI World (EUR)
    'SWDA.L': 'indices',           # iShares MSCI World (GBP)
    'VWCE.DE': 'indices',          # Vanguard FTSE All-World (EUR)
    'VWRL.AS': 'indices',          # Vanguard FTSE All-World (EUR)
    'CSPX.L': 'indices',           # iShares S&P 500 UCITS (GBP)
    'SXR8.DE': 'indices',          # iShares S&P 500 UCITS (EUR)
    'VUAA.DE': 'indices',          # Vanguard S&P 500 UCITS (EUR)
    'EUNL.DE': 'indices',          # iShares MSCI World UCITS (EUR)
    'EXSA.DE': 'indices',          # iShares Euro Stoxx 50 (EUR)
    'MEUD.PA': 'indices',          # Amundi MSCI Europe (EUR)
    'CW8.PA': 'indices',           # Amundi MSCI World (EUR)
    'EWLD.PA': 'indices',          # Lyxor MSCI World (EUR)
    'MWRD.DE': 'indices',          # Amundi MSCI World II (EUR)
    
    # ============================================================
    # ETF SECTORIELS
    # ============================================================
    'XLF': 'etf_sector', 'XLE': 'etf_sector', 'XLK': 'etf_sector',
    'XLV': 'etf_sector', 'XLI': 'etf_sector', 'XLY': 'etf_sector',
    'XLP': 'etf_sector', 'XLU': 'etf_sector', 'XLB': 'etf_sector',
    'XLRE': 'etf_sector', 'XLC': 'etf_sector',
    'VGT': 'etf_sector', 'VHT': 'etf_sector', 'VNQ': 'etf_sector',
    'SMH': 'etf_sector', 'XBI': 'etf_sector', 'IBB': 'etf_sector',
    'KRE': 'etf_sector', 'XHB': 'etf_sector', 'ITB': 'etf_sector',
    
    # ============================================================
    # MATIÈRES PREMIÈRES
    # ============================================================
    'CL=F': 'commodities', 'NG=F': 'commodities', 'ZW=F': 'commodities',
    'ZC=F': 'commodities', 'ZS=F': 'commodities', 'KC=F': 'commodities',
    'CT=F': 'commodities', 'SB=F': 'commodities', 'CC=F': 'commodities',
    'HG=F': 'commodities', 'LBS=F': 'commodities',
    'USO': 'commodities', 'UNG': 'commodities', 'DBA': 'commodities',
    'DBC': 'commodities', 'GSG': 'commodities', 'PDBC': 'commodities',
}


def detect_asset_category(ticker, ticker_info=None):
    """
    Détecte automatiquement la catégorie d'un asset.
    """
    ticker = ticker.upper().strip()
    
    # 1. Vérifier si le ticker est dans la liste connue
    if ticker in KNOWN_TICKERS:
        return KNOWN_TICKERS[ticker]
    
    # 2. Détection par pattern du ticker
    # Crypto EUR
    if '-EUR' in ticker:
        base = ticker.replace('-EUR', '')
        if base.isalpha() and len(base) <= 5:
            return 'crypto_eur'
    
    # Crypto USD
    if '-USD' in ticker or '-GBP' in ticker:
        base = ticker.replace('-USD', '').replace('-GBP', '')
        if base.isalpha() and len(base) <= 5:
            return 'crypto'
    
    # Forex EUR (paires commençant par EUR)
    if '=X' in ticker:
        if ticker.startswith('EUR'):
            return 'forex_eur'
        return 'forex'
    
    # Actions européennes par extension
    if ticker.endswith('.PA') or ticker.endswith('.DE') or ticker.endswith('.AS'):
        return 'blue_chip_eur'
    if ticker.endswith('.MC') or ticker.endswith('.MI'):
        return 'blue_chip_eur'
    if ticker.endswith('.L'):
        return 'blue_chip'
    
    # Futures
    if '=F' in ticker:
        base = ticker.replace('=F', '')
        if base in ['GC', 'SI', 'PL', 'PA', 'HG']:
            return 'precious_metals'
        return 'commodities'
    
    # Indices
    if ticker.startswith('^'):
        return 'indices'
    
    # 3. Utiliser les infos yfinance si disponibles
    if ticker_info:
        quote_type = ticker_info.get('quoteType', '').upper()
        currency = ticker_info.get('currency', '').upper()
        
        if quote_type == 'CRYPTOCURRENCY':
            return 'crypto_eur' if currency == 'EUR' else 'crypto'
        elif quote_type == 'CURRENCY':
            symbol = ticker_info.get('symbol', ticker)
            if symbol.startswith('EUR'):
                return 'forex_eur'
            return 'forex'
        elif quote_type == 'ETF':
            short_name = ticker_info.get('shortName', '').upper()
            if any(x in short_name for x in ['S&P 500', 'NASDAQ', 'DOW', 'RUSSELL', 'TOTAL MARKET', 'MSCI WORLD', 'FTSE']):
                return 'indices'
            return 'etf_sector'
        elif quote_type == 'INDEX':
            return 'indices'
        elif quote_type == 'FUTURE':
            category = ticker_info.get('category', '')
            if 'metal' in category.lower() or 'gold' in category.lower() or 'silver' in category.lower():
                return 'precious_metals'
            return 'commodities'
        elif quote_type == 'EQUITY':
            sector = ticker_info.get('sector', '')
            industry = ticker_info.get('industry', '')
            beta = ticker_info.get('beta', 1.0)
            market_cap = ticker_info.get('marketCap', 0)
            
            if currency == 'EUR':
                if market_cap and market_cap > 10e9:
                    return 'blue_chip_eur'
            
            if sector == 'Technology':
                if beta and beta > 1.5:
                    return 'tech_volatile'
                elif market_cap and market_cap > 100e9:
                    return 'blue_chip'
                else:
                    return 'tech_volatile'
            
            if sector in ['Consumer Cyclical', 'Consumer Defensive', 'Financial Services', 'Healthcare']:
                if market_cap and market_cap > 50e9:
                    return 'blue_chip'
            
            if 'gold' in industry.lower() or 'precious' in industry.lower():
                return 'precious_metals'
            
            if sector == 'Energy':
                if market_cap and market_cap > 100e9:
                    return 'blue_chip'
                return 'commodities'
    
    return 'custom'


def get_category_config(category_key):
    """
    Retourne la configuration complète pour une catégorie d'asset.
    """
    config = get_default_config()
    
    if category_key not in ASSET_CATEGORIES:
        category_key = 'custom'
    
    category = ASSET_CATEGORIES[category_key]
    
    weight_mods = category.get('weight_modifiers', {})
    for key, multiplier in weight_mods.items():
        if key in config['individual_weights']:
            config['individual_weights'][key] *= multiplier
    
    combo_mods = category.get('combination_modifiers', {})
    for key, multiplier in combo_mods.items():
        if key in config['combination_weights']:
            config['combination_weights'][key] *= multiplier
    
    decision_mods = category.get('decision_modifiers', {})
    for key, value in decision_mods.items():
        if key in config['decision']:
            config['decision'][key] = value
    
    rsi_thresholds = category.get('rsi_thresholds', {})
    if 'oversold' in rsi_thresholds:
        config['rsi']['oversold'] = rsi_thresholds['oversold']
    if 'overbought' in rsi_thresholds:
        config['rsi']['overbought'] = rsi_thresholds['overbought']
    
    config['asset_category'] = category_key
    
    return config


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
        'asset_category': 'custom',
    }


# === FONCTIONS DE GESTION DES ACTIFS AVEC CATÉGORIES ===

def load_user_assets():
    """Charge la liste des actifs depuis la base de données."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_assets' AND column_name = 'category'
        """)
        has_category = cursor.fetchone() is not None
        
        if has_category:
            cursor.execute("SELECT ticker, category FROM user_assets ORDER BY display_order, id")
        else:
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


def load_user_assets_with_categories():
    """Charge la liste des actifs avec leurs catégories."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_assets' AND column_name = 'category'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE user_assets ADD COLUMN category VARCHAR(50) DEFAULT 'custom'")
            conn.commit()
        
        cursor.execute("SELECT ticker, category FROM user_assets ORDER BY display_order, id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if rows:
            return {row[0]: row[1] or 'custom' for row in rows}
        else:
            assets_with_cats = {}
            for ticker in DEFAULT_ASSETS:
                assets_with_cats[ticker] = detect_asset_category(ticker)
            save_user_assets_with_categories(assets_with_cats)
            return assets_with_cats
            
    except Exception as e:
        print(f"Erreur lors du chargement des actifs avec catégories: {e}")
        return {ticker: detect_asset_category(ticker) for ticker in DEFAULT_ASSETS}


def save_user_assets(assets):
    """Sauvegarde la liste des actifs."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM user_assets")
        
        for i, ticker in enumerate(assets):
            category = detect_asset_category(ticker)
            cursor.execute(
                """INSERT INTO user_assets (ticker, display_order, category) 
                   VALUES (%s, %s, %s) 
                   ON CONFLICT (ticker) DO UPDATE SET display_order = %s, category = %s""",
                (ticker.upper().strip(), i, category, i, category)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des actifs: {e}")
        return False


def save_user_assets_with_categories(assets_dict):
    """Sauvegarde la liste des actifs avec leurs catégories."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'user_assets' AND column_name = 'category'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE user_assets ADD COLUMN category VARCHAR(50) DEFAULT 'custom'")
            conn.commit()
        
        cursor.execute("DELETE FROM user_assets")
        
        for i, (ticker, category) in enumerate(assets_dict.items()):
            cursor.execute(
                """INSERT INTO user_assets (ticker, display_order, category) 
                   VALUES (%s, %s, %s) 
                   ON CONFLICT (ticker) DO UPDATE SET display_order = %s, category = %s""",
                (ticker.upper().strip(), i, category, i, category)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des actifs avec catégories: {e}")
        return False


def get_asset_category(ticker):
    """Récupère la catégorie d'un asset."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT category FROM user_assets WHERE ticker = %s", (ticker.upper(),))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row and row[0]:
            return row[0]
        else:
            return detect_asset_category(ticker)
            
    except Exception as e:
        print(f"Erreur lors de la récupération de la catégorie de {ticker}: {e}")
        return detect_asset_category(ticker)


def update_asset_category(ticker, category):
    """Met à jour la catégorie d'un asset."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE user_assets SET category = %s WHERE ticker = %s",
            (category, ticker.upper())
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la catégorie de {ticker}: {e}")
        return False


def add_asset(ticker):
    """Ajoute un actif avec détection automatique de sa catégorie."""
    assets = load_user_assets_with_categories()
    ticker = ticker.upper().strip()
    
    if ticker and ticker not in assets:
        try:
            import yfinance as yf
            info = yf.Ticker(ticker).info
            category = detect_asset_category(ticker, info)
        except Exception:
            category = detect_asset_category(ticker)
        
        assets[ticker] = category
        return save_user_assets_with_categories(assets), category
    
    return False, None


def remove_asset(ticker):
    """Supprime un actif de la liste."""
    assets = load_user_assets_with_categories()
    ticker = ticker.upper().strip()
    
    if ticker in assets and len(assets) > 1:
        del assets[ticker]
        return save_user_assets_with_categories(assets)
    
    return False


def reset_to_default_assets():
    """Réinitialise la liste des actifs aux valeurs par défaut."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer tous les actifs existants
        cursor.execute("DELETE FROM user_assets")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        # Sauvegarder les actifs par défaut
        return save_user_assets(DEFAULT_ASSETS)
        
    except Exception as e:
        print(f"Erreur lors de la réinitialisation: {e}")
        return save_user_assets(DEFAULT_ASSETS)


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
    Catégories d'assets: {len(ASSET_CATEGORIES)} types configurés
    Actifs par défaut: {len(DEFAULT_ASSETS)} actifs
    """