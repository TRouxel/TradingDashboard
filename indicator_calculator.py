# indicator_calculator.py
import pandas as pd
import pandas_ta as ta
from config import (
    RSI, STOCHASTIC, MOVING_AVERAGES, MACD, ADX,
    SIGNAL_WEIGHTS, DECISION, TREND, DIVERGENCE, SIGNAL_TIMEFRAME,
    get_default_config
)

# Patterns qui sont TOUJOURS neutres, peu importe la valeur retournée
NEUTRAL_PATTERNS = {
    'DOJI', 'DOJISTAR', 'LONGLEGGEDOJI', 'LONGLEGGEDDOJI',
    'SPINNINGTOP', 'HIGHWAVE', 'RICKSHAWMAN',
    'INSIDE',
    'SHORTLINE', 'LONGLINE',
}


def get_pattern_with_direction(candle_patterns_row):
    """
    Analyse une ligne de patterns et retourne (pattern_name, direction).
    Direction: 'bullish', 'bearish', ou 'neutral'
    """
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
    """
    Calcule tous les indicateurs techniques et les ajoute au DataFrame.
    """
    if config is None:
        config = get_default_config()
    
    rsi_cfg = config.get('rsi', RSI)
    stoch_cfg = config.get('stochastic', STOCHASTIC)
    ma_cfg = config.get('moving_averages', MOVING_AVERAGES)
    macd_cfg = config.get('macd', MACD)
    adx_cfg = config.get('adx', ADX)
    
    # === INDICATEURS DE MOMENTUM ===
    df.ta.stoch(k=stoch_cfg['k_period'], d=stoch_cfg['d_period'], append=True)
    df.ta.rsi(length=rsi_cfg['period'], append=True)
    
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
    
    existing_cols = {k: v for k, v in rename_map.items() if k in df.columns}
    df.rename(columns=existing_cols, inplace=True)

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
    df['recommendation'], df['conviction'] = zip(*df.apply(
        lambda row: calculate_recommendation_v3(row, df, config, signal_timeframe), 
        axis=1
    ))

    return df


def calculate_trend(df, config=None):
    """
    Détermine la tendance basée sur les moyennes mobiles et l'ADX.
    """
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
    """
    Détecte les divergences entre le prix et le RSI.
    """
    if config is None:
        config = get_default_config()
    
    div_cfg = config.get('divergence', DIVERGENCE)
    rsi_low = div_cfg.get('rsi_low_threshold', 40)
    rsi_high = div_cfg.get('rsi_high_threshold', 60)
    
    divergences = ['none'] * len(df)
    
    for i in range(lookback * 2, len(df)):
        try:
            rsi = df['rsi'].iloc[i]
            rsi_prev = df['rsi'].iloc[i - lookback]
            price = df['Close'].iloc[i]
            price_prev = df['Close'].iloc[i - lookback]
            
            if pd.isna(rsi) or pd.isna(rsi_prev):
                continue
            
            if price < price_prev and rsi > rsi_prev and rsi < rsi_low:
                divergences[i] = 'bullish'
            
            elif price > price_prev and rsi < rsi_prev and rsi > rsi_high:
                divergences[i] = 'bearish'
                
        except (IndexError, KeyError):
            continue
    
    return divergences


