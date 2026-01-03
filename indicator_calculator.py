# indicator_calculator.py
"""
Module de calcul des indicateurs techniques.
VERSION 2.4 - Correction du passage de config + debug amélioré
"""
import pandas as pd
import pandas_ta as ta
from config import (
    RSI, STOCHASTIC, MOVING_AVERAGES, MACD, ADX, BOLLINGER,
    SIGNAL_WEIGHTS, INDIVIDUAL_WEIGHTS, COMBINATION_WEIGHTS,
    DECISION, TREND, DIVERGENCE, SIGNAL_TIMEFRAME,
    get_default_config
)

# === FLAG DE DEBUG ===
DEBUG_RECOMMENDATIONS = True  # Mettre à True pour voir les détails
DEBUG_CONFIG = True  # Debug de la config reçue


# Patterns qui sont TOUJOURS neutres
NEUTRAL_PATTERNS = {
    'DOJI', 'DOJISTAR', 'LONGLEGGEDOJI', 'LONGLEGGEDDOJI',
    'SPINNINGTOP', 'HIGHWAVE', 'RICKSHAWMAN',
    'INSIDE',
    'SHORTLINE', 'LONGLINE',
}


def get_pattern_with_direction(candle_patterns_row):
    """Analyse une ligne de patterns et retourne (pattern_name, direction)."""
    non_zero = candle_patterns_row[candle_patterns_row != 0]
    
    if len(non_zero) == 0:
        return 'Aucun', 'neutral'
    
    abs_values = non_zero.abs()
    pattern_col = abs_values.idxmax()
    pattern_value = non_zero[pattern_col]
    pattern_name = pattern_col.replace('CDL_', '')
    
    if pattern_name in NEUTRAL_PATTERNS:
        return pattern_name, 'neutral'
    
    if pattern_value > 0:
        direction = 'bullish'
    elif pattern_value < 0:
        direction = 'bearish'
    else:
        direction = 'neutral'
    
    return pattern_name, direction


def calculate_all_indicators(df, config=None):
    """Calcule tous les indicateurs techniques."""
    if config is None:
        config = get_default_config()
        if DEBUG_CONFIG:
            print("⚠️ calculate_all_indicators appelé avec config=None, utilisation des valeurs par défaut")
    else:
        if DEBUG_CONFIG:
            ind_weights = config.get('individual_weights', {})
            print(f"✅ calculate_all_indicators appelé avec config personnalisée")
            print(f"   individual_weights reçus: rsi_extreme={ind_weights.get('rsi_extreme')}, "
                  f"stoch_cross={ind_weights.get('stoch_cross')}, "
                  f"macd_histogram={ind_weights.get('macd_histogram')}, "
                  f"rsi_divergence={ind_weights.get('rsi_divergence')}, "
                  f"adx_direction={ind_weights.get('adx_direction')}")
    
    rsi_cfg = config.get('rsi', RSI)
    stoch_cfg = config.get('stochastic', STOCHASTIC)
    ma_cfg = config.get('moving_averages', MOVING_AVERAGES)
    macd_cfg = config.get('macd', MACD)
    adx_cfg = config.get('adx', ADX)
    bb_cfg = config.get('bollinger', BOLLINGER)
    
    # === INDICATEURS DE MOMENTUM ===
    df.ta.stoch(k=stoch_cfg['k_period'], d=stoch_cfg['d_period'], append=True)
    df.ta.rsi(length=rsi_cfg['period'], append=True)
    
    # === BANDES DE BOLLINGER ===
    df.ta.bbands(length=bb_cfg['period'], std=bb_cfg['std_dev'], append=True)
    
    # === INDICATEURS DE TENDANCE ===
    df.ta.sma(length=ma_cfg['sma_short'], append=True)
    df.ta.sma(length=ma_cfg['sma_medium'], append=True)
    df.ta.sma(length=ma_cfg['sma_long'], append=True)
    df.ta.ema(length=ma_cfg['ema_fast'], append=True)
    df.ta.ema(length=ma_cfg['ema_slow'], append=True)
    df.ta.macd(fast=macd_cfg['fast'], slow=macd_cfg['slow'], signal=macd_cfg['signal'], append=True)
    df.ta.adx(length=adx_cfg['period'], append=True)
    
    # Renommer les colonnes
    rename_map = {
        f'STOCHk_{stoch_cfg["k_period"]}_{stoch_cfg["d_period"]}_3': 'stochastic_k',
        f'STOCHd_{stoch_cfg["k_period"]}_{stoch_cfg["d_period"]}_3': 'stochastic_d',
        f'RSI_{rsi_cfg["period"]}': 'rsi',
        f'SMA_{ma_cfg["sma_short"]}': 'sma_20',
        f'SMA_{ma_cfg["sma_medium"]}': 'sma_50',
        f'SMA_{ma_cfg["sma_long"]}': 'sma_200',
        f'EMA_{ma_cfg["ema_fast"]}': 'ema_12',
        f'EMA_{ma_cfg["ema_slow"]}': 'ema_26',
        f'MACD_{macd_cfg["fast"]}_{macd_cfg["slow"]}_{macd_cfg["signal"]}': 'macd',
        f'MACDh_{macd_cfg["fast"]}_{macd_cfg["slow"]}_{macd_cfg["signal"]}': 'macd_histogram',
        f'MACDs_{macd_cfg["fast"]}_{macd_cfg["slow"]}_{macd_cfg["signal"]}': 'macd_signal',
        f'ADX_{adx_cfg["period"]}': 'adx',
        f'DMP_{adx_cfg["period"]}': 'di_plus',
        f'DMN_{adx_cfg["period"]}': 'di_minus',
    }
    
    # Chercher les colonnes Bollinger
    for col in df.columns:
        if col.startswith('BBL_'):
            rename_map[col] = 'bb_lower'
        elif col.startswith('BBM_'):
            rename_map[col] = 'bb_middle'
        elif col.startswith('BBU_'):
            rename_map[col] = 'bb_upper'
        elif col.startswith('BBB_'):
            rename_map[col] = 'bb_bandwidth'
        elif col.startswith('BBP_'):
            rename_map[col] = 'bb_percent'
    
    existing_cols = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols, inplace=True)

    df['bb_signal'] = calculate_bollinger_signal(df, config)
    df['trend'] = calculate_trend(df, config)
    
    divergence_cfg = config.get('divergence', DIVERGENCE)
    df['rsi_divergence'] = detect_rsi_divergence(df, lookback=divergence_cfg['lookback_period'], config=config)

    candle_patterns = df.ta.cdl_pattern(name="all")
    
    patterns_list = []
    directions_list = []
    
    for idx in range(len(df)):
        pattern_row = candle_patterns.iloc[idx]
        pattern_name, direction = get_pattern_with_direction(pattern_row)
        patterns_list.append(pattern_name)
        directions_list.append(direction)
    
    df['pattern'] = patterns_list
    df['pattern_direction'] = directions_list

    signal_timeframe = config.get('signal_timeframe', 1)
    
    # Passer explicitement la config à chaque appel
    results = df.apply(
        lambda row: calculate_recommendation_v4(row, df, config, signal_timeframe), 
        axis=1
    )
    
    df['recommendation'] = [r[0] for r in results]
    df['conviction'] = [r[1] for r in results]
    df['active_combinations'] = [r[2] for r in results]

    return df


