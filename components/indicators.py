# components/indicators.py
"""
Calcul des contributions des indicateurs techniques.
"""


def calculate_indicator_contributions(row, config):
    """
    Calcule la contribution de chaque indicateur à la recommandation.
    Retourne une liste de dictionnaires avec les détails de chaque indicateur.
    """
    contributions = []
    weights = config.get('signal_weights', {})
    rsi_cfg = config.get('rsi', {})
    stoch_cfg = config.get('stochastic', {})
    adx_cfg = config.get('adx', {})
    
    # === RSI ===
    rsi = row.get('rsi')
    rsi_weight = weights.get('rsi_exit_oversold', 2.0)
    if rsi is not None:
        buy_contrib = 0
        sell_contrib = 0
        
        if rsi <= rsi_cfg.get('oversold', 30):
            rsi_interpretation = "Survente extrême"
            rsi_signal = "🟢 Achat"
            buy_contrib = rsi_weight * 1.2
        elif rsi_cfg.get('exit_oversold_min', 30) <= rsi <= rsi_cfg.get('exit_oversold_max', 40):
            stoch_k = row.get('stochastic_k', 50)
            stoch_d = row.get('stochastic_d', 50)
            if stoch_k and stoch_d and stoch_k > stoch_d:
                rsi_interpretation = "Sortie survente + confirmation stoch"
                rsi_signal = "🟢 Achat"
                buy_contrib = rsi_weight
            else:
                rsi_interpretation = "Sortie survente (sans confirmation)"
                rsi_signal = "🟡 Achat faible"
                buy_contrib = rsi_weight * 0.5
        elif rsi >= rsi_cfg.get('overbought', 70):
            rsi_interpretation = "Surachat extrême"
            rsi_signal = "🔴 Vente"
            sell_contrib = rsi_weight * 1.2
        elif rsi_cfg.get('exit_overbought_min', 60) <= rsi <= rsi_cfg.get('exit_overbought_max', 70):
            stoch_k = row.get('stochastic_k', 50)
            stoch_d = row.get('stochastic_d', 50)
            if stoch_k and stoch_d and stoch_k < stoch_d:
                rsi_interpretation = "Sortie surachat + confirmation stoch"
                rsi_signal = "🔴 Vente"
                sell_contrib = rsi_weight
            else:
                rsi_interpretation = "Sortie surachat (sans confirmation)"
                rsi_signal = "🟠 Vente faible"
                sell_contrib = rsi_weight * 0.5
        else:
            rsi_interpretation = "Zone neutre"
            rsi_signal = "⚪ Neutre"
        
        contributions.append({
            'name': 'RSI',
            'interpretation_guide': '<30 = survente (achat), >70 = surachat (vente)',
            'value': f"{rsi:.1f}",
            'signal': rsi_signal,
            'weight': rsi_weight,
            'buy_contrib': buy_contrib,
            'sell_contrib': sell_contrib,
            'interpretation': rsi_interpretation
        })
    
    # === STOCHASTIQUE ===
    stoch_k = row.get('stochastic_k')
    stoch_d = row.get('stochastic_d')
    stoch_weight = weights.get('stoch_bullish_cross', 1.0)
    if stoch_k is not None and stoch_d is not None:
        buy_contrib = 0
        sell_contrib = 0
        
        if stoch_k < stoch_cfg.get('oversold', 20) + 10:
            if stoch_k > stoch_d:
                stoch_interpretation = "Zone basse + croisement haussier"
                stoch_signal = "🟢 Achat"
                buy_contrib = stoch_weight
            else:
                stoch_interpretation = "Zone basse (attendre croisement)"
                stoch_signal = "🟡 Attention"
        elif stoch_k > stoch_cfg.get('overbought', 80) - 10:
            if stoch_k < stoch_d:
                stoch_interpretation = "Zone haute + croisement baissier"
                stoch_signal = "🔴 Vente"
                sell_contrib = stoch_weight
            else:
                stoch_interpretation = "Zone haute (attendre croisement)"
                stoch_signal = "🟠 Attention"
        elif stoch_k > 50 and stoch_k < stoch_d:
            stoch_interpretation = "Retournement baissier en zone médiane"
            stoch_signal = "🟠 Vente faible"
            sell_contrib = 0.5
        else:
            stoch_interpretation = "Zone neutre"
            stoch_signal = "⚪ Neutre"
        
        contributions.append({
            'name': 'Stochastique (%K/%D)',
            'interpretation_guide': 'Croisement %K/%D en zones extrêmes',
            'value': f"%K: {stoch_k:.1f} / %D: {stoch_d:.1f}",
            'signal': stoch_signal,
            'weight': stoch_weight,
            'buy_contrib': buy_contrib,
            'sell_contrib': sell_contrib,
            'interpretation': stoch_interpretation
        })
    
    # === MACD ===
    macd = row.get('macd')
    macd_signal_val = row.get('macd_signal')
    macd_hist = row.get('macd_histogram')
    macd_weight = weights.get('macd_bullish', 1.0)
    macd_hist_weight = weights.get('macd_histogram_positive', 0.5)
    
    if macd is not None and macd_signal_val is not None:
        buy_contrib = 0
        sell_contrib = 0
        
        if macd > macd_signal_val and macd_hist and macd_hist > 0:
            macd_interpretation = "Croisement haussier confirmé"
            macd_signal = "🟢 Achat"
            buy_contrib = macd_weight
        elif macd < macd_signal_val and macd_hist and macd_hist < 0:
            macd_interpretation = "Croisement baissier confirmé"
            macd_signal = "🔴 Vente"
            sell_contrib = macd_weight
            if macd < 0 and macd_signal_val < 0:
                sell_contrib += 0.5
                macd_interpretation += " + sous zéro"
        elif macd > macd_signal_val:
            macd_interpretation = "MACD > Signal (hist négatif)"
            macd_signal = "🟡 Mixte"
        else:
            macd_interpretation = "MACD < Signal (hist positif)"
            macd_signal = "🟠 Mixte"
        
        contributions.append({
            'name': 'MACD',
            'interpretation_guide': 'Croisement MACD/Signal + histogramme',
            'value': f"{macd:.2f} vs {macd_signal_val:.2f}",
            'signal': macd_signal,
            'weight': macd_weight,
            'buy_contrib': buy_contrib,
            'sell_contrib': sell_contrib,
            'interpretation': macd_interpretation
        })
        
        # Histogramme MACD séparé
        if macd_hist is not None:
            hist_buy = 0
            hist_sell = 0
            if macd_hist > 0:
                hist_interpretation = "Momentum haussier"
                hist_signal = "🟢 Achat"
                hist_buy = macd_hist_weight
            elif macd_hist < 0:
                hist_interpretation = "Momentum baissier"
                hist_signal = "🔴 Vente"
                hist_sell = macd_hist_weight
            else:
                hist_interpretation = "Neutre"
                hist_signal = "⚪ Neutre"
            
            contributions.append({
                'name': 'Histogramme MACD',
                'interpretation_guide': 'Force du momentum',
                'value': f"{macd_hist:.3f}",
                'signal': hist_signal,
                'weight': macd_hist_weight,
                'buy_contrib': hist_buy,
                'sell_contrib': hist_sell,
                'interpretation': hist_interpretation
            })
    
    # === TENDANCE ===
    trend = row.get('trend', 'neutral')
    trend_weight = weights.get('trend_bonus', 1.0)
    buy_contrib = 0
    sell_contrib = 0
    
    if trend == 'strong_bullish':
        trend_interpretation = "Tendance haussière forte"
        trend_signal = "🟢 Achat"
        buy_contrib = trend_weight
    elif trend == 'bullish':
        trend_interpretation = "Tendance haussière"
        trend_signal = "🟢 Achat"
        buy_contrib = trend_weight
    elif trend == 'strong_bearish':
        trend_interpretation = "Tendance baissière forte"
        trend_signal = "🔴 Vente"
        sell_contrib = trend_weight
    elif trend == 'bearish':
        trend_interpretation = "Tendance baissière"
        trend_signal = "🔴 Vente"
        sell_contrib = trend_weight
    else:
        trend_interpretation = "Tendance neutre"
        trend_signal = "⚪ Neutre"
    
    contributions.append({
        'name': 'Tendance (MAs)',
        'interpretation_guide': 'Alignement Prix > SMA20 > SMA50 > SMA200',
        'value': trend.replace('_', ' ').title(),
        'signal': trend_signal,
        'weight': trend_weight,
        'buy_contrib': buy_contrib,
        'sell_contrib': sell_contrib,
        'interpretation': trend_interpretation
    })
    
    # === ADX / DI ===
    adx = row.get('adx')
    di_plus = row.get('di_plus')
    di_minus = row.get('di_minus')
    
    if adx is not None and di_plus is not None and di_minus is not None:
        buy_contrib = 0
        sell_contrib = 0
        
        if adx > adx_cfg.get('weak', 20):
            if di_plus > di_minus:
                adx_interpretation = f"Tendance haussière (ADX={adx:.0f})"
                adx_signal = "🟢 Achat"
                buy_contrib = 0.5
            else:
                adx_interpretation = f"Tendance baissière (ADX={adx:.0f})"
                adx_signal = "🔴 Vente"
                sell_contrib = 0.5
        else:
            adx_interpretation = f"Pas de tendance claire (ADX={adx:.0f})"
            adx_signal = "⚪ Neutre"
        
        contributions.append({
            'name': 'ADX / DI+/DI-',
            'interpretation_guide': 'Force et direction de la tendance',
            'value': f"ADX:{adx:.0f} DI+:{di_plus:.0f} DI-:{di_minus:.0f}",
            'signal': adx_signal,
            'weight': 0.5,
            'buy_contrib': buy_contrib,
            'sell_contrib': sell_contrib,
            'interpretation': adx_interpretation
        })
    
    # === PRIX VS MOYENNES MOBILES ===
    close = row.get('close')
    sma_20 = row.get('sma_20')
    sma_50 = row.get('sma_50')
    
    if close is not None and sma_20 is not None and sma_50 is not None:
        buy_contrib = 0
        sell_contrib = 0
        
        if close < sma_20 < sma_50:
            ma_interpretation = "Prix < SMA20 < SMA50 (structure baissière)"
            ma_signal = "🔴 Vente"
            sell_contrib = 0.7
        elif close < sma_20:
            ma_interpretation = "Prix sous SMA20"
            ma_signal = "🟠 Vente faible"
            sell_contrib = 0.3
        elif close > sma_20 > sma_50:
            ma_interpretation = "Prix > SMA20 > SMA50 (structure haussière)"
            ma_signal = "🟢 Achat"
            buy_contrib = 0.7
        else:
            ma_interpretation = "Structure mixte"
            ma_signal = "⚪ Neutre"
        
        contributions.append({
            'name': 'Prix vs MAs',
            'interpretation_guide': 'Position du prix par rapport aux moyennes',
            'value': f"Close:{close:.2f} SMA20:{sma_20:.2f}",
            'signal': ma_signal,
            'weight': 0.7,
            'buy_contrib': buy_contrib,
            'sell_contrib': sell_contrib,
            'interpretation': ma_interpretation
        })
    
    # === DIVERGENCE RSI ===
    rsi_div = row.get('rsi_divergence', 'none')
    div_weight = weights.get('rsi_divergence', 2.0)
    buy_contrib = 0
    sell_contrib = 0
    
    if rsi_div == 'bullish':
        div_interpretation = "Divergence haussière détectée"
        div_signal = "🟢 Achat"
        buy_contrib = div_weight
    elif rsi_div == 'bearish':
        div_interpretation = "Divergence baissière détectée"
        div_signal = "🔴 Vente"
        sell_contrib = div_weight
    else:
        div_interpretation = "Aucune divergence"
        div_signal = "⚪ Neutre"
    
    contributions.append({
        'name': 'Divergence RSI',
        'interpretation_guide': 'Prix vs RSI en désaccord = retournement',
        'value': rsi_div.title() if rsi_div != 'none' else 'Aucune',
        'signal': div_signal,
        'weight': div_weight,
        'buy_contrib': buy_contrib,
        'sell_contrib': sell_contrib,
        'interpretation': div_interpretation
    })
    
    # === PATTERN ===
    pattern = row.get('pattern', 'Aucun')
    pattern_dir = row.get('pattern_direction', 'neutral')
    pattern_weight = weights.get('pattern_bullish', 1.5)
    buy_contrib = 0
    sell_contrib = 0
    
    if pattern != 'Aucun' and pattern_dir == 'bullish':
        pattern_interpretation = f"Pattern haussier: {pattern}"
        pattern_signal = "🟢 Achat"
        buy_contrib = pattern_weight
    elif pattern != 'Aucun' and pattern_dir == 'bearish':
        pattern_interpretation = f"Pattern baissier: {pattern}"
        pattern_signal = "🔴 Vente"
        sell_contrib = pattern_weight
    else:
        pattern_interpretation = "Aucun pattern significatif"
        pattern_signal = "⚪ Neutre"
    
    contributions.append({
        'name': 'Pattern Chandelier',
        'interpretation_guide': 'Figures de retournement (Engulfing, Hammer...)',
        'value': pattern,
        'signal': pattern_signal,
        'weight': pattern_weight,
        'buy_contrib': buy_contrib,
        'sell_contrib': sell_contrib,
        'interpretation': pattern_interpretation
    })
    
    return contributions