def calculate_recommendation_v3(row, df, config=None, signal_timeframe=1):
    """
    VERSION 3 : Logique de recommandation ÉQUILIBRÉE entre achat et vente.
    
    Changements majeurs :
    - Suppression du filtre de tendance strict (permet signaux contre-tendance)
    - Ajout de signaux de vente basés sur le momentum déclinant
    - Détection des retournements de tendance
    - Signaux plus réactifs aux conditions de surachat
    """
    if config is None:
        config = get_default_config()
    
    if pd.isna(row.get('stochastic_k')) or pd.isna(row.get('rsi')):
        return 'Neutre', 0
    
    rsi_cfg = config.get('rsi', RSI)
    stoch_cfg = config.get('stochastic', STOCHASTIC)
    weights = config.get('signal_weights', SIGNAL_WEIGHTS)
    decision = config.get('decision', DECISION)
    adx_cfg = config.get('adx', ADX)
    
    stoch_k = row['stochastic_k']
    stoch_d = row['stochastic_d']
    rsi = row['rsi']
    trend = row.get('trend', 'neutral')
    macd = row.get('macd', 0)
    macd_signal = row.get('macd_signal', 0)
    macd_hist = row.get('macd_histogram', 0)
    pattern_dir = row.get('pattern_direction', 'neutral')
    rsi_div = row.get('rsi_divergence', 'none')
    adx = row.get('adx', 20)
    di_plus = row.get('di_plus', 25)
    di_minus = row.get('di_minus', 25)
    
    conviction_achat = 0
    conviction_vente = 0
    
    # === ANALYSE MULTI-TIMEFRAME ===
    if signal_timeframe > 1 and row.name in df.index:
        try:
            current_idx = df.index.get_loc(row.name)
            start_idx = max(0, current_idx - signal_timeframe + 1)
            window = df.iloc[start_idx:current_idx + 1]
            
            rsi = window['rsi'].mean() if 'rsi' in window else rsi
            stoch_k = window['stochastic_k'].mean() if 'stochastic_k' in window else stoch_k
            stoch_d = window['stochastic_d'].mean() if 'stochastic_d' in window else stoch_d
            
            patterns_in_window = window[window['pattern_direction'] != 'neutral']['pattern_direction']
            if len(patterns_in_window) > 0:
                pattern_dir = patterns_in_window.mode().iloc[0] if len(patterns_in_window.mode()) > 0 else 'neutral'
            
            divs_in_window = window[window['rsi_divergence'] != 'none']['rsi_divergence']
            if len(divs_in_window) > 0:
                rsi_div = divs_in_window.iloc[-1]
                
        except Exception:
            pass
    
    # ============================================
    # === SIGNAUX D'ACHAT ===
    # ============================================
    
    # 1. RSI en zone de survente ou sortie de survente
    if rsi <= rsi_cfg['oversold']:
        conviction_achat += weights.get('rsi_exit_oversold', 2) * 1.2  # Bonus survente extrême
    elif rsi_cfg['exit_oversold_min'] <= rsi <= rsi_cfg['exit_oversold_max']:
        if stoch_k > stoch_d:  # Confirmation stochastique
            conviction_achat += weights.get('rsi_exit_oversold', 2)
        else:
            conviction_achat += weights.get('rsi_exit_oversold', 2) * 0.5
    
    # 2. Stochastique : croisement haussier en zone basse
    if stoch_k < stoch_cfg['oversold'] + 10:  # Zone basse élargie
        if stoch_k > stoch_d:
            conviction_achat += weights.get('stoch_bullish_cross', 1)
    
    # 3. MACD : signaux haussiers
    if macd is not None and macd_signal is not None:
        if macd > macd_signal and macd_hist > 0:
            conviction_achat += weights.get('macd_bullish', 1)
        elif macd_hist is not None and macd_hist > 0:
            conviction_achat += weights.get('macd_histogram_positive', 0.5)
    
    # 4. Divergence RSI haussière
    if rsi_div == 'bullish':
        conviction_achat += weights.get('rsi_divergence', 2)
    
    # 5. Pattern de chandelier haussier
    if pattern_dir == 'bullish':
        conviction_achat += weights.get('pattern_bullish', 1.5)
    
    # 6. Bonus tendance haussière
    if trend in ['bullish', 'strong_bullish']:
        conviction_achat += weights.get('trend_bonus', 1)
    
    # 7. DI+ > DI- (momentum acheteur)
    if di_plus > di_minus and adx > adx_cfg['weak']:
        conviction_achat += 0.5
    
    # ============================================
    # === SIGNAUX DE VENTE ===
    # ============================================
    
    # 1. RSI en zone de surachat ou sortie de surachat
    if rsi >= rsi_cfg['overbought']:
        conviction_vente += weights.get('rsi_exit_overbought', 2) * 1.2  # Bonus surachat extrême
    elif rsi_cfg['exit_overbought_min'] <= rsi <= rsi_cfg['exit_overbought_max']:
        if stoch_k < stoch_d:  # Confirmation stochastique
            conviction_vente += weights.get('rsi_exit_overbought', 2)
        else:
            conviction_vente += weights.get('rsi_exit_overbought', 2) * 0.5
    
    # 2. RSI déclinant depuis zone haute (NOUVEAU)
    if rsi > 50 and rsi < rsi_cfg['exit_overbought_min']:
        # RSI qui descend après avoir été haut = momentum qui faiblit
        if stoch_k < stoch_d:
            conviction_vente += 0.8
    
    # 3. Stochastique : croisement baissier en zone haute
    if stoch_k > stoch_cfg['overbought'] - 10:  # Zone haute élargie
        if stoch_k < stoch_d:
            conviction_vente += weights.get('stoch_bearish_cross', 1)
    
    # 4. Stochastique en retournement (NOUVEAU)
    if stoch_k > 50 and stoch_k < stoch_d:
        conviction_vente += 0.5
    
    # 5. MACD : signaux baissiers
    if macd is not None and macd_signal is not None:
        if macd < macd_signal and macd_hist < 0:
            conviction_vente += weights.get('macd_bearish', 1)
        elif macd_hist is not None and macd_hist < 0:
            conviction_vente += weights.get('macd_histogram_negative', 0.5)
        
        # MACD qui passe sous zéro (NOUVEAU)
        if macd < 0 and macd_signal < 0:
            conviction_vente += 0.5
    
    # 6. Divergence RSI baissière
    if rsi_div == 'bearish':
        conviction_vente += weights.get('rsi_divergence', 2)
    
    # 7. Pattern de chandelier baissier
    if pattern_dir == 'bearish':
        conviction_vente += weights.get('pattern_bearish', 1.5)
    
    # 8. Bonus tendance baissière
    if trend in ['bearish', 'strong_bearish']:
        conviction_vente += weights.get('trend_bonus', 1)
    
    # 9. DI- > DI+ (momentum vendeur)
    if di_minus > di_plus and adx > adx_cfg['weak']:
        conviction_vente += 0.5
    
    # 10. Prix sous les moyennes mobiles clés (NOUVEAU)
    close = row.get('Close', 0)
    sma_20 = row.get('sma_20')
    sma_50 = row.get('sma_50')
    
    if sma_20 is not None and sma_50 is not None:
        if close < sma_20 < sma_50:  # Prix sous SMA20 qui est sous SMA50
            conviction_vente += 0.7
        elif close < sma_20:  # Prix sous SMA20
            conviction_vente += 0.3
    
    # ============================================
    # === AJUSTEMENTS ET PÉNALITÉS ===
    # ============================================
    
    # Pénalité légère pour signaux contre-tendance forte
    against_penalty = decision.get('against_trend_penalty', 0.5)
    if trend == 'strong_bullish' and conviction_vente > conviction_achat:
        conviction_vente *= (1 - against_penalty * 0.3)  # Pénalité réduite
    if trend == 'strong_bearish' and conviction_achat > conviction_vente:
        conviction_achat *= (1 - against_penalty * 0.3)
    
    # Bonus si ADX confirme une tendance forte
    adx_level = decision.get('adx_confirmation_level', 30)
    adx_bonus = decision.get('adx_confirmation_bonus', 1.2)
    if adx > adx_level:
        if trend in ['bullish', 'strong_bullish'] and conviction_achat > conviction_vente:
            conviction_achat *= adx_bonus
        elif trend in ['bearish', 'strong_bearish'] and conviction_vente > conviction_achat:
            conviction_vente *= adx_bonus
    
    # ============================================
    # === DÉCISION FINALE ===
    # ============================================
    
    seuil_minimum = decision.get('min_conviction_threshold', 2.5)
    diff_minimum = decision.get('conviction_difference', 0.5)
    max_conviction = decision.get('max_conviction', 5)
    
    conviction_achat = round(conviction_achat, 1)
    conviction_vente = round(conviction_vente, 1)
    
    # Décision avec seuil plus bas pour permettre plus de signaux
    seuil_effectif = seuil_minimum * 0.8  # Seuil réduit de 20%
    
    if conviction_achat >= seuil_effectif and conviction_achat > conviction_vente + diff_minimum:
        return 'Acheter', min(int(round(conviction_achat)), max_conviction)
    elif conviction_vente >= seuil_effectif and conviction_vente > conviction_achat + diff_minimum:
        return 'Vendre', min(int(round(conviction_vente)), max_conviction)
    else:
        max_conv = max(conviction_achat, conviction_vente)
        return 'Neutre', min(int(round(max_conv)), max_conviction)


def get_weekly_trend(df_daily):
    """
    Convertit les données daily en weekly et calcule la tendance weekly.
    """
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