def calculate_bollinger_signal(df, config=None):
    """Calcule le signal Bollinger pour chaque ligne."""
    if config is None:
        config = get_default_config()
    
    bb_cfg = config.get('bollinger', BOLLINGER)
    squeeze_threshold = bb_cfg.get('squeeze_threshold', 0.05)
    
    signals = []
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        close = row.get('Close', 0)
        bb_lower = row.get('bb_lower')
        bb_upper = row.get('bb_upper')
        bb_middle = row.get('bb_middle')
        bb_bandwidth = row.get('bb_bandwidth')
        
        if pd.isna(bb_lower) or pd.isna(bb_upper) or pd.isna(close):
            signals.append('neutral')
            continue
        
        bb_range = bb_upper - bb_lower
        position = (close - bb_lower) / bb_range if bb_range > 0 else 0.5
        
        if bb_bandwidth is not None and bb_middle is not None and bb_middle > 0:
            bandwidth_pct = bb_bandwidth / bb_middle * 100
            if bandwidth_pct < squeeze_threshold * 100:
                signals.append('squeeze')
                continue
        
        if position <= 0.05:
            signals.append('lower_touch')
        elif position >= 0.95:
            signals.append('upper_touch')
        elif position <= 0.20:
            signals.append('lower_zone')
        elif position >= 0.80:
            signals.append('upper_zone')
        else:
            signals.append('neutral')
    
    return signals


def calculate_trend(df, config=None):
    """Détermine la tendance basée sur les moyennes mobiles et l'ADX."""
    if config is None:
        config = get_default_config()
    
    trend_cfg = config.get('trend', TREND)
    adx_cfg = config.get('adx', ADX)
    
    trends = []
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        
        if pd.isna(row.get('sma_200')) or pd.isna(row.get('sma_50')):
            trends.append('neutral')
            continue
        
        close = row['Close']
        sma_20 = row.get('sma_20', close)
        sma_50 = row.get('sma_50', close)
        sma_200 = row.get('sma_200', close)
        adx = row.get('adx', 20)
        di_plus = row.get('di_plus', 25)
        di_minus = row.get('di_minus', 25)
        
        weights = trend_cfg.get('weights', TREND['weights'])
        trend_score = 0
        
        if close > sma_20:
            trend_score += weights['price_vs_sma_short']
        else:
            trend_score -= weights['price_vs_sma_short']
            
        if close > sma_50:
            trend_score += weights['price_vs_sma_medium']
        else:
            trend_score -= weights['price_vs_sma_medium']
            
        if close > sma_200:
            trend_score += weights['price_vs_sma_long']
        else:
            trend_score -= weights['price_vs_sma_long']
        
        if sma_20 > sma_50 > sma_200:
            trend_score += weights['ma_alignment']
        elif sma_20 < sma_50 < sma_200:
            trend_score -= weights['ma_alignment']
        
        strong_trend = adx > adx_cfg['strong']
        
        if di_plus > di_minus:
            trend_score += weights['di_direction']
        else:
            trend_score -= weights['di_direction']
        
        strong_threshold = trend_cfg.get('strong_threshold', 5)
        weak_threshold = trend_cfg.get('weak_threshold', 2)
        
        if trend_score >= strong_threshold and strong_trend:
            trends.append('strong_bullish')
        elif trend_score >= weak_threshold:
            trends.append('bullish')
        elif trend_score <= -strong_threshold and strong_trend:
            trends.append('strong_bearish')
        elif trend_score <= -weak_threshold:
            trends.append('bearish')
        else:
            trends.append('neutral')
    
    return trends


