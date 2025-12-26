# indicator_performance.py
"""
Module d'analyse de la performance des indicateurs.
Mesure la pertinence de chaque signal sur différents horizons temporels.
VERSION CORRIGÉE - Signaux améliorés + Combinaisons fonctionnelles
"""
import pandas as pd
import numpy as np
from config import get_default_config, RSI, STOCHASTIC, BOLLINGER, ADX


def calculate_performance_history(df, config=None, horizons=[1, 2, 5, 10, 20]):
    """
    Calcule l'historique de performance de chaque indicateur jour par jour.
    
    Pour chaque jour et chaque indicateur, on calcule:
    - Le signal émis (achat/vente/neutre)
    - L'intensité du signal (contribution)
    - Si le signal était correct pour chaque horizon
    - Un score = intensité * (1 si correct, -1 si incorrect)
    
    Returns:
        dict: {indicateur: DataFrame avec colonnes [Date, signal, intensity, score_1d, score_2d, ...]}
    """
    if config is None:
        config = get_default_config()
    
    if df.empty or len(df) < max(horizons) + 1:
        return {}
    
    # S'assurer que le DataFrame est trié par date
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Normaliser les noms de colonnes (gérer close/Close)
    df = _normalize_column_names(df)
    
    # Calculer les rendements futurs pour chaque horizon
    for h in horizons:
        df[f'future_return_{h}d'] = df['close'].shift(-h) / df['close'] - 1
    
    # Dictionnaire pour stocker les résultats
    performance_history = {}
    
    # === ANALYSER CHAQUE INDICATEUR ===
    indicators_config = [
        ('RSI', analyze_rsi_daily),
        ('Stochastique', analyze_stochastic_daily),
        ('Bollinger', analyze_bollinger_daily),
        ('MACD', analyze_macd_daily),
        ('Tendance', analyze_trend_daily),
        ('ADX', analyze_adx_daily),
        ('Patterns', analyze_pattern_daily),
        ('Divergence RSI', analyze_divergence_daily),
    ]
    
    for indicator_name, analyze_func in indicators_config:
        try:
            result_df = analyze_func(df, config, horizons)
            if result_df is not None and not result_df.empty:
                performance_history[indicator_name] = result_df
        except Exception as e:
            print(f"Erreur lors de l'analyse de {indicator_name}: {e}")
            continue
    
    # Ajouter la recommandation globale
    global_df = analyze_recommendation_daily(df, config, horizons)
    if global_df is not None and not global_df.empty:
        performance_history['Recommandation'] = global_df
    
    return performance_history


def _normalize_column_names(df):
    """Normalise les noms de colonnes pour gérer les variations de casse."""
    df = df.copy()
    
    # Mapping des colonnes avec variations possibles
    column_mapping = {
        'Close': 'close',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Volume': 'volume',
    }
    
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]
    
    return df


def _ensure_future_returns(df, horizons):
    """
    S'assure que les colonnes future_return_Xd existent dans le DataFrame.
    Si elles n'existent pas, les calcule.
    """
    df = df.copy()
    
    # S'assurer que 'close' existe
    if 'close' not in df.columns and 'Close' in df.columns:
        df['close'] = df['Close']
    
    # Calculer les rendements futurs manquants
    for h in horizons:
        col_name = f'future_return_{h}d'
        if col_name not in df.columns:
            df[col_name] = df['close'].shift(-h) / df['close'] - 1
    
    return df


def _calculate_scores(df, signal_col, intensity_col, horizons):
    """
    Calcule les scores pour chaque horizon.
    Score = intensité * direction_correcte
    où direction_correcte = 1 si le prix va dans le sens prédit, -1 sinon
    """
    result = df[['Date', signal_col, intensity_col]].copy()
    result.columns = ['Date', 'signal', 'intensity']
    
    for h in horizons:
        future_ret_col = f'future_return_{h}d'
        score_col = f'score_{h}d'
        correct_col = f'correct_{h}d'
        
        if future_ret_col not in df.columns:
            result[score_col] = np.nan
            result[correct_col] = np.nan
            continue
        
        scores = []
        corrects = []
        
        for idx in range(len(df)):
            signal = df.iloc[idx][signal_col]
            intensity = df.iloc[idx][intensity_col]
            future_ret = df.iloc[idx][future_ret_col]
            
            if pd.isna(future_ret) or signal == 'neutral' or intensity == 0:
                scores.append(0)
                corrects.append(np.nan)
                continue
            
            # Déterminer si la prédiction était correcte
            if signal == 'buy':
                is_correct = future_ret > 0
            elif signal == 'sell':
                is_correct = future_ret < 0
            else:
                scores.append(0)
                corrects.append(np.nan)
                continue
            
            # Score = intensité * direction
            direction = 1 if is_correct else -1
            scores.append(intensity * direction)
            corrects.append(1 if is_correct else 0)
        
        result[score_col] = scores
        result[correct_col] = corrects
    
    return result


