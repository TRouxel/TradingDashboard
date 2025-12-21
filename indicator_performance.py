# indicator_performance.py
"""
Module d'analyse de la performance des indicateurs.
Mesure la pertinence de chaque signal sur différents horizons temporels.
VERSION CORRIGÉE - Signaux améliorés
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
        performance_history['🎯 Recommandation'] = global_df
    
    return performance_history


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


def analyze_rsi_daily(df, config, horizons):
    """
    Analyse quotidienne du RSI - VERSION CORRIGÉE.
    
    CORRECTION: On ne signale plus quand RSI ENTRE en zone extrême,
    mais quand il en SORT (confirmation de retournement).
    """
    rsi_cfg = config.get('rsi', RSI)
    weights = config.get('signal_weights', {})
    base_weight = weights.get('rsi_exit_oversold', 2.0)
    
    signals = []
    intensities = []
    
    oversold = rsi_cfg.get('oversold', 30)
    overbought = rsi_cfg.get('overbought', 70)
    
    for idx in range(len(df)):
        rsi = df.iloc[idx].get('rsi')
        
        # Besoin du RSI précédent pour détecter le croisement
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
        
        # === SIGNAL D'ACHAT : RSI SORT de survente (croise au-dessus de 30) ===
        if rsi_prev <= oversold and rsi > oversold:
            # Confirmation avec stochastique
            if stoch_k > stoch_d:
                signals.append('buy')
                intensities.append(base_weight * 1.2)
            else:
                signals.append('buy')
                intensities.append(base_weight * 0.7)
        
        # === RSI remonte depuis zone basse avec momentum ===
        elif rsi_prev < 35 and rsi > rsi_prev + 3 and rsi < 50:
            if stoch_k > stoch_d:
                signals.append('buy')
                intensities.append(base_weight * 0.8)
            else:
                signals.append('neutral')
                intensities.append(0)
        
        # === SIGNAL DE VENTE : RSI SORT de surachat (croise en dessous de 70) ===
        elif rsi_prev >= overbought and rsi < overbought:
            if stoch_k < stoch_d:
                signals.append('sell')
                intensities.append(base_weight * 1.2)
            else:
                signals.append('sell')
                intensities.append(base_weight * 0.7)
        
        # === RSI descend depuis zone haute avec momentum ===
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
    """
    Analyse quotidienne du Stochastique - VERSION AMÉLIORÉE.
    
    CORRECTION: Ajout de la détection du croisement réel (pas juste la position).
    """
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
        
        # Valeurs précédentes pour détecter le croisement
        stoch_k_prev = df.iloc[idx - 1].get('stochastic_k')
        stoch_d_prev = df.iloc[idx - 1].get('stochastic_d')
        
        if pd.isna(stoch_k_prev) or pd.isna(stoch_d_prev):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        # Détecter le croisement haussier (%K croise au-dessus de %D)
        bullish_cross = stoch_k_prev <= stoch_d_prev and stoch_k > stoch_d
        bearish_cross = stoch_k_prev >= stoch_d_prev and stoch_k < stoch_d
        
        # === ACHAT : Croisement haussier en zone de survente ===
        if bullish_cross and stoch_k < oversold + 15:
            signals.append('buy')
            # Plus le croisement est bas, plus c'est fort
            intensity = base_weight * (1 + (oversold + 15 - stoch_k) / 30)
            intensities.append(min(intensity, base_weight * 1.5))
        
        # === VENTE : Croisement baissier en zone de surachat ===
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
        
        # Ajouter une confirmation : le prix doit rebondir
        if idx > 0:
            close = df.iloc[idx].get('close', 0)
            close_prev = df.iloc[idx - 1].get('close', 0)
            price_rising = close > close_prev
            price_falling = close < close_prev
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
    """
    Analyse quotidienne du MACD - VERSION CORRIGÉE.
    
    CORRECTIONS:
    1. Détecter le CROISEMENT réel (pas juste la position)
    2. Pondérer selon la position par rapport à zéro
    3. Ajouter un filtre de confirmation (histogramme croissant)
    """
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
        
        # Valeurs précédentes
        macd_prev = df.iloc[idx - 1].get('macd')
        macd_signal_prev = df.iloc[idx - 1].get('macd_signal')
        macd_hist_prev = df.iloc[idx - 1].get('macd_histogram')
        macd_hist_prev2 = df.iloc[idx - 2].get('macd_histogram')
        
        if pd.isna(macd_prev) or pd.isna(macd_signal_prev):
            signals.append('neutral')
            intensities.append(0)
            continue
        
        # Détecter les croisements
        bullish_cross = macd_prev <= macd_signal_prev and macd > macd_signal
        bearish_cross = macd_prev >= macd_signal_prev and macd < macd_signal
        
        # Histogramme croissant/décroissant (momentum)
        hist_increasing = macd_hist_prev is not None and macd_hist > macd_hist_prev
        hist_decreasing = macd_hist_prev is not None and macd_hist < macd_hist_prev
        
        # === ACHAT : Croisement haussier ===
        if bullish_cross:
            intensity = base_weight
            
            # Bonus si croisement au-dessus de zéro (plus fiable)
            if macd > 0:
                intensity *= 1.3
            # Bonus si histogramme confirme
            if hist_increasing:
                intensity *= 1.2
            
            signals.append('buy')
            intensities.append(min(intensity, base_weight * 2))
        
        # === VENTE : Croisement baissier ===
        elif bearish_cross:
            intensity = base_weight
            
            # Bonus si croisement en dessous de zéro
            if macd < 0:
                intensity *= 1.3
            if hist_decreasing:
                intensity *= 1.2
            
            signals.append('sell')
            intensities.append(min(intensity, base_weight * 2))
        
        # === Signal secondaire : Histogramme change de signe ===
        elif macd_hist_prev is not None:
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
            intensity = 0.5 + (adx - 20) / 40  # Plus l'ADX est fort, plus l'intensité est grande
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
    """
    Analyse quotidienne des Divergences RSI - VERSION CORRIGÉE.
    
    Utilise les divergences déjà calculées dans indicator_calculator.py
    (qui sera aussi corrigé).
    """
    weights = config.get('signal_weights', {})
    base_weight = weights.get('rsi_divergence', 2.0)
    
    signals = []
    intensities = []
    
    for idx in range(len(df)):
        rsi_div = df.iloc[idx].get('rsi_divergence', 'none')
        
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
    
    Returns:
        dict: {horizon: {'accuracy': %, 'total_signals': n, 'correct': n, 'wrong': n}}
    """
    stats = {}
    
    for h in horizons:
        correct_col = f'correct_{h}d'
        if correct_col not in perf_df.columns:
            continue
        
        # Filtrer les signaux non-neutres
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