def detect_rsi_divergence(df, lookback=14, config=None):
    """Détecte les divergences entre le prix et le RSI."""
    if config is None:
        config = get_default_config()
    
    div_cfg = config.get('divergence', DIVERGENCE)
    rsi_low = div_cfg.get('rsi_low_threshold', 40)
    rsi_high = div_cfg.get('rsi_high_threshold', 60)
    
    divergences = ['none'] * len(df)
    
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
    
    for i in range(lookback * 2 + window, len(df) - window):
        try:
            rsi = df['rsi'].iloc[i]
            price = df['Close'].iloc[i]
            
            if pd.isna(rsi):
                continue
            
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


# ============================================
# === FONCTIONS HELPER ===
# ============================================

def _safe_get(row, key, default=None):
    """Récupère une valeur de manière sécurisée."""
    keys_to_try = [key]
    if key == 'close':
        keys_to_try.append('Close')
    elif key == 'Close':
        keys_to_try.append('close')
    
    for k in keys_to_try:
        val = row.get(k, None)
        if val is not None and not (isinstance(val, float) and pd.isna(val)):
            return val
    return default


def _safe_num(row, key, default=0):
    """Récupère une valeur numérique de manière sécurisée."""
    val = _safe_get(row, key, default)
    if val is None:
        return default
    try:
        result = float(val)
        return default if pd.isna(result) else result
    except (ValueError, TypeError):
        return default


def _get_active_indicator_flags(config):
    """
    Retourne un dictionnaire indiquant quels indicateurs sont actifs (poids > 0).
    """
    ind_weights = config.get('individual_weights', INDIVIDUAL_WEIGHTS)
    comb_weights = config.get('combination_weights', COMBINATION_WEIGHTS)
    
    # Debug
    if DEBUG_CONFIG:
        print(f"   _get_active_indicator_flags - ind_weights keys: {list(ind_weights.keys())[:5]}...")
        print(f"   rsi_extreme={ind_weights.get('rsi_extreme', 'MISSING')}, "
              f"rsi_divergence={ind_weights.get('rsi_divergence', 'MISSING')}")
    
    # Un indicateur est actif si :
    # 1. Son poids individuel est > 0
    # OU
    # 2. Il est utilisé dans une combinaison active
    
    # D'abord, vérifier les poids individuels
    rsi_active = (ind_weights.get('rsi_extreme', 0) > 0 or 
                  ind_weights.get('rsi_exit_zone', 0) > 0)
    
    stoch_active = (ind_weights.get('stoch_cross', 0) > 0 or 
                    ind_weights.get('stoch_extreme', 0) > 0)
    
    macd_active = (ind_weights.get('macd_cross', 0) > 0 or 
                   ind_weights.get('macd_histogram', 0) > 0)
    
    trend_active = (ind_weights.get('trend_strong', 0) > 0 or 
                    ind_weights.get('trend_weak', 0) > 0)
    
    pattern_active = ind_weights.get('pattern_signal', 0) > 0
    
    divergence_active = ind_weights.get('rsi_divergence', 0) > 0
    
    bollinger_active = (ind_weights.get('bollinger_touch', 0) > 0 or 
                        ind_weights.get('bollinger_zone', 0) > 0)
    
    adx_active = ind_weights.get('adx_direction', 0) > 0
    
    # Ensuite, vérifier si des combinaisons actives utilisent ces indicateurs
    # (une combinaison peut activer un indicateur même si son poids individuel est 0)
    
    # Combinaisons qui utilisent RSI
    rsi_combos = ['rsi_low_stoch_bullish', 'rsi_high_stoch_bearish', 'bollinger_low_rsi_low', 
                  'bollinger_high_rsi_high', 'macd_cross_rsi_low', 'macd_cross_bearish_rsi_high',
                  'pattern_bullish_rsi_low', 'pattern_bearish_rsi_high', 'triple_confirm_buy',
                  'triple_confirm_sell', 'rsi_exit_oversold_stoch', 'rsi_exit_overbought_stoch',
                  'stoch_cross_bullish_rsi_low', 'stoch_cross_bearish_rsi_high']
    
    # Combinaisons qui utilisent Stoch
    stoch_combos = ['divergence_bullish_stoch', 'divergence_bearish_stoch', 'rsi_low_stoch_bullish',
                    'rsi_high_stoch_bearish', 'bollinger_low_stoch_bullish', 'bollinger_high_stoch_bearish',
                    'triple_confirm_buy', 'triple_confirm_sell', 'rsi_exit_oversold_stoch',
                    'rsi_exit_overbought_stoch', 'stoch_cross_bullish_rsi_low', 'stoch_cross_bearish_rsi_high']
    
    # Combinaisons qui utilisent MACD
    macd_combos = ['macd_cross_rsi_low', 'macd_cross_bearish_rsi_high', 'macd_bullish_trend_bullish',
                   'macd_bearish_trend_bearish', 'macd_positive_trend_bullish', 'macd_negative_trend_bearish',
                   'triple_confirm_buy', 'triple_confirm_sell', 'price_below_mas_macd_negative']
    
    # Combinaisons qui utilisent Divergence
    divergence_combos = ['divergence_bullish_stoch', 'divergence_bearish_stoch']
    
    # Combinaisons qui utilisent Bollinger
    bollinger_combos = ['bollinger_low_rsi_low', 'bollinger_high_rsi_high', 
                        'bollinger_low_stoch_bullish', 'bollinger_high_stoch_bearish']
    
    # Combinaisons qui utilisent ADX
    adx_combos = ['adx_strong_di_plus', 'adx_strong_di_minus']
    
    # Combinaisons qui utilisent Trend
    trend_combos = ['macd_bullish_trend_bullish', 'macd_bearish_trend_bearish',
                    'macd_positive_trend_bullish', 'macd_negative_trend_bearish',
                    'pattern_bullish_trend_bullish', 'pattern_bearish_trend_bearish']
    
    # Combinaisons qui utilisent Pattern
    pattern_combos = ['pattern_bullish_rsi_low', 'pattern_bearish_rsi_high',
                      'pattern_bullish_trend_bullish', 'pattern_bearish_trend_bearish']
    
    # Vérifier si des combinaisons sont actives
    def any_combo_active(combo_list):
        return any(comb_weights.get(c, 0) > 0 for c in combo_list)
    
    flags = {
        'rsi': rsi_active or any_combo_active(rsi_combos),
        'stoch': stoch_active or any_combo_active(stoch_combos),
        'macd': macd_active or any_combo_active(macd_combos),
        'trend': trend_active or any_combo_active(trend_combos),
        'pattern': pattern_active or any_combo_active(pattern_combos),
        'divergence': divergence_active or any_combo_active(divergence_combos),
        'bollinger': bollinger_active or any_combo_active(bollinger_combos),
        'adx': adx_active or any_combo_active(adx_combos),
    }
    
    if DEBUG_CONFIG:
        print(f"   Computed flags: {flags}")
    
    return flags