def _safe_get(row, key, default=None):
    """Récupère une valeur de manière sécurisée (gère NaN et clés manquantes)."""
    # Essayer plusieurs variantes du nom de colonne
    keys_to_try = [key]
    
    # Ajouter des variantes de casse
    if key == 'close':
        keys_to_try.append('Close')
    elif key == 'Close':
        keys_to_try.append('close')
    elif key == 'open':
        keys_to_try.append('Open')
    elif key == 'Open':
        keys_to_try.append('open')
    
    for k in keys_to_try:
        val = row.get(k, None)
        if val is not None:
            if isinstance(val, float) and pd.isna(val):
                return default
            return val
    
    return default


def _safe_get_numeric(row, key, default=0):
    """Récupère une valeur numérique de manière sécurisée."""
    val = _safe_get(row, key, default)
    if val is None:
        return default
    try:
        result = float(val)
        if pd.isna(result):
            return default
        return result
    except (ValueError, TypeError):
        return default


def analyze_rsi_daily(df, config, horizons):
    """Analyse quotidienne du RSI."""
    rsi_cfg = config.get('rsi', RSI)
    weights = config.get('signal_weights', {})
    base_weight = weights.get('rsi_exit_oversold', 2.0)
    
    signals = []
    intensities = []
    
    oversold = rsi_cfg.get('oversold', 30)
    overbought = rsi_cfg.get('overbought', 70)
    
    for idx in range(len(df)):
        rsi = df.iloc[idx].get('rsi')
        
        if idx == 0 or pd.isna(rsi):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        rsi_prev = df.iloc[idx - 1].get('rsi')
        if pd.isna(rsi_prev):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        stoch_k = df.iloc[idx].get('stochastic_k', 50)
        stoch_d = df.iloc[idx].get('stochastic_d', 50)
        
        if pd.isna(stoch_k):
            stoch_k = 50
        if pd.isna(stoch_d):
            stoch_d = 50
        
        # Signal d'achat : RSI sort de survente
        if rsi_prev <= oversold and rsi > oversold:
            if stoch_k > stoch_d:
                signals.append('buy')
                intensities.append(base_weight * 1.2)
            else:
                signals.append('buy')
                intensities.append(base_weight * 0.7)
        
        elif rsi_prev < 35 and rsi > rsi_prev + 3 and rsi < 50:
            if stoch_k > stoch_d:
                signals.append('buy')
                intensities.append(base_weight * 0.8)
            else:
                signals.append('neutral')
                intensities.append(0)
        
        # Signal de vente : RSI sort de surachat
        elif rsi_prev >= overbought and rsi < overbought:
            if stoch_k < stoch_d:
                signals.append('sell')
                intensities.append(base_weight * 1.2)
            else:
                signals.append('sell')
                intensities.append(base_weight * 0.7)
        
        elif rsi_prev > 65 and rsi < rsi_prev - 3 and rsi > 50:
            if stoch_k < stoch_d:
                signals.append('sell')
                intensities.append(base_weight * 0.8)
            else:
                signals.append('neutral')
                intensities.append(0)
        
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_stochastic_daily(df, config, horizons):
    """Analyse quotidienne du Stochastique."""
    stoch_cfg = config.get('stochastic', STOCHASTIC)
    weights = config.get('signal_weights', {})
    base_weight = weights.get('stoch_bullish_cross', 1.0)
    
    oversold = stoch_cfg.get('oversold', 20)
    overbought = stoch_cfg.get('overbought', 80)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        stoch_k = df.iloc[idx].get('stochastic_k')
        stoch_d = df.iloc[idx].get('stochastic_d')
        
        if pd.isna(stoch_k) or pd.isna(stoch_d) or idx == 0:
            signals.append('neutral')
            intensities.append(0)
            continue
        
        stoch_k_prev = df.iloc[idx - 1].get('stochastic_k')
        stoch_d_prev = df.iloc[idx - 1].get('stochastic_d')
        
        if pd.isna(stoch_k_prev) or pd.isna(stoch_d_prev):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        bullish_cross = stoch_k_prev <= stoch_d_prev and stoch_k > stoch_d
        bearish_cross = stoch_k_prev >= stoch_d_prev and stoch_k < stoch_d
        
        if bullish_cross and stoch_k < oversold + 15:
            signals.append('buy')
            intensity = base_weight * (1 + (oversold + 15 - stoch_k) / 30)
            intensities.append(min(intensity, base_weight * 1.5))
        
        elif bearish_cross and stoch_k > overbought - 15:
            signals.append('sell')
            intensity = base_weight * (1 + (stoch_k - (overbought - 15)) / 30)
            intensities.append(min(intensity, base_weight * 1.5))
        
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_bollinger_daily(df, config, horizons):
    """Analyse quotidienne des Bandes de Bollinger."""
    weights = config.get('signal_weights', {})
    base_weight = weights.get('bollinger_lower', 1.5)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        bb_signal = df.iloc[idx].get('bb_signal', 'neutral')
        
        if pd.isna(bb_signal) or bb_signal is None:
            bb_signal = 'neutral'
        
        if idx > 0:
            close = _safe_get_numeric(df.iloc[idx].to_dict(), 'close', 0)
            close_prev = _safe_get_numeric(df.iloc[idx - 1].to_dict(), 'close', 0)
            price_rising = close > close_prev if close_prev > 0 else False
            price_falling = close < close_prev if close_prev > 0 else False
        else:
            price_rising = False
            price_falling = False
        
        if bb_signal == 'lower_touch' and price_rising:
            signals.append('buy')
            intensities.append(base_weight)
        elif bb_signal == 'lower_zone' and price_rising:
            signals.append('buy')
            intensities.append(base_weight * 0.5)
        elif bb_signal == 'upper_touch' and price_falling:
            signals.append('sell')
            intensities.append(base_weight)
        elif bb_signal == 'upper_zone' and price_falling:
            signals.append('sell')
            intensities.append(base_weight * 0.5)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_macd_daily(df, config, horizons):
    """Analyse quotidienne du MACD."""
    weights = config.get('signal_weights', {})
    base_weight = weights.get('macd_bullish', 1.0)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        macd = df.iloc[idx].get('macd')
        macd_signal = df.iloc[idx].get('macd_signal')
        macd_hist = df.iloc[idx].get('macd_histogram')
        
        if pd.isna(macd) or pd.isna(macd_signal) or idx < 2:
            signals.append('neutral')
            intensities.append(0)
            continue
        
        macd_prev = df.iloc[idx - 1].get('macd')
        macd_signal_prev = df.iloc[idx - 1].get('macd_signal')
        macd_hist_prev = df.iloc[idx - 1].get('macd_histogram')
        
        if pd.isna(macd_prev) or pd.isna(macd_signal_prev):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        bullish_cross = macd_prev <= macd_signal_prev and macd > macd_signal
        bearish_cross = macd_prev >= macd_signal_prev and macd < macd_signal
        
        hist_increasing = macd_hist_prev is not None and not pd.isna(macd_hist_prev) and not pd.isna(macd_hist) and macd_hist > macd_hist_prev
        hist_decreasing = macd_hist_prev is not None and not pd.isna(macd_hist_prev) and not pd.isna(macd_hist) and macd_hist < macd_hist_prev
        
        if bullish_cross:
            intensity = base_weight
            if macd > 0:
                intensity *= 1.3
            if hist_increasing:
                intensity *= 1.2
            signals.append('buy')
            intensities.append(min(intensity, base_weight * 2))
        
        elif bearish_cross:
            intensity = base_weight
            if macd < 0:
                intensity *= 1.3
            if hist_decreasing:
                intensity *= 1.2
            signals.append('sell')
            intensities.append(min(intensity, base_weight * 2))
        
        elif macd_hist_prev is not None and not pd.isna(macd_hist_prev) and not pd.isna(macd_hist):
            if macd_hist_prev <= 0 and macd_hist > 0 and hist_increasing:
                signals.append('buy')
                intensities.append(base_weight * 0.5)
            elif macd_hist_prev >= 0 and macd_hist < 0 and hist_decreasing:
                signals.append('sell')
                intensities.append(base_weight * 0.5)
            else:
                signals.append('neutral')
                intensities.append(0)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_trend_daily(df, config, horizons):
    """Analyse quotidienne de la Tendance."""
    weights = config.get('signal_weights', {})
    base_weight = weights.get('trend_bonus', 1.0)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        trend = df.iloc[idx].get('trend', 'neutral')
        
        if pd.isna(trend) or trend is None:
            trend = 'neutral'
        
        if trend in ['strong_bullish', 'bullish']:
            signals.append('buy')
            intensities.append(base_weight if trend == 'strong_bullish' else base_weight * 0.7)
        elif trend in ['strong_bearish', 'bearish']:
            signals.append('sell')
            intensities.append(base_weight if trend == 'strong_bearish' else base_weight * 0.7)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_adx_daily(df, config, horizons):
    """Analyse quotidienne de l'ADX/DI."""
    adx_cfg = config.get('adx', ADX)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        adx = df.iloc[idx].get('adx')
        di_plus = df.iloc[idx].get('di_plus')
        di_minus = df.iloc[idx].get('di_minus')
        
        if pd.isna(adx) or pd.isna(di_plus) or pd.isna(di_minus):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        if adx > adx_cfg.get('weak', 20):
            intensity = 0.5 + (adx - 20) / 40
            intensity = min(intensity, 1.5)
            
            if di_plus > di_minus:
                signals.append('buy')
            else:
                signals.append('sell')
            intensities.append(intensity)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_pattern_daily(df, config, horizons):
    """Analyse quotidienne des Patterns."""
    weights = config.get('signal_weights', {})
    base_weight = weights.get('pattern_bullish', 1.5)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        pattern_dir = df.iloc[idx].get('pattern_direction', 'neutral')
        
        if pd.isna(pattern_dir) or pattern_dir is None:
            pattern_dir = 'neutral'
        
        if pattern_dir == 'bullish':
            signals.append('buy')
            intensities.append(base_weight)
        elif pattern_dir == 'bearish':
            signals.append('sell')
            intensities.append(base_weight)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_divergence_daily(df, config, horizons):
    """Analyse quotidienne des Divergences RSI."""
    weights = config.get('signal_weights', {})
    base_weight = weights.get('rsi_divergence', 2.0)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        rsi_div = df.iloc[idx].get('rsi_divergence', 'none')
        
        if pd.isna(rsi_div) or rsi_div is None:
            rsi_div = 'none'
        
        if rsi_div == 'bullish':
            signals.append('buy')
            intensities.append(base_weight)
        elif rsi_div == 'bearish':
            signals.append('sell')
            intensities.append(base_weight)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def analyze_recommendation_daily(df, config, horizons):
    """Analyse quotidienne de la Recommandation globale."""
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        reco = df.iloc[idx].get('recommendation', 'Neutre')
        conviction = df.iloc[idx].get('conviction', 0)
        
        if pd.isna(reco) or reco is None:
            reco = 'Neutre'
        if pd.isna(conviction) or conviction is None:
            conviction = 0
        
        if reco == 'Acheter':
            signals.append('buy')
            intensities.append(conviction)
        elif reco == 'Vendre':
            signals.append('sell')
            intensities.append(conviction)
        else:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def calculate_accuracy_stats(perf_df, horizons=[1, 2, 5, 10, 20]):
    """
    Calcule les statistiques de précision pour un indicateur.
    """
    stats = {}
    
    for h in horizons:
        correct_col = f'correct_{h}d'
        if correct_col not in perf_df.columns:
            continue
        
        valid = perf_df[perf_df[correct_col].notna()]
        
        if len(valid) == 0:
            stats[h] = {'accuracy': None, 'total_signals': 0, 'correct': 0, 'wrong': 0}
            continue
        
        correct = (valid[correct_col] == 1).sum()
        wrong = (valid[correct_col] == 0).sum()
        total = correct + wrong
        
        stats[h] = {
            'accuracy': (correct / total * 100) if total > 0 else None,
            'total_signals': total,
            'correct': correct,
            'wrong': wrong
        }
    
    return stats


