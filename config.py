# config.py - VERSION MISE À JOUR avec corrections devises et assets
"""
Configuration centralisée des paramètres du modèle d'analyse technique.
VERSION 3.3 - Corrections Forex EUR, Métaux EUR, réorganisation actions US
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
    
    # === BLUE CHIPS US (Valeurs stables) ===
    'AAPL',           # Apple
    'MSFT',           # Microsoft
    'GOOGL',          # Alphabet (Google)
    'JNJ',            # Johnson & Johnson
    'KO',             # Coca-Cola
    'PG',             # Procter & Gamble
    'PEP',            # PepsiCo
    'MCD',            # McDonald's
    'WMT',            # Walmart
    'JPM',            # JPMorgan Chase
    'V',              # Visa
    'MA',             # Mastercard
    'UNH',            # UnitedHealth
    'HD',             # Home Depot
    'DIS',            # Disney
    
    # === TECH VOLATILE US (Growth / Momentum) ===
    'TSLA',           # Tesla
    'NVDA',           # NVIDIA
    'AMD',            # AMD
    'AMZN',           # Amazon
    'META',           # Meta (Facebook)
    'NFLX',           # Netflix
    'PLTR',           # Palantir
    'COIN',           # Coinbase
    'SQ',             # Block (Square)
    'SHOP',           # Shopify
    'ROKU',           # Roku
    'SNOW',           # Snowflake
    'CRWD',           # CrowdStrike
    'DDOG',           # Datadog
    
    # === ACTIONS EUR (Blue Chips) ===
    'AI.PA',          # Air Liquide
    'MC.PA',          # LVMH
    'OR.PA',          # L'Oréal
    'SAN.PA',         # Sanofi
    'AIR.PA',         # Airbus
    'SAP.DE',         # SAP
    'ASML.AS',        # ASML
    
    # === FOREX - Paires vs EUR (pour portefeuille EUR) ===
    # Format: on achète la devise cotée contre EUR, prix = combien d'EUR pour 1 unité
    'USDEUR=X',       # USD/EUR - Dollar US
    'AUDEUR=X',       # AUD/EUR - Dollar Australien
    'GBPEUR=X',       # GBP/EUR - Livre Sterling
    'CHFEUR=X',       # CHF/EUR - Franc Suisse
    'JPYEUR=X',       # JPY/EUR - Yen (pour 1 JPY)
    'CADEUR=X',       # CAD/EUR - Dollar Canadien
    'NZDEUR=X',       # NZD/EUR - Dollar Néo-Zélandais
    'SEKEUR=X',       # SEK/EUR - Couronne Suédoise
    'NOKEUR=X',       # NOK/EUR - Couronne Norvégienne
    'SGDEUR=X',       # SGD/EUR - Dollar Singapourien
    
    # === MÉTAUX PRÉCIEUX EN EUR ===
    '4GLD.DE',        # Xetra-Gold (coté en EUR)
    'VZLE.DE',        # WisdomTree Physical Silver EUR
    # Retirer EGLN.L, PHAU.L, PHAG.L qui sont en GBP
    # Ou les garder si tu veux aussi suivre des métaux en GBP
    
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
    'ATOM-EUR',       # Cosmos EUR
    'NEAR-EUR',       # Near Protocol EUR
    'AAVE-EUR',       # Aave EUR
    'SHIB-EUR',       # Shiba Inu EUR
]

# === NOMS COMPLETS DES ACTIFS (pour affichage) ===
ASSET_NAMES = {
    # Indices
    '^GSPC': 'S&P 500',
    '^DJI': 'Dow Jones',
    '^IXIC': 'NASDAQ Composite',
    '^NDX': 'NASDAQ 100',
    '^STOXX50E': 'Euro Stoxx 50',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    
    # ETF Indices
    'IWDA.AS': 'iShares MSCI World',
    'EUNL.DE': 'iShares MSCI World UCITS',
    'CW8.PA': 'Amundi MSCI World',
    'EWLD.PA': 'Lyxor MSCI World',
    'MWRD.DE': 'Amundi MSCI World II',
    'SXR8.DE': 'iShares S&P 500 UCITS',
    'VUAA.DE': 'Vanguard S&P 500 UCITS',
    'SPY': 'SPDR S&P 500',
    'QQQ': 'Invesco NASDAQ 100',
    'VOO': 'Vanguard S&P 500',
    
    # Blue Chips US
    'AAPL': 'Apple',
    'MSFT': 'Microsoft',
    'GOOGL': 'Alphabet (Google)',
    'GOOG': 'Alphabet (Google)',
    'JNJ': 'Johnson & Johnson',
    'JPM': 'JPMorgan Chase',
    'V': 'Visa',
    'MA': 'Mastercard',
    'PG': 'Procter & Gamble',
    'KO': 'Coca-Cola',
    'PEP': 'PepsiCo',
    'MCD': "McDonald's",
    'WMT': 'Walmart',
    'HD': 'Home Depot',
    'DIS': 'Disney',
    'CSCO': 'Cisco',
    'INTC': 'Intel',
    'VZ': 'Verizon',
    'T': 'AT&T',
    'IBM': 'IBM',
    'GE': 'General Electric',
    'BA': 'Boeing',
    'CAT': 'Caterpillar',
    'MMM': '3M',
    'AXP': 'American Express',
    'GS': 'Goldman Sachs',
    'UNH': 'UnitedHealth',
    'CVX': 'Chevron',
    'XOM': 'ExxonMobil',
    
    # Tech Volatile US
    'TSLA': 'Tesla',
    'NVDA': 'NVIDIA',
    'AMD': 'AMD',
    'AMZN': 'Amazon',
    'META': 'Meta (Facebook)',
    'NFLX': 'Netflix',
    'PLTR': 'Palantir',
    'SQ': 'Block (Square)',
    'SHOP': 'Shopify',
    'ROKU': 'Roku',
    'SNAP': 'Snap',
    'PINS': 'Pinterest',
    'COIN': 'Coinbase',
    'MARA': 'Marathon Digital',
    'RIOT': 'Riot Platforms',
    'HOOD': 'Robinhood',
    'RIVN': 'Rivian',
    'LCID': 'Lucid Motors',
    'NIO': 'NIO',
    'XPEV': 'XPeng',
    'LI': 'Li Auto',
    'MU': 'Micron',
    'MRVL': 'Marvell',
    'AVGO': 'Broadcom',
    'ARM': 'ARM Holdings',
    'SMCI': 'Super Micro Computer',
    'SNOW': 'Snowflake',
    'CRWD': 'CrowdStrike',
    'DDOG': 'Datadog',
    'ZS': 'Zscaler',
    'NET': 'Cloudflare',
    'ABNB': 'Airbnb',
    'UBER': 'Uber',
    'LYFT': 'Lyft',
    'DASH': 'DoorDash',
    
    # Blue Chips EUR
    'AI.PA': 'Air Liquide',
    'MC.PA': 'LVMH',
    'OR.PA': "L'Oréal",
    'SAN.PA': 'Sanofi',
    'TTE.PA': 'TotalEnergies',
    'BNP.PA': 'BNP Paribas',
    'ACA.PA': 'Crédit Agricole',
    'SU.PA': 'Schneider Electric',
    'AIR.PA': 'Airbus',
    'SAF.PA': 'Safran',
    'DG.PA': 'Vinci',
    'KER.PA': 'Kering',
    'RI.PA': 'Pernod Ricard',
    'CAP.PA': 'Capgemini',
    'CS.PA': 'AXA',
    'BN.PA': 'Danone',
    'ENGI.PA': 'Engie',
    'ORA.PA': 'Orange',
    'VIV.PA': 'Vivendi',
    'SAP.DE': 'SAP',
    'SIE.DE': 'Siemens',
    'ALV.DE': 'Allianz',
    'BAS.DE': 'BASF',
    'BAYN.DE': 'Bayer',
    'BMW.DE': 'BMW',
    'MBG.DE': 'Mercedes-Benz',
    'VOW3.DE': 'Volkswagen',
    'DTE.DE': 'Deutsche Telekom',
    'DBK.DE': 'Deutsche Bank',
    'MUV2.DE': 'Munich Re',
    'ADS.DE': 'Adidas',
    'ASML.AS': 'ASML',
    'PHIA.AS': 'Philips',
    'UNA.AS': 'Unilever',
    'INGA.AS': 'ING',
    'HEIA.AS': 'Heineken',
    
    # Forex EUR (inversées pour portefeuille EUR)
    'USDEUR=X': 'Dollar US',
    'AUDEUR=X': 'Dollar Australien',
    'GBPEUR=X': 'Livre Sterling',
    'CHFEUR=X': 'Franc Suisse',
    'JPYEUR=X': 'Yen Japonais',
    'CADEUR=X': 'Dollar Canadien',
    'NZDEUR=X': 'Dollar Néo-Zélandais',
    'SEKEUR=X': 'Couronne Suédoise',
    'NOKEUR=X': 'Couronne Norvégienne',
    'DKKEUR=X': 'Couronne Danoise',
    'PLNEUR=X': 'Zloty Polonais',
    'HUFEUR=X': 'Forint Hongrois',
    'CZKEUR=X': 'Couronne Tchèque',
    'TRYEUR=X': 'Lire Turque',
    'ZAREUR=X': 'Rand Sud-Africain',
    'MXNEUR=X': 'Peso Mexicain',
    'SGDEUR=X': 'Dollar Singapourien',
    'HKDEUR=X': 'Dollar Hong Kong',
    'CNYEUR=X': 'Yuan Chinois',
    'INREUR=X': 'Roupie Indienne',
    'KRWEUR=X': 'Won Coréen',
    # Anciennes paires (pour compatibilité)
    'EURJPY=X': 'EUR/JPY',
    'EURGBP=X': 'EUR/GBP',
    'EURCHF=X': 'EUR/CHF',
    'EURAUD=X': 'EUR/AUD',
    'EURCAD=X': 'EUR/CAD',
    'EURNZD=X': 'EUR/NZD',
    'EURUSD=X': 'EUR/USD',
    
    # Métaux Précieux EUR
    'EGLN.L': 'Gold ETC EUR',
    'PHAU.L': 'Physical Gold',
    'PHAG.L': 'Physical Silver',
    '4GLD.DE': 'Xetra-Gold',
    'VZLE.DE': 'Silver EUR',
    'PPLT': 'Physical Platinum',
    'GC=F': 'Gold Futures',
    'SI=F': 'Silver Futures',
    'PL=F': 'Platinum Futures',
    'PA=F': 'Palladium Futures',
    'GLD': 'SPDR Gold',
    'SLV': 'iShares Silver',
    'IAU': 'iShares Gold',
    
    # Crypto EUR
    'BTC-EUR': 'Bitcoin',
    'ETH-EUR': 'Ethereum',
    'SOL-EUR': 'Solana',
    'XRP-EUR': 'Ripple (XRP)',
    'ADA-EUR': 'Cardano',
    'DOGE-EUR': 'Dogecoin',
    'DOT-EUR': 'Polkadot',
    'LINK-EUR': 'Chainlink',
    'AVAX-EUR': 'Avalanche',
    'MATIC-EUR': 'Polygon',
    'UNI-EUR': 'Uniswap',
    'LTC-EUR': 'Litecoin',
    'BCH-EUR': 'Bitcoin Cash',
    'ATOM-EUR': 'Cosmos',
    'NEAR-EUR': 'Near Protocol',
    'FTM-EUR': 'Fantom',
    'ALGO-EUR': 'Algorand',
    'XLM-EUR': 'Stellar',
    'AAVE-EUR': 'Aave',
    'MKR-EUR': 'Maker',
    'CRV-EUR': 'Curve',
    'SHIB-EUR': 'Shiba Inu',
    'PEPE-EUR': 'Pepe',
    
    # Crypto USD
    'BTC-USD': 'Bitcoin',
    'ETH-USD': 'Ethereum',
    'SOL-USD': 'Solana',
    'XRP-USD': 'Ripple (XRP)',
    'ADA-USD': 'Cardano',
    'DOGE-USD': 'Dogecoin',
}

# === DEVISES PAR ASSET ===
def get_asset_currency(ticker):
    """Retourne la devise d'un actif."""
    ticker = ticker.upper()
    
    # Crypto EUR
    if '-EUR' in ticker:
        return 'EUR'
    
    # Crypto USD
    if '-USD' in ticker:
        return 'USD'
    
    # Forex - la devise de cotation
    if '=X' in ticker:
        # Format XXXYYY=X -> cotation en YYY
        pair = ticker.replace('=X', '')
        if len(pair) == 6:
            return pair[3:6]
        return 'USD'
    
    # ETC/ETF métaux précieux - CORRECTION
    # Les ETC cotés à Londres (.L) sont en GBP sauf indication contraire
    gbp_etcs = ['EGLN.L', 'PHAU.L', 'PHAG.L', 'SGLN.L', 'SSLN.L']
    if ticker in gbp_etcs:
        return 'GBP'
    
    # ETC cotés en EUR (Xetra, etc.)
    eur_etcs = ['4GLD.DE', 'VZLE.DE', 'EWG2.DE', 'PPFB.DE']
    if ticker in eur_etcs:
        return 'EUR'
    
    # Actions européennes par extension
    if ticker.endswith('.PA') or ticker.endswith('.DE') or ticker.endswith('.AS'):
        return 'EUR'
    if ticker.endswith('.L'):
        return 'GBP'  # Par défaut pour Londres
    if ticker.endswith('.MI'):
        return 'EUR'
    if ticker.endswith('.MC'):
        return 'EUR'
    
    # ETF européens connus (cotés en EUR)
    eur_etfs = ['IWDA.AS', 'EUNL.DE', 'CW8.PA', 'EWLD.PA', 'MWRD.DE', 'SXR8.DE', 
                'VUAA.DE', 'EXSA.DE', 'MEUD.PA']
    if ticker in eur_etfs:
        return 'EUR'
    
    # Futures
    if '=F' in ticker:
        return 'USD'
    
    # Indices
    if ticker.startswith('^'):
        if ticker in ['^GDAXI', '^FCHI', '^STOXX50E', '^AEX']:
            return 'EUR'
        if ticker == '^FTSE':
            return 'GBP'
        return 'USD'
    
    # Par défaut (actions US)
    return 'USD'