# ============================================
# === DÉTECTION DES COMBINAISONS ===
# ============================================

def detect_active_combinations(row, row_prev, config, active_flags):
    """
    Détecte les combinaisons actives.
    Ne retourne que les combinaisons dont le poids > 0.
    """
    active = {'buy': [], 'sell': []}
    
    comb_weights = config.get('combination_weights', COMBINATION_WEIGHTS)
    rsi_cfg = config.get('rsi', RSI)
    adx_cfg = config.get('adx', ADX)
    
    # Extraire les valeurs
    rsi = _safe_num(row, 'rsi', 50)
    rsi_prev = _safe_num(row_prev, 'rsi', 50) if row_prev else 50
    stoch_k = _safe_num(row, 'stochastic_k', 50)
    stoch_d = _safe_num(row, 'stochastic_d', 50)
    stoch_k_prev = _safe_num(row_prev, 'stochastic_k', 50) if row_prev else 50
    stoch_d_prev = _safe_num(row_prev, 'stochastic_d', 50) if row_prev else 50
    macd = _safe_num(row, 'macd', 0)
    macd_signal_val = _safe_num(row, 'macd_signal', 0)
    macd_hist = _safe_num(row, 'macd_histogram', 0)
    macd_prev = _safe_num(row_prev, 'macd', 0) if row_prev else 0
    macd_signal_prev = _safe_num(row_prev, 'macd_signal', 0) if row_prev else 0
    trend = _safe_get(row, 'trend', 'neutral')
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    rsi_div = _safe_get(row, 'rsi_divergence', 'none')
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    adx = _safe_num(row, 'adx', 0)
    di_plus = _safe_num(row, 'di_plus', 0)
    di_minus = _safe_num(row, 'di_minus', 0)
    close = _safe_num(row, 'close', 0) or _safe_num(row, 'Close', 0)
    sma_20 = _safe_num(row, 'sma_20', None)
    sma_50 = _safe_num(row, 'sma_50', None)
    
    # Croisements
    stoch_bullish_cross = stoch_k_prev <= stoch_d_prev and stoch_k > stoch_d
    stoch_bearish_cross = stoch_k_prev >= stoch_d_prev and stoch_k < stoch_d
    macd_bullish_cross = macd_prev <= macd_signal_prev and macd > macd_signal_val
    macd_bearish_cross = macd_prev >= macd_signal_prev and macd < macd_signal_val
    
    # === COMBINAISONS D'ACHAT ===
    # Chaque combinaison vérifie UNIQUEMENT son propre poids > 0
    
    # Divergence Haussière + Stoch
    if rsi_div == 'bullish' and stoch_k > stoch_d:
        if comb_weights.get('divergence_bullish_stoch', 0) > 0:
            active['buy'].append('divergence_bullish_stoch')
    
    # Triple Confirm Achat
    if rsi < 50 and stoch_k > stoch_d and macd_hist > 0:
        if comb_weights.get('triple_confirm_buy', 0) > 0:
            active['buy'].append('triple_confirm_buy')
    
    # MACD Croisement Haussier + RSI Bas
    if macd_bullish_cross and rsi < 50:
        if comb_weights.get('macd_cross_rsi_low', 0) > 0:
            active['buy'].append('macd_cross_rsi_low')
    
    # Bollinger Basse + RSI Bas
    if bb_signal in ['lower_touch', 'lower_zone'] and rsi < 40:
        if comb_weights.get('bollinger_low_rsi_low', 0) > 0:
            active['buy'].append('bollinger_low_rsi_low')
    
    # RSI Bas + Stoch Haussier
    if rsi < 45 and stoch_k > stoch_d:
        if comb_weights.get('rsi_low_stoch_bullish', 0) > 0:
            active['buy'].append('rsi_low_stoch_bullish')
    
    # Pattern Haussier + RSI Bas
    if pattern_dir == 'bullish' and rsi < 45:
        if comb_weights.get('pattern_bullish_rsi_low', 0) > 0:
            active['buy'].append('pattern_bullish_rsi_low')
    
    # Bollinger Basse + Stoch Haussier
    if bb_signal in ['lower_touch', 'lower_zone'] and stoch_k > stoch_d:
        if comb_weights.get('bollinger_low_stoch_bullish', 0) > 0:
            active['buy'].append('bollinger_low_stoch_bullish')
    
    # ADX Fort + DI+ Dominant
    if adx > adx_cfg.get('strong', 25) and di_plus > di_minus:
        if comb_weights.get('adx_strong_di_plus', 0) > 0:
            active['buy'].append('adx_strong_di_plus')
    
    # MACD Haussier + Tendance Haussière
    if macd > macd_signal_val and macd_hist > 0 and trend in ['bullish', 'strong_bullish']:
        if comb_weights.get('macd_bullish_trend_bullish', 0) > 0:
            active['buy'].append('macd_bullish_trend_bullish')
    
    # MACD Positif + Tendance Haussière
    if macd_hist > 0 and trend in ['bullish', 'strong_bullish']:
        if comb_weights.get('macd_positive_trend_bullish', 0) > 0:
            active['buy'].append('macd_positive_trend_bullish')
    
    # Pattern Haussier + Tendance Haussière
    if pattern_dir == 'bullish' and trend in ['bullish', 'strong_bullish']:
        if comb_weights.get('pattern_bullish_trend_bullish', 0) > 0:
            active['buy'].append('pattern_bullish_trend_bullish')
    
    # Stoch Croisement Haussier + RSI Bas
    if stoch_bullish_cross and rsi < 50:
        if comb_weights.get('stoch_cross_bullish_rsi_low', 0) > 0:
            active['buy'].append('stoch_cross_bullish_rsi_low')
    
    # RSI Sortie Survente + Stoch
    oversold = rsi_cfg.get('oversold', 30)
    if rsi_prev <= oversold and rsi > oversold and stoch_k > stoch_d:
        if comb_weights.get('rsi_exit_oversold_stoch', 0) > 0:
            active['buy'].append('rsi_exit_oversold_stoch')
    
    # === COMBINAISONS DE VENTE ===
    
    # Divergence Baissière + Stoch
    if rsi_div == 'bearish' and stoch_k < stoch_d:
        if comb_weights.get('divergence_bearish_stoch', 0) > 0:
            active['sell'].append('divergence_bearish_stoch')
    
    # Triple Confirm Vente
    if rsi > 50 and stoch_k < stoch_d and macd_hist < 0:
        if comb_weights.get('triple_confirm_sell', 0) > 0:
            active['sell'].append('triple_confirm_sell')
    
    # MACD Croisement Baissier + RSI Haut
    if macd_bearish_cross and rsi > 50:
        if comb_weights.get('macd_cross_bearish_rsi_high', 0) > 0:
            active['sell'].append('macd_cross_bearish_rsi_high')
    
    # Bollinger Haute + RSI Haut
    if bb_signal in ['upper_touch', 'upper_zone'] and rsi > 60:
        if comb_weights.get('bollinger_high_rsi_high', 0) > 0:
            active['sell'].append('bollinger_high_rsi_high')
    
    # RSI Haut + Stoch Baissier
    if rsi > 55 and stoch_k < stoch_d:
        if comb_weights.get('rsi_high_stoch_bearish', 0) > 0:
            active['sell'].append('rsi_high_stoch_bearish')
    
    # Pattern Baissier + RSI Haut
    if pattern_dir == 'bearish' and rsi > 55:
        if comb_weights.get('pattern_bearish_rsi_high', 0) > 0:
            active['sell'].append('pattern_bearish_rsi_high')
    
    # Bollinger Haute + Stoch Baissier
    if bb_signal in ['upper_touch', 'upper_zone'] and stoch_k < stoch_d:
        if comb_weights.get('bollinger_high_stoch_bearish', 0) > 0:
            active['sell'].append('bollinger_high_stoch_bearish')
    
    # ADX Fort + DI- Dominant
    if adx > adx_cfg.get('strong', 25) and di_minus > di_plus:
        if comb_weights.get('adx_strong_di_minus', 0) > 0:
            active['sell'].append('adx_strong_di_minus')
    
    # MACD Baissier + Tendance Baissière
    if macd < macd_signal_val and macd_hist < 0 and trend in ['bearish', 'strong_bearish']:
        if comb_weights.get('macd_bearish_trend_bearish', 0) > 0:
            active['sell'].append('macd_bearish_trend_bearish')
    
    # MACD Négatif + Tendance Baissière
    if macd_hist < 0 and trend in ['bearish', 'strong_bearish']:
        if comb_weights.get('macd_negative_trend_bearish', 0) > 0:
            active['sell'].append('macd_negative_trend_bearish')
    
    # Pattern Baissier + Tendance Baissière
    if pattern_dir == 'bearish' and trend in ['bearish', 'strong_bearish']:
        if comb_weights.get('pattern_bearish_trend_bearish', 0) > 0:
            active['sell'].append('pattern_bearish_trend_bearish')
    
    # Stoch Croisement Baissier + RSI Haut
    if stoch_bearish_cross and rsi > 50:
        if comb_weights.get('stoch_cross_bearish_rsi_high', 0) > 0:
            active['sell'].append('stoch_cross_bearish_rsi_high')
    
    # RSI Sortie Surachat + Stoch
    overbought = rsi_cfg.get('overbought', 70)
    if rsi_prev >= overbought and rsi < overbought and stoch_k < stoch_d:
        if comb_weights.get('rsi_exit_overbought_stoch', 0) > 0:
            active['sell'].append('rsi_exit_overbought_stoch')
    
    # Prix Sous MAs + MACD Négatif
    if sma_20 and sma_50 and close < sma_20 and sma_20 < sma_50 and macd < 0:
        if comb_weights.get('price_below_mas_macd_negative', 0) > 0:
            active['sell'].append('price_below_mas_macd_negative')
    
    return active