# === ANALYSE DES COMBINAISONS DE SIGNAUX ===

def _check_rsi_oversold_stoch_bullish(row, row_prev, cfg):
    """RSI Survente + Stoch Haussier - VERSION ASSOUPLIE"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    # Assouplir: RSI < 45 ET stoch haussier
    return rsi < 45 and stoch_k > stoch_d


def _check_rsi_exit_oversold_stoch(row, row_prev, cfg):
    """RSI Sortie Survente + Stoch Confirme"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    rsi_prev = _safe_get_numeric(row_prev, 'rsi', 50) if row_prev else 50
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    oversold = cfg.get('rsi', {}).get('oversold', 30)
    # RSI était en survente et remonte, avec stoch haussier
    return rsi_prev <= oversold and rsi > oversold and stoch_k > stoch_d


def _check_macd_bullish_trend_bullish(row, row_prev, cfg):
    """MACD Haussier + Tendance Haussière"""
    macd = _safe_get_numeric(row, 'macd', 0)
    macd_signal = _safe_get_numeric(row, 'macd_signal', 0)
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    trend = _safe_get(row, 'trend', 'neutral')
    return macd > macd_signal and macd_hist > 0 and trend in ['bullish', 'strong_bullish']


def _check_macd_cross_rsi_low(row, row_prev, cfg):
    """MACD Croisement Haussier + RSI Bas"""
    macd = _safe_get_numeric(row, 'macd', 0)
    macd_signal = _safe_get_numeric(row, 'macd_signal', 0)
    macd_prev = _safe_get_numeric(row_prev, 'macd', 0) if row_prev else 0
    macd_signal_prev = _safe_get_numeric(row_prev, 'macd_signal', 0) if row_prev else 0
    rsi = _safe_get_numeric(row, 'rsi', 50)
    # Croisement haussier du MACD + RSI < 50
    bullish_cross = macd_prev <= macd_signal_prev and macd > macd_signal
    return bullish_cross and rsi < 50