def get_currency_symbol(currency):
    """Retourne le symbole d'une devise."""
    symbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
        'JPY': '¥',
        'CHF': 'CHF',
        'AUD': 'A$',
        'CAD': 'C$',
        'NZD': 'NZ$',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'PLN': 'zł',
        'HUF': 'Ft',
        'CZK': 'Kč',
        'TRY': '₺',
        'ZAR': 'R',
        'MXN': '$',
        'SGD': 'S$',
        'HKD': 'HK$',
        'CNY': '¥',
        'INR': '₹',
        'KRW': '₩',
    }
    return symbols.get(currency, currency)


def get_asset_name(ticker):
    """Retourne le nom complet d'un actif."""
    return ASSET_NAMES.get(ticker.upper(), ticker)


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
    'blue_chip_us': {
        'name': 'Blue Chip US',
        'description': 'Actions US stables (Apple, Microsoft, Coca-Cola, J&J...)',
        'icon': '🇺🇸',
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
    
    'tech_volatile_us': {
        'name': 'Tech Volatile US',
        'description': 'Tech US à forte volatilité (Tesla, NVIDIA, AMD, Amazon, Meta...)',
        'icon': '⚡🇺🇸',
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
    
    'blue_chip_eur': {
        'name': 'Blue Chip EUR',
        'description': 'Actions européennes stables (LVMH, Air Liquide, SAP...)',
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
    
    'forex_eur': {
        'name': 'Forex vs EUR',
        'description': 'Devises vs EUR pour portefeuille EUR (USD, AUD, GBP...)',
        'icon': '💱🇪🇺',
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
    
    'precious_metals_eur': {
        'name': 'Métaux Précieux EUR',
        'description': 'Or, Argent cotés en EUR (4GLD.DE, VZLE.DE...)',
        'icon': '🥇🇪🇺',
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
    
    'precious_metals': {
        'name': 'Métaux Précieux USD',
        'description': 'Or, Argent, Platine en USD (GC=F, SI=F, GLD...)',
        'icon': '🥇',
        'color': '#d4af37',
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
        'description': 'Indices boursiers (S&P 500, NASDAQ, DAX, CAC 40...)',
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
        'description': 'ETF sectoriels et thématiques',
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
        'description': 'Pétrole, Gaz, Blé, etc.',
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
    'AAPL': 'blue_chip_us', 'MSFT': 'blue_chip_us', 'GOOGL': 'blue_chip_us', 'GOOG': 'blue_chip_us',
    'JNJ': 'blue_chip_us', 'JPM': 'blue_chip_us',
    'V': 'blue_chip_us', 'MA': 'blue_chip_us', 'PG': 'blue_chip_us', 'KO': 'blue_chip_us',
    'PEP': 'blue_chip_us', 'MCD': 'blue_chip_us', 'WMT': 'blue_chip_us', 'HD': 'blue_chip_us',
    'DIS': 'blue_chip_us', 'CSCO': 'blue_chip_us', 'INTC': 'blue_chip_us',
    'VZ': 'blue_chip_us', 'T': 'blue_chip_us', 'IBM': 'blue_chip_us', 'GE': 'blue_chip_us',
    'BA': 'blue_chip_us', 'CAT': 'blue_chip_us', 'MMM': 'blue_chip_us', 'AXP': 'blue_chip_us',
    'GS': 'blue_chip_us', 'UNH': 'blue_chip_us', 'CVX': 'blue_chip_us', 'XOM': 'blue_chip_us',
    'BRK-B': 'blue_chip_us', 'BRK.B': 'blue_chip_us',
    
    # ============================================================
    # TECH VOLATILE US (Growth / Momentum)
    # ============================================================
    'TSLA': 'tech_volatile_us', 'NVDA': 'tech_volatile_us', 'AMD': 'tech_volatile_us',
    'AMZN': 'tech_volatile_us', 'META': 'tech_volatile_us', 'NFLX': 'tech_volatile_us',
    'PLTR': 'tech_volatile_us', 'SQ': 'tech_volatile_us', 'SHOP': 'tech_volatile_us',
    'ROKU': 'tech_volatile_us', 'SNAP': 'tech_volatile_us', 'PINS': 'tech_volatile_us',
    'COIN': 'tech_volatile_us', 'MARA': 'tech_volatile_us', 'RIOT': 'tech_volatile_us',
    'HOOD': 'tech_volatile_us', 'RIVN': 'tech_volatile_us', 'LCID': 'tech_volatile_us',
    'NIO': 'tech_volatile_us', 'XPEV': 'tech_volatile_us', 'LI': 'tech_volatile_us',
    'ARKK': 'tech_volatile_us', 'ARKG': 'tech_volatile_us', 'ARKF': 'tech_volatile_us',
    'SOXL': 'tech_volatile_us', 'TQQQ': 'tech_volatile_us', 'UPRO': 'tech_volatile_us',
    'MU': 'tech_volatile_us', 'MRVL': 'tech_volatile_us', 'AVGO': 'tech_volatile_us',
    'ARM': 'tech_volatile_us', 'SMCI': 'tech_volatile_us',
    'SNOW': 'tech_volatile_us', 'CRWD': 'tech_volatile_us', 'DDOG': 'tech_volatile_us',
    'ZS': 'tech_volatile_us', 'NET': 'tech_volatile_us',
    'ABNB': 'tech_volatile_us', 'UBER': 'tech_volatile_us', 'LYFT': 'tech_volatile_us',
    'DASH': 'tech_volatile_us', 'RBLX': 'tech_volatile_us', 'U': 'tech_volatile_us',
    
    # ============================================================
    # BLUE CHIPS EUROPÉENNES (EUR)
    # ============================================================
    'AI.PA': 'blue_chip_eur', 'MC.PA': 'blue_chip_eur', 'OR.PA': 'blue_chip_eur',
    'SAN.PA': 'blue_chip_eur', 'TTE.PA': 'blue_chip_eur', 'BNP.PA': 'blue_chip_eur',
    'ACA.PA': 'blue_chip_eur', 'SU.PA': 'blue_chip_eur', 'AIR.PA': 'blue_chip_eur',
    'SAF.PA': 'blue_chip_eur', 'DG.PA': 'blue_chip_eur', 'KER.PA': 'blue_chip_eur',
    'RI.PA': 'blue_chip_eur', 'CAP.PA': 'blue_chip_eur', 'CS.PA': 'blue_chip_eur',
    'BN.PA': 'blue_chip_eur', 'ENGI.PA': 'blue_chip_eur', 'ORA.PA': 'blue_chip_eur',
    'VIV.PA': 'blue_chip_eur',
    'SAP.DE': 'blue_chip_eur', 'SIE.DE': 'blue_chip_eur', 'ALV.DE': 'blue_chip_eur',
    'BAS.DE': 'blue_chip_eur', 'BAYN.DE': 'blue_chip_eur', 'BMW.DE': 'blue_chip_eur',
    'MBG.DE': 'blue_chip_eur', 'VOW3.DE': 'blue_chip_eur', 'DTE.DE': 'blue_chip_eur',
    'DBK.DE': 'blue_chip_eur', 'MUV2.DE': 'blue_chip_eur', 'ADS.DE': 'blue_chip_eur',
    'ASML.AS': 'blue_chip_eur', 'PHIA.AS': 'blue_chip_eur', 'UNA.AS': 'blue_chip_eur',
    'INGA.AS': 'blue_chip_eur', 'HEIA.AS': 'blue_chip_eur',
    'SAN.MC': 'blue_chip_eur', 'BBVA.MC': 'blue_chip_eur', 'ITX.MC': 'blue_chip_eur',
    'IBE.MC': 'blue_chip_eur', 'TEF.MC': 'blue_chip_eur',
    'ENI.MI': 'blue_chip_eur', 'ENEL.MI': 'blue_chip_eur', 'ISP.MI': 'blue_chip_eur',
    'UCG.MI': 'blue_chip_eur',
    
    # ============================================================
    # CRYPTO VS USD
    # ============================================================
    'BTC-USD': 'crypto', 'ETH-USD': 'crypto', 'SOL-USD': 'crypto',
    'XRP-USD': 'crypto', 'ADA-USD': 'crypto', 'DOGE-USD': 'crypto',
    'DOT-USD': 'crypto', 'LINK-USD': 'crypto', 'AVAX-USD': 'crypto',
    'MATIC-USD': 'crypto', 'UNI-USD': 'crypto', 'ATOM-USD': 'crypto',
    'LTC-USD': 'crypto', 'BCH-USD': 'crypto', 'NEAR-USD': 'crypto',
    
    # ============================================================
    # CRYPTO VS EUR
    # ============================================================
    'BTC-EUR': 'crypto_eur', 'ETH-EUR': 'crypto_eur', 'SOL-EUR': 'crypto_eur',
    'XRP-EUR': 'crypto_eur', 'ADA-EUR': 'crypto_eur', 'DOGE-EUR': 'crypto_eur',
    'DOT-EUR': 'crypto_eur', 'LINK-EUR': 'crypto_eur', 'AVAX-EUR': 'crypto_eur',
    'MATIC-EUR': 'crypto_eur', 'UNI-EUR': 'crypto_eur', 'LTC-EUR': 'crypto_eur',
    'BCH-EUR': 'crypto_eur', 'ATOM-EUR': 'crypto_eur', 'NEAR-EUR': 'crypto_eur',
    'FTM-EUR': 'crypto_eur', 'ALGO-EUR': 'crypto_eur', 'XLM-EUR': 'crypto_eur',
    'AAVE-EUR': 'crypto_eur', 'MKR-EUR': 'crypto_eur', 'CRV-EUR': 'crypto_eur',
    'SHIB-EUR': 'crypto_eur', 'PEPE-EUR': 'crypto_eur',
    
    # ============================================================
    # FOREX VS EUR (paires inversées pour portefeuille EUR)
    # ============================================================
    'USDEUR=X': 'forex_eur', 'AUDEUR=X': 'forex_eur', 'GBPEUR=X': 'forex_eur',
    'CHFEUR=X': 'forex_eur', 'JPYEUR=X': 'forex_eur', 'CADEUR=X': 'forex_eur',
    'NZDEUR=X': 'forex_eur', 'SEKEUR=X': 'forex_eur', 'NOKEUR=X': 'forex_eur',
    'DKKEUR=X': 'forex_eur', 'PLNEUR=X': 'forex_eur', 'HUFEUR=X': 'forex_eur',
    'CZKEUR=X': 'forex_eur', 'TRYEUR=X': 'forex_eur', 'ZAREUR=X': 'forex_eur',
    'MXNEUR=X': 'forex_eur', 'SGDEUR=X': 'forex_eur', 'HKDEUR=X': 'forex_eur',
    'CNYEUR=X': 'forex_eur', 'INREUR=X': 'forex_eur', 'KRWEUR=X': 'forex_eur',
    # Anciennes paires (compatibilité)
    'EURJPY=X': 'forex_eur', 'EURGBP=X': 'forex_eur', 'EURCHF=X': 'forex_eur',
    'EURAUD=X': 'forex_eur', 'EURCAD=X': 'forex_eur', 'EURNZD=X': 'forex_eur',
    'EURUSD=X': 'forex_eur',
    
    # ============================================================
    # MÉTAUX PRÉCIEUX - Correction des devises
    # ============================================================
    # ETCs cotés à Londres (GBP) - à mettre dans precious_metals (USD/GBP)
    'EGLN.L': 'precious_metals',      # WisdomTree Physical Gold - GBP
    'PHAU.L': 'precious_metals',      # Physical Gold - GBP  
    'PHAG.L': 'precious_metals',      # Physical Silver - GBP
    'SGLN.L': 'precious_metals',      # iShares Physical Gold - GBP
    
    # ETCs cotés en EUR (Xetra)
    '4GLD.DE': 'precious_metals_eur', # Xetra-Gold - EUR
    'VZLE.DE': 'precious_metals_eur', # WisdomTree Physical Silver - EUR
    'EWG2.DE': 'precious_metals_eur', # Xetra-Gold - EUR
    
    # Futures et ETF USD
    'GC=F': 'precious_metals',        # Gold Futures - USD
    'SI=F': 'precious_metals',        # Silver Futures - USD
    'PL=F': 'precious_metals',        # Platinum Futures - USD
    'PA=F': 'precious_metals',        # Palladium Futures - USD
    'GLD': 'precious_metals',         # SPDR Gold - USD
    'SLV': 'precious_metals',         # iShares Silver - USD
    'IAU': 'precious_metals',         # iShares Gold - USD
    'PPLT': 'precious_metals',        # Physical Platinum - USD
    
    # ============================================================
    # INDICES MAJEURS
    # ============================================================
    '^GSPC': 'indices', '^DJI': 'indices', '^IXIC': 'indices', '^NDX': 'indices',
    '^RUT': 'indices', '^VIX': 'indices',
    '^STOXX50E': 'indices', '^GDAXI': 'indices', '^FCHI': 'indices',
    '^FTSE': 'indices', '^IBEX': 'indices', '^FTSEMIB.MI': 'indices',
    '^AEX': 'indices', '^SSMI': 'indices',
    '^N225': 'indices', '^HSI': 'indices', '000001.SS': 'indices',
    'SPY': 'indices', 'QQQ': 'indices', 'DIA': 'indices', 'IWM': 'indices',
    'VOO': 'indices', 'VTI': 'indices', 'IVV': 'indices',
    'IWDA.AS': 'indices', 'SWDA.L': 'indices', 'VWCE.DE': 'indices',
    'VWRL.AS': 'indices', 'CSPX.L': 'indices', 'SXR8.DE': 'indices',
    'VUAA.DE': 'indices', 'EUNL.DE': 'indices', 'EXSA.DE': 'indices',
    'MEUD.PA': 'indices', 'CW8.PA': 'indices', 'EWLD.PA': 'indices',
    'MWRD.DE': 'indices',
    
    # ============================================================
    # ETF SECTORIELS
    # ============================================================
    'XLF': 'etf_sector', 'XLE': 'etf_sector', 'XLK': 'etf_sector',
    'XLV': 'etf_sector', 'XLI': 'etf_sector', 'XLY': 'etf_sector',
    'XLP': 'etf_sector', 'XLU': 'etf_sector', 'XLB': 'etf_sector',
    'XLRE': 'etf_sector', 'XLC': 'etf_sector',
    
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
    
    # Forex vs EUR (nouvelles paires inversées)
    if '=X' in ticker:
        pair = ticker.replace('=X', '')
        if pair.endswith('EUR'):
            return 'forex_eur'
        if pair.startswith('EUR'):
            return 'forex_eur'
        return 'forex_eur'  # Par défaut forex
    
    # Actions européennes par extension
    if ticker.endswith('.PA') or ticker.endswith('.DE') or ticker.endswith('.AS'):
        return 'blue_chip_eur'
    if ticker.endswith('.MC') or ticker.endswith('.MI'):
        return 'blue_chip_eur'
    if ticker.endswith('.L'):
        # Vérifier si c'est un ETC métaux
        if any(metal in ticker.upper() for metal in ['GOLD', 'SILV', 'PLAT', 'PALL', 'PHAU', 'PHAG', 'EGLN']):
            return 'precious_metals_eur'
        return 'blue_chip_eur'
    
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
            return 'forex_eur'
        elif quote_type == 'ETF':
            short_name = ticker_info.get('shortName', '').upper()
            if any(x in short_name for x in ['S&P 500', 'NASDAQ', 'DOW', 'RUSSELL', 'TOTAL MARKET', 'MSCI WORLD', 'FTSE']):
                return 'indices'
            if any(x in short_name for x in ['GOLD', 'SILVER', 'PRECIOUS']):
                return 'precious_metals_eur' if currency == 'EUR' else 'precious_metals'
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
            beta = ticker_info.get('beta', 1.0)
            market_cap = ticker_info.get('marketCap', 0)
            
            # Actions EUR
            if currency == 'EUR':
                return 'blue_chip_eur'
            
            # Tech volatile US
            if sector == 'Technology':
                if beta and beta > 1.3:
                    return 'tech_volatile_us'
                elif market_cap and market_cap > 500e9:
                    return 'blue_chip_us'
                else:
                    return 'tech_volatile_us'
            
            # Consumer / Growth volatile
            if sector == 'Consumer Cyclical':
                if beta and beta > 1.3:
                    return 'tech_volatile_us'
                return 'blue_chip_us'
            
            # Blue chips US par défaut
            if market_cap and market_cap > 100e9:
                return 'blue_chip_us'
    
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
        
        cursor.execute("DELETE FROM user_assets")
        conn.commit()
        
        cursor.close()
        conn.close()
        
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