def calculate_individual_signals(row, config, active_flags):
    """
    Calcule les signaux des indicateurs individuels.
    VERSION CORRIGÉE: Utilise DIRECTEMENT les poids de la config, sans vérifier active_flags.
    """
    ind_weights = config.get('individual_weights', {})
    rsi_cfg = config.get('rsi', RSI)
    stoch_cfg = config.get('stochastic', STOCHASTIC)
    adx_cfg = config.get('adx', ADX)
    
    buy_score = 0
    sell_score = 0
    debug_contributions = []
    
    # Extraire les valeurs
    rsi = _safe_num(row, 'rsi', 50)
    stoch_k = _safe_num(row, 'stochastic_k', 50)
    stoch_d = _safe_num(row, 'stochastic_d', 50)
    macd = _safe_num(row, 'macd', 0)
    macd_signal_val = _safe_num(row, 'macd_signal', 0)
    macd_hist = _safe_num(row, 'macd_histogram', 0)
    trend = _safe_get(row, 'trend', 'neutral')
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    rsi_div = _safe_get(row, 'rsi_divergence', 'none')
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    adx = _safe_num(row, 'adx', 0)
    di_plus = _safe_num(row, 'di_plus', 0)
    di_minus = _safe_num(row, 'di_minus', 0)
    
    # === DIVERGENCE RSI - PRIORITÉ HAUTE ===
    # C'est le signal le plus fiable, on le traite EN PREMIER
    div_weight = ind_weights.get('rsi_divergence', 0)
    if div_weight > 0:
        if rsi_div == 'bullish':
            buy_score += div_weight
            debug_contributions.append(f"RSI DIV BULLISH: +{div_weight} buy")
        elif rsi_div == 'bearish':
            sell_score += div_weight
            debug_contributions.append(f"RSI DIV BEARISH: +{div_weight} sell")
    
    # === RSI ===
    rsi_extreme_weight = ind_weights.get('rsi_extreme', 0)
    rsi_exit_weight = ind_weights.get('rsi_exit_zone', 0)
    
    if rsi_extreme_weight > 0:
        if rsi <= rsi_cfg.get('oversold', 30):
            buy_score += rsi_extreme_weight
            debug_contributions.append(f"RSI extreme oversold: +{rsi_extreme_weight} buy")
        elif rsi >= rsi_cfg.get('overbought', 70):
            sell_score += rsi_extreme_weight
            debug_contributions.append(f"RSI extreme overbought: +{rsi_extreme_weight} sell")
    
    if rsi_exit_weight > 0:
        if rsi_cfg.get('exit_oversold_min', 30) <= rsi <= rsi_cfg.get('exit_oversold_max', 40):
            buy_score += rsi_exit_weight
            debug_contributions.append(f"RSI exit oversold: +{rsi_exit_weight} buy")
        elif rsi_cfg.get('exit_overbought_min', 60) <= rsi <= rsi_cfg.get('exit_overbought_max', 70):
            sell_score += rsi_exit_weight
            debug_contributions.append(f"RSI exit overbought: +{rsi_exit_weight} sell")
    
    # === STOCHASTIQUE ===
    stoch_weight = ind_weights.get('stoch_cross', 0)
    if stoch_weight > 0:
        if stoch_k < stoch_cfg.get('oversold', 20) + 10 and stoch_k > stoch_d:
            buy_score += stoch_weight
            debug_contributions.append(f"Stoch bullish: +{stoch_weight} buy")
        elif stoch_k > stoch_cfg.get('overbought', 80) - 10 and stoch_k < stoch_d:
            sell_score += stoch_weight
            debug_contributions.append(f"Stoch bearish: +{stoch_weight} sell")
    
    # === MACD ===
    macd_weight = ind_weights.get('macd_cross', 0)
    macd_hist_weight = ind_weights.get('macd_histogram', 0)
    
    if macd_weight > 0:
        if macd > macd_signal_val and macd_hist > 0:
            buy_score += macd_weight
            debug_contributions.append(f"MACD bullish: +{macd_weight} buy")
        elif macd < macd_signal_val and macd_hist < 0:
            sell_score += macd_weight
            debug_contributions.append(f"MACD bearish: +{macd_weight} sell")
    
    if macd_hist_weight > 0:
        if macd_hist > 0:
            buy_score += macd_hist_weight
            debug_contributions.append(f"MACD hist+: +{macd_hist_weight} buy")
        elif macd_hist < 0:
            sell_score += macd_hist_weight
            debug_contributions.append(f"MACD hist-: +{macd_hist_weight} sell")
    
    # === TENDANCE ===
    trend_strong_weight = ind_weights.get('trend_strong', 0)
    trend_weak_weight = ind_weights.get('trend_weak', 0)
    
    if trend == 'strong_bullish' and trend_strong_weight > 0:
        buy_score += trend_strong_weight
        debug_contributions.append(f"Trend strong bull: +{trend_strong_weight} buy")
    elif trend == 'bullish' and trend_weak_weight > 0:
        buy_score += trend_weak_weight
        debug_contributions.append(f"Trend bull: +{trend_weak_weight} buy")
    elif trend == 'strong_bearish' and trend_strong_weight > 0:
        sell_score += trend_strong_weight
        debug_contributions.append(f"Trend strong bear: +{trend_strong_weight} sell")
    elif trend == 'bearish' and trend_weak_weight > 0:
        sell_score += trend_weak_weight
        debug_contributions.append(f"Trend bear: +{trend_weak_weight} sell")
    
    # === PATTERNS ===
    pattern_weight = ind_weights.get('pattern_signal', 0)
    if pattern_weight > 0:
        if pattern_dir == 'bullish':
            buy_score += pattern_weight
            debug_contributions.append(f"Pattern bullish: +{pattern_weight} buy")
        elif pattern_dir == 'bearish':
            sell_score += pattern_weight
            debug_contributions.append(f"Pattern bearish: +{pattern_weight} sell")
    
    # === BOLLINGER ===
    bb_touch_weight = ind_weights.get('bollinger_touch', 0)
    bb_zone_weight = ind_weights.get('bollinger_zone', 0)
    
    if bb_touch_weight > 0:
        if bb_signal == 'lower_touch':
            buy_score += bb_touch_weight
            debug_contributions.append(f"BB lower touch: +{bb_touch_weight} buy")
        elif bb_signal == 'upper_touch':
            sell_score += bb_touch_weight
            debug_contributions.append(f"BB upper touch: +{bb_touch_weight} sell")
    
    if bb_zone_weight > 0:
        if bb_signal == 'lower_zone':
            buy_score += bb_zone_weight
            debug_contributions.append(f"BB lower zone: +{bb_zone_weight} buy")
        elif bb_signal == 'upper_zone':
            sell_score += bb_zone_weight
            debug_contributions.append(f"BB upper zone: +{bb_zone_weight} sell")
    
    # === ADX/DI ===
    adx_weight = ind_weights.get('adx_direction', 0)
    if adx_weight > 0 and adx > adx_cfg.get('weak', 20):
        if di_plus > di_minus:
            buy_score += adx_weight
            debug_contributions.append(f"ADX DI+: +{adx_weight} buy")
        else:
            sell_score += adx_weight
            debug_contributions.append(f"ADX DI-: +{adx_weight} sell")
    
    return buy_score, sell_score, debug_contributions