def _check_bollinger_low_stoch_bullish(row, row_prev, cfg):
    """Bollinger Basse + Stoch Haussier"""
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    return bb_signal in ['lower_touch', 'lower_zone'] and stoch_k > stoch_d


def _check_bollinger_low_rsi_oversold(row, row_prev, cfg):
    """Bollinger Basse + RSI Survente"""
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    rsi = _safe_get_numeric(row, 'rsi', 50)
    return bb_signal in ['lower_touch', 'lower_zone'] and rsi < 40


def _check_pattern_bullish_trend_bullish(row, row_prev, cfg):
    """Pattern Haussier + Tendance Haussière"""
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    trend = _safe_get(row, 'trend', 'neutral')
    return pattern_dir == 'bullish' and trend in ['bullish', 'strong_bullish']


def _check_pattern_bullish_rsi_oversold(row, row_prev, cfg):
    """Pattern Haussier + RSI Survente"""
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    rsi = _safe_get_numeric(row, 'rsi', 50)
    return pattern_dir == 'bullish' and rsi < 45


def _check_divergence_bullish_stoch(row, row_prev, cfg):
    """Divergence RSI Haussière + Stoch"""
    rsi_div = _safe_get(row, 'rsi_divergence', 'none')
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    return rsi_div == 'bullish' and stoch_k > stoch_d