def calculate_combination_signals(active_combinations, config):
    """Calcule le score basé sur les combinaisons actives."""
    comb_weights = config.get('combination_weights', COMBINATION_WEIGHTS)
    decision_cfg = config.get('decision', DECISION)
    bonus = decision_cfg.get('combination_bonus', 1.3)
    
    buy_score = 0
    sell_score = 0
    
    for combo_name in active_combinations.get('buy', []):
        weight = comb_weights.get(combo_name, 0)
        buy_score += weight
    
    for combo_name in active_combinations.get('sell', []):
        weight = comb_weights.get(combo_name, 0)
        sell_score += weight
    
    num_buy = len(active_combinations.get('buy', []))
    num_sell = len(active_combinations.get('sell', []))
    
    if num_buy >= 2:
        buy_score *= (1 + (bonus - 1) * min(num_buy - 1, 2) / 2)
    if num_sell >= 2:
        sell_score *= (1 + (bonus - 1) * min(num_sell - 1, 2) / 2)
    
    return buy_score, sell_score, num_buy, num_sell

def calculate_recommendation_v4(row, df, config=None, signal_timeframe=1):
    """
    VERSION 4.5 : Strictement basé sur les poids configurés.
    CORRECTION: Afficher les seuils reçus pour debug.
    """
    if config is None:
        config = get_default_config()
    
    if pd.isna(row.get('stochastic_k')) or pd.isna(row.get('rsi')):
        return 'Neutre', 0, []
    
    decision_cfg = config.get('decision', DECISION)
    
    # DEBUG: Afficher les seuils utilisés (une seule fois par run)
    if DEBUG_RECOMMENDATIONS:
        # Récupérer la date pour identifier la ligne
        date_val = row.get('Date', row.get('date', 'N/A'))
        # Afficher seulement pour la dernière ligne (éviter le spam)
        # On peut vérifier si c'est la dernière ligne du DataFrame
        pass  # Le debug sera affiché plus bas
    
    # Récupérer les flags d'indicateurs actifs
    active_flags = _get_active_indicator_flags(config)
    
    # Récupérer la ligne précédente
    row_prev = None
    if row.name in df.index:
        try:
            current_idx = df.index.get_loc(row.name)
            if current_idx > 0:
                row_prev = df.iloc[current_idx - 1].to_dict()
        except:
            pass
    
    row_dict = row.to_dict()
    
    # === ANALYSE MULTI-TIMEFRAME ===
    if signal_timeframe > 1 and row.name in df.index:
        try:
            current_idx = df.index.get_loc(row.name)
            start_idx = max(0, current_idx - signal_timeframe + 1)
            window = df.iloc[start_idx:current_idx + 1]
            
            row_dict['rsi'] = window['rsi'].mean() if 'rsi' in window else row_dict.get('rsi')
            row_dict['stochastic_k'] = window['stochastic_k'].mean() if 'stochastic_k' in window else row_dict.get('stochastic_k')
            row_dict['stochastic_d'] = window['stochastic_d'].mean() if 'stochastic_d' in window else row_dict.get('stochastic_d')
        except Exception:
            pass
    
    # === 1. CALCULER LES SIGNAUX INDIVIDUELS ===
    ind_buy, ind_sell, debug_contribs = calculate_individual_signals(row_dict, config, active_flags)
    
    # === 2. DÉTECTER LES COMBINAISONS ACTIVES ===
    active_combinations = detect_active_combinations(row_dict, row_prev, config, active_flags)
    
    # === 3. CALCULER LES SIGNAUX DES COMBINAISONS ===
    comb_buy, comb_sell, num_buy_combos, num_sell_combos = calculate_combination_signals(active_combinations, config)
    
    # === 4. COMBINER LES SCORES ===
    has_any_combo = num_buy_combos > 0 or num_sell_combos > 0
    
    if has_any_combo:
        total_buy = ind_buy * 0.3 + comb_buy * 0.7
        total_sell = ind_sell * 0.3 + comb_sell * 0.7
    else:
        total_buy = ind_buy
        total_sell = ind_sell
    
    # === 5. AJUSTEMENTS ===
    if active_flags['trend']:
        trend = row_dict.get('trend', 'neutral')
        against_penalty = decision_cfg.get('against_trend_penalty', 0.5)
        if trend == 'strong_bullish' and total_sell > total_buy:
            total_sell *= (1 - against_penalty * 0.4)
        if trend == 'strong_bearish' and total_buy > total_sell:
            total_buy *= (1 - against_penalty * 0.4)
    
    if active_flags['adx']:
        adx = _safe_num(row_dict, 'adx', 20)
        trend = row_dict.get('trend', 'neutral')
        adx_level = decision_cfg.get('adx_confirmation_level', 30)
        adx_bonus = decision_cfg.get('adx_confirmation_bonus', 1.2)
        if adx > adx_level:
            if trend in ['bullish', 'strong_bullish'] and total_buy > total_sell:
                total_buy *= adx_bonus
            elif trend in ['bearish', 'strong_bearish'] and total_sell > total_buy:
                total_sell *= adx_bonus
    
    # === 6. DÉCISION FINALE ===
    seuil_minimum = decision_cfg.get('min_conviction_threshold', 2.5)
    diff_minimum = decision_cfg.get('conviction_difference', 0.5)
    max_conviction = decision_cfg.get('max_conviction', 5)
    min_combos = decision_cfg.get('min_combinations_for_signal', 1)
    
    total_buy = round(total_buy, 2)
    total_sell = round(total_sell, 2)
    
    all_active = active_combinations.get('buy', []) + active_combinations.get('sell', [])
    
    # === DEBUG ===
    if DEBUG_RECOMMENDATIONS and (total_buy > 0 or total_sell > 0):
        date_str = row_dict.get('Date', row_dict.get('date', 'N/A'))
        rsi_div = row_dict.get('rsi_divergence', 'none')
        print(f"\n=== DEBUG {date_str} ===")
        print(f"Active flags: {active_flags}")
        print(f"RSI Divergence: {rsi_div}")
        print(f"Individual contributions: {debug_contribs}")
        print(f"ind_buy={ind_buy}, ind_sell={ind_sell}")
        print(f"Active combos: {all_active}")
        print(f"comb_buy={comb_buy}, comb_sell={comb_sell}")
        print(f"total_buy={total_buy}, total_sell={total_sell}")
        # IMPORTANT: Afficher les seuils RÉELLEMENT utilisés
        print(f">>> SEUILS UTILISÉS: seuil={seuil_minimum}, diff={diff_minimum}, min_combos={min_combos}")
    
    # CORRECTION: Si aucune combinaison n'est configurée, ne pas exiger de combinaisons
    comb_weights = config.get('combination_weights', {})
    any_combo_configured = any(w > 0 for w in comb_weights.values())
    effective_min_combos = min_combos if any_combo_configured else 0
    
    # Vérifier les conditions pour ACHAT
    if total_buy >= seuil_minimum and total_buy > total_sell + diff_minimum:
        if num_buy_combos >= effective_min_combos:
            result = ('Acheter', min(int(round(total_buy)), max_conviction), all_active)
            if DEBUG_RECOMMENDATIONS:
                print(f">>> RESULT: {result}")
            return result
    
    # Vérifier les conditions pour VENTE
    if total_sell >= seuil_minimum and total_sell > total_buy + diff_minimum:
        if num_sell_combos >= effective_min_combos:
            result = ('Vendre', min(int(round(total_sell)), max_conviction), all_active)
            if DEBUG_RECOMMENDATIONS:
                print(f">>> RESULT: {result}")
            return result
    
    # NEUTRE
    max_conv = max(total_buy, total_sell)
    if DEBUG_RECOMMENDATIONS and (total_buy > 0 or total_sell > 0):
        print(f">>> RESULT: Neutre (buy={total_buy} < seuil={seuil_minimum} ou sell={total_sell} < seuil={seuil_minimum})")
    
    return 'Neutre', min(int(round(max_conv)), max_conviction), all_active

def get_weekly_trend(df_daily):
    """Convertit les données daily en weekly et calcule la tendance weekly."""
    df_weekly = df_daily.resample('W').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    if len(df_weekly) < 50:
        return 'neutral'
    
    df_weekly['sma_10'] = df_weekly['Close'].rolling(10).mean()
    df_weekly['sma_20'] = df_weekly['Close'].rolling(20).mean()
    df_weekly['sma_40'] = df_weekly['Close'].rolling(40).mean()
    
    last = df_weekly.iloc[-1]
    
    if last['Close'] > last['sma_10'] > last['sma_20'] > last['sma_40']:
        return 'strong_bullish'
    elif last['Close'] > last['sma_20']:
        return 'bullish'
    elif last['Close'] < last['sma_10'] < last['sma_20'] < last['sma_40']:
        return 'strong_bearish'
    elif last['Close'] < last['sma_20']:
        return 'bearish'
    else:
        return 'neutral'