def _check_triple_buy(row, row_prev, cfg):
    """Triple Confirm Achat (RSI bas + Stoch haussier + MACD positif)"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    return rsi < 50 and stoch_k > stoch_d and macd_hist > 0


def _check_adx_strong_di_plus(row, row_prev, cfg):
    """ADX Fort + DI Plus Dominant"""
    adx = _safe_get_numeric(row, 'adx', 0)
    di_plus = _safe_get_numeric(row, 'di_plus', 0)
    di_minus = _safe_get_numeric(row, 'di_minus', 0)
    adx_strong = cfg.get('adx', {}).get('strong', 25)
    return adx > adx_strong and di_plus > di_minus


def _check_stoch_bullish_cross_rsi_low(row, row_prev, cfg):
    """Stoch Croisement Haussier + RSI Bas"""
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    stoch_k_prev = _safe_get_numeric(row_prev, 'stochastic_k', 50) if row_prev else 50
    stoch_d_prev = _safe_get_numeric(row_prev, 'stochastic_d', 50) if row_prev else 50
    rsi = _safe_get_numeric(row, 'rsi', 50)
    bullish_cross = stoch_k_prev <= stoch_d_prev and stoch_k > stoch_d
    return bullish_cross and rsi < 50


def _check_macd_positive_trend_bullish(row, row_prev, cfg):
    """MACD Histogramme Positif + Tendance Haussière"""
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    trend = _safe_get(row, 'trend', 'neutral')
    return macd_hist > 0 and trend in ['bullish', 'strong_bullish']


def _check_rsi_overbought_stoch_bearish(row, row_prev, cfg):
    """RSI Surachat + Stoch Baissier - VERSION ASSOUPLIE"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    # Assouplir: RSI > 55 ET stoch baissier
    return rsi > 55 and stoch_k < stoch_d


def _check_rsi_exit_overbought_stoch(row, row_prev, cfg):
    """RSI Sortie Surachat + Stoch Confirme"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    rsi_prev = _safe_get_numeric(row_prev, 'rsi', 50) if row_prev else 50
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    overbought = cfg.get('rsi', {}).get('overbought', 70)
    # RSI était en surachat et descend, avec stoch baissier
    return rsi_prev >= overbought and rsi < overbought and stoch_k < stoch_d


def _check_macd_bearish_trend_bearish(row, row_prev, cfg):
    """MACD Baissier + Tendance Baissière"""
    macd = _safe_get_numeric(row, 'macd', 0)
    macd_signal = _safe_get_numeric(row, 'macd_signal', 0)
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    trend = _safe_get(row, 'trend', 'neutral')
    return macd < macd_signal and macd_hist < 0 and trend in ['bearish', 'strong_bearish']


def _check_macd_cross_bearish_rsi_high(row, row_prev, cfg):
    """MACD Croisement Baissier + RSI Haut"""
    macd = _safe_get_numeric(row, 'macd', 0)
    macd_signal = _safe_get_numeric(row, 'macd_signal', 0)
    macd_prev = _safe_get_numeric(row_prev, 'macd', 0) if row_prev else 0
    macd_signal_prev = _safe_get_numeric(row_prev, 'macd_signal', 0) if row_prev else 0
    rsi = _safe_get_numeric(row, 'rsi', 50)
    # Croisement baissier du MACD + RSI > 50
    bearish_cross = macd_prev >= macd_signal_prev and macd < macd_signal
    return bearish_cross and rsi > 50


def _check_bollinger_high_stoch_bearish(row, row_prev, cfg):
    """Bollinger Haute + Stoch Baissier"""
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    return bb_signal in ['upper_touch', 'upper_zone'] and stoch_k < stoch_d


def _check_bollinger_high_rsi_overbought(row, row_prev, cfg):
    """Bollinger Haute + RSI Surachat"""
    bb_signal = _safe_get(row, 'bb_signal', 'neutral')
    rsi = _safe_get_numeric(row, 'rsi', 50)
    return bb_signal in ['upper_touch', 'upper_zone'] and rsi > 60


def _check_pattern_bearish_trend_bearish(row, row_prev, cfg):
    """Pattern Baissier + Tendance Baissière"""
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    trend = _safe_get(row, 'trend', 'neutral')
    return pattern_dir == 'bearish' and trend in ['bearish', 'strong_bearish']


def _check_pattern_bearish_rsi_overbought(row, row_prev, cfg):
    """Pattern Baissier + RSI Surachat"""
    pattern_dir = _safe_get(row, 'pattern_direction', 'neutral')
    rsi = _safe_get_numeric(row, 'rsi', 50)
    return pattern_dir == 'bearish' and rsi > 55


def _check_divergence_bearish_stoch(row, row_prev, cfg):
    """Divergence RSI Baissière + Stoch"""
    rsi_div = _safe_get(row, 'rsi_divergence', 'none')
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    return rsi_div == 'bearish' and stoch_k < stoch_d


def _check_triple_sell(row, row_prev, cfg):
    """Triple Confirm Vente (RSI haut + Stoch baissier + MACD négatif)"""
    rsi = _safe_get_numeric(row, 'rsi', 50)
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    return rsi > 50 and stoch_k < stoch_d and macd_hist < 0


def _check_adx_strong_di_minus(row, row_prev, cfg):
    """ADX Fort + DI Moins Dominant"""
    adx = _safe_get_numeric(row, 'adx', 0)
    di_plus = _safe_get_numeric(row, 'di_plus', 0)
    di_minus = _safe_get_numeric(row, 'di_minus', 0)
    adx_strong = cfg.get('adx', {}).get('strong', 25)
    return adx > adx_strong and di_minus > di_plus


def _check_price_below_mas_macd_negative(row, row_prev, cfg):
    """Prix Sous MAs + MACD Négatif"""
    close = _safe_get_numeric(row, 'close', 0)
    sma_20 = _safe_get_numeric(row, 'sma_20', None)
    sma_50 = _safe_get_numeric(row, 'sma_50', None)
    macd = _safe_get_numeric(row, 'macd', 0)
    
    if sma_20 is None or sma_50 is None or sma_20 == 0 or sma_50 == 0:
        return False
    
    return close < sma_20 and sma_20 < sma_50 and macd < 0


def _check_stoch_bearish_cross_rsi_high(row, row_prev, cfg):
    """Stoch Croisement Baissier + RSI Haut"""
    stoch_k = _safe_get_numeric(row, 'stochastic_k', 50)
    stoch_d = _safe_get_numeric(row, 'stochastic_d', 50)
    stoch_k_prev = _safe_get_numeric(row_prev, 'stochastic_k', 50) if row_prev else 50
    stoch_d_prev = _safe_get_numeric(row_prev, 'stochastic_d', 50) if row_prev else 50
    rsi = _safe_get_numeric(row, 'rsi', 50)
    bearish_cross = stoch_k_prev >= stoch_d_prev and stoch_k < stoch_d
    return bearish_cross and rsi > 50


def _check_macd_negative_trend_bearish(row, row_prev, cfg):
    """MACD Histogramme Négatif + Tendance Baissière"""
    macd_hist = _safe_get_numeric(row, 'macd_histogram', 0)
    trend = _safe_get(row, 'trend', 'neutral')
    return macd_hist < 0 and trend in ['bearish', 'strong_bearish']


# Définition des combinaisons avec leur type explicite
COMBINATION_DEFINITIONS = [
    # === COMBINAISONS D'ACHAT ===
    {'name': 'RSI Bas + Stoch Haussier', 'type': 'buy', 'check': _check_rsi_oversold_stoch_bullish},
    {'name': 'RSI Sortie Survente + Stoch', 'type': 'buy', 'check': _check_rsi_exit_oversold_stoch},
    {'name': 'MACD Haussier + Tendance Haussière', 'type': 'buy', 'check': _check_macd_bullish_trend_bullish},
    {'name': 'MACD Croisement Haussier + RSI Bas', 'type': 'buy', 'check': _check_macd_cross_rsi_low},
    {'name': 'Bollinger Basse + Stoch Haussier', 'type': 'buy', 'check': _check_bollinger_low_stoch_bullish},
    {'name': 'Bollinger Basse + RSI Bas', 'type': 'buy', 'check': _check_bollinger_low_rsi_oversold},
    {'name': 'Pattern Haussier + Tendance Haussière', 'type': 'buy', 'check': _check_pattern_bullish_trend_bullish},
    {'name': 'Pattern Haussier + RSI Bas', 'type': 'buy', 'check': _check_pattern_bullish_rsi_oversold},
    {'name': 'Divergence Haussière + Stoch', 'type': 'buy', 'check': _check_divergence_bullish_stoch},
    {'name': 'Triple Confirm Achat', 'type': 'buy', 'check': _check_triple_buy},
    {'name': 'ADX Fort + DI+ Dominant', 'type': 'buy', 'check': _check_adx_strong_di_plus},
    {'name': 'Stoch Croisement Haussier + RSI Bas', 'type': 'buy', 'check': _check_stoch_bullish_cross_rsi_low},
    {'name': 'MACD Positif + Tendance Haussière', 'type': 'buy', 'check': _check_macd_positive_trend_bullish},
    
    # === COMBINAISONS DE VENTE ===
    {'name': 'RSI Haut + Stoch Baissier', 'type': 'sell', 'check': _check_rsi_overbought_stoch_bearish},
    {'name': 'RSI Sortie Surachat + Stoch', 'type': 'sell', 'check': _check_rsi_exit_overbought_stoch},
    {'name': 'MACD Baissier + Tendance Baissière', 'type': 'sell', 'check': _check_macd_bearish_trend_bearish},
    {'name': 'MACD Croisement Baissier + RSI Haut', 'type': 'sell', 'check': _check_macd_cross_bearish_rsi_high},
    {'name': 'Bollinger Haute + Stoch Baissier', 'type': 'sell', 'check': _check_bollinger_high_stoch_bearish},
    {'name': 'Bollinger Haute + RSI Haut', 'type': 'sell', 'check': _check_bollinger_high_rsi_overbought},
    {'name': 'Pattern Baissier + Tendance Baissière', 'type': 'sell', 'check': _check_pattern_bearish_trend_bearish},
    {'name': 'Pattern Baissier + RSI Haut', 'type': 'sell', 'check': _check_pattern_bearish_rsi_overbought},
    {'name': 'Divergence Baissière + Stoch', 'type': 'sell', 'check': _check_divergence_bearish_stoch},
    {'name': 'Triple Confirm Vente', 'type': 'sell', 'check': _check_triple_sell},
    {'name': 'ADX Fort + DI- Dominant', 'type': 'sell', 'check': _check_adx_strong_di_minus},
    {'name': 'Prix Sous MAs + MACD Négatif', 'type': 'sell', 'check': _check_price_below_mas_macd_negative},
    {'name': 'Stoch Croisement Baissier + RSI Haut', 'type': 'sell', 'check': _check_stoch_bearish_cross_rsi_high},
    {'name': 'MACD Négatif + Tendance Baissière', 'type': 'sell', 'check': _check_macd_negative_trend_bearish},
]


def analyze_signal_combinations(df, config, horizons):
    """
    Analyse les combinaisons de signaux.
    Retourne un dictionnaire avec les performances de chaque combinaison.
    
    CORRECTION: Calcule les future_returns avant d'analyser les combinaisons.
    """
    if config is None:
        config = get_default_config()
    
    # S'assurer que la config a les clés nécessaires
    if 'rsi' not in config:
        config['rsi'] = RSI
    if 'stochastic' not in config:
        config['stochastic'] = STOCHASTIC
    if 'adx' not in config:
        config['adx'] = ADX
    
    # CORRECTION: S'assurer que les future_returns existent
    df = _ensure_future_returns(df, horizons)
    
    results = {}
    
    for combo_def in COMBINATION_DEFINITIONS:
        combo_name = combo_def['name']
        combo_type = combo_def['type']
        check_func = combo_def['check']
        
        result_df = _analyze_single_combination_v2(df, combo_name, combo_type, check_func, config, horizons)
        
        if result_df is not None and not result_df.empty:
            # Compter les signaux non-neutres
            signal_count = len(result_df[result_df['signal'] != 'neutral'])
            if signal_count > 0:
                results[combo_name] = {
                    'df': result_df,
                    'type': combo_type,
                    'signal_count': signal_count
                }
    
    return results


def _analyze_single_combination_v2(df, combo_name, combo_type, check_func, config, horizons):
    """
    Analyse une combinaison spécifique.
    """
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        row_dict = row.to_dict()
        
        # Récupérer la ligne précédente pour les croisements
        if idx > 0:
            row_prev_dict = df.iloc[idx - 1].to_dict()
        else:
            row_prev_dict = None
        
        try:
            if check_func(row_dict, row_prev_dict, config):
                signals.append(combo_type)
                intensities.append(1.5)
            else:
                signals.append('neutral')
                intensities.append(0)
        except Exception as e:
            signals.append('neutral')
            intensities.append(0)
    
    df_temp = df.copy()
    df_temp['_signal'] = signals
    df_temp['_intensity'] = intensities
    
    return _calculate_scores(df_temp, '_signal', '_intensity', horizons)


def calculate_performance_history_with_combinations(df, config=None, horizons=[1, 2, 5, 10, 20]):
    """
    Version étendue qui inclut les indicateurs individuels ET les combinaisons.
    """
    if config is None:
        config = get_default_config()
    
    # Normaliser les colonnes
    df = _normalize_column_names(df)
    
    # S'assurer que les future_returns existent pour tout le monde
    df = _ensure_future_returns(df, horizons)
    
    # D'abord, calculer les performances des indicateurs individuels
    individual_perf = calculate_performance_history(df, config, horizons)
    
    # Ensuite, calculer les performances des combinaisons
    combination_results = analyze_signal_combinations(df, config, horizons)
    
    # Fusionner les résultats
    all_perf = {}
    
    # Ajouter les indicateurs individuels avec préfixe
    for name, perf_df in individual_perf.items():
        all_perf[f"📊 {name}"] = perf_df
    
    # Ajouter les combinaisons avec leur type (emoji vert/rouge)
    for combo_name, combo_data in combination_results.items():
        perf_df = combo_data['df']
        combo_type = combo_data['type']
        
        if combo_type == 'buy':
            all_perf[f"🟢 {combo_name}"] = perf_df
        else:
            all_perf[f"🔴 {combo_name}"] = perf_df
    
    return all_perf


def get_combination_summary(combination_perf, horizons=[1, 2, 5, 10, 20]):
    """
    Crée un résumé trié des combinaisons par performance.
    """
    summary = []
    
    for combo_name, perf_df in combination_perf.items():
        stats = calculate_accuracy_stats(perf_df, horizons)
        
        # Calculer la moyenne des précisions sur tous les horizons
        valid_accuracies = [s['accuracy'] for h, s in stats.items() 
                          if s.get('accuracy') is not None]
        avg_accuracy = np.mean(valid_accuracies) if valid_accuracies else None
        
        # Total des signaux
        total_signals = sum(s.get('total_signals', 0) for s in stats.values())
        
        if avg_accuracy is not None and total_signals > 0:
            summary.append({
                'name': combo_name,
                'accuracy': avg_accuracy,
                'total_signals': total_signals,
                'stats': stats
            })
    
    # Trier par précision décroissante
    summary.sort(key=lambda x: x['accuracy'], reverse=True)
    
    return summary


def debug_combination_signals(df, config=None):
    """
    Fonction de debug pour voir combien de signaux chaque combinaison génère.
    """
    if config is None:
        config = get_default_config()
    
    df = _normalize_column_names(df)
    
    print("\n" + "="*60)
    print("DEBUG: Signaux générés par chaque combinaison")
    print("="*60)
    
    for combo_def in COMBINATION_DEFINITIONS:
        combo_name = combo_def['name']
        combo_type = combo_def['type']
        check_func = combo_def['check']
        
        count = 0
        for idx in range(len(df)):
            row = df.iloc[idx].to_dict()
            row_prev = df.iloc[idx - 1].to_dict() if idx > 0 else None
            try:
                if check_func(row, row_prev, config):
                    count += 1
            except:
                pass
        
        emoji = "🟢" if combo_type == 'buy' else "🔴"
        status = "✓" if count > 0 else "✗ VIDE"
        print(f"{emoji} {combo_name}: {count} signaux {status}")
    
    print("="*60 + "\n")