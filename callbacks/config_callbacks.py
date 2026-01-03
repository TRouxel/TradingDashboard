# callbacks/config_callbacks.py
"""
Callbacks pour la gestion de la configuration.
VERSION 2.3 - CORRECTION COMPLÈTE du passage de la config
"""
from dash import html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from config import get_default_config, get_profile_config, TRADING_PROFILES, INDIVIDUAL_WEIGHTS, COMBINATION_WEIGHTS


def register_config_callbacks(app):
    """Enregistre les callbacks de configuration."""
    
    @app.callback(
        Output("config-modal", "is_open"),
        [Input("open-config-btn", "n_clicks"),
         Input("config-apply-btn", "n_clicks"),
         Input("config-reset-btn", "n_clicks")],
        [State("config-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_config_modal(open_clicks, apply_clicks, reset_clicks, is_open):
        return not is_open

    @app.callback(
        [Output('profile-description', 'children'),
         Output('profile-details', 'children')],
        [Input('config-trading-profile', 'value')],
        prevent_initial_call=True
    )
    def update_profile_description(profile_name):
        if not profile_name or profile_name not in TRADING_PROFILES:
            return "", ""
        
        profile = TRADING_PROFILES[profile_name]
        
        description = html.P(profile['description'], className="text-info")
        
        details = html.Ul([
            html.Li(f"Seuil de conviction: {profile['min_conviction_threshold']}"),
            html.Li(f"Écart minimum: {profile['conviction_difference']}"),
            html.Li(f"Bonus combinaisons: x{profile['combination_bonus']}"),
            html.Li(f"Min. combinaisons pour signal: {profile['min_combinations_for_signal']}"),
        ])
        
        return description, details

    @app.callback(
        [Output('config-store', 'data'),
         Output('config-summary', 'children'),
         Output('signal-timeframe-quick', 'value')],
        [Input('config-apply-btn', 'n_clicks'),
         Input('config-reset-btn', 'n_clicks'),
         Input('signal-timeframe-quick', 'value'),
         Input('config-trading-profile', 'value')],
        [State('config-signal-timeframe', 'value'),
         # RSI
         State('config-rsi-period', 'value'),
         State('config-rsi-oversold', 'value'),
         State('config-rsi-overbought', 'value'),
         State('config-rsi-exit-oversold-min', 'value'),
         State('config-rsi-exit-oversold-max', 'value'),
         State('config-rsi-exit-overbought-min', 'value'),
         State('config-rsi-exit-overbought-max', 'value'),
         # Stochastique
         State('config-stoch-k', 'value'),
         State('config-stoch-d', 'value'),
         State('config-stoch-oversold', 'value'),
         State('config-stoch-overbought', 'value'),
         # Bollinger
         State('config-bb-period', 'value'),
         State('config-bb-std', 'value'),
         # Moyennes mobiles
         State('config-sma-short', 'value'),
         State('config-sma-medium', 'value'),
         State('config-sma-long', 'value'),
         # MACD
         State('config-macd-fast', 'value'),
         State('config-macd-slow', 'value'),
         State('config-macd-signal', 'value'),
         # ADX
         State('config-adx-period', 'value'),
         State('config-adx-strong', 'value'),
         State('config-adx-very-strong', 'value'),
         # === TOUTES LES COMBINAISONS D'ACHAT (13) ===
         State('config-comb-divergence-bullish-stoch', 'value'),
         State('config-comb-triple-confirm-buy', 'value'),
         State('config-comb-macd-cross-rsi-low', 'value'),
         State('config-comb-bollinger-low-rsi-low', 'value'),
         State('config-comb-rsi-low-stoch-bullish', 'value'),
         State('config-comb-pattern-bullish-rsi-low', 'value'),
         State('config-comb-bollinger-low-stoch-bullish', 'value'),
         State('config-comb-adx-strong-di-plus', 'value'),
         State('config-comb-macd-bullish-trend-bullish', 'value'),
         State('config-comb-macd-positive-trend-bullish', 'value'),
         State('config-comb-pattern-bullish-trend-bullish', 'value'),
         State('config-comb-stoch-cross-bullish-rsi-low', 'value'),
         State('config-comb-rsi-exit-oversold-stoch', 'value'),
         # === TOUTES LES COMBINAISONS DE VENTE (13) ===
         State('config-comb-divergence-bearish-stoch', 'value'),
         State('config-comb-triple-confirm-sell', 'value'),
         State('config-comb-macd-cross-bearish-rsi-high', 'value'),
         State('config-comb-bollinger-high-rsi-high', 'value'),
         State('config-comb-rsi-high-stoch-bearish', 'value'),
         State('config-comb-pattern-bearish-rsi-high', 'value'),
         State('config-comb-bollinger-high-stoch-bearish', 'value'),
         State('config-comb-adx-strong-di-minus', 'value'),
         State('config-comb-macd-bearish-trend-bearish', 'value'),
         State('config-comb-macd-negative-trend-bearish', 'value'),
         State('config-comb-pattern-bearish-trend-bearish', 'value'),
         State('config-comb-stoch-cross-bearish-rsi-high', 'value'),
         State('config-comb-rsi-exit-overbought-stoch', 'value'),
         State('config-comb-price-below-mas-macd-negative', 'value'),
         # Poids des indicateurs individuels
         State('config-ind-divergence', 'value'),
         State('config-ind-trend-strong', 'value'),
         State('config-ind-trend-weak', 'value'),
         State('config-ind-pattern', 'value'),
         State('config-ind-rsi-extreme', 'value'),
         State('config-ind-stoch', 'value'),
         State('config-ind-macd', 'value'),
         State('config-ind-bollinger', 'value'),
         # Seuils de décision
         State('config-decision-threshold', 'value'),
         State('config-decision-difference', 'value'),
         State('config-decision-penalty', 'value'),
         State('config-decision-adx-level', 'value'),
         State('config-decision-adx-bonus', 'value'),
         State('config-decision-min-combos', 'value'),
         # Divergences
         State('config-div-lookback', 'value'),
         State('config-div-rsi-low', 'value'),
         State('config-div-rsi-high', 'value'),
         # Config actuelle
         State('config-store', 'data')],
        prevent_initial_call=True
    )
    def update_config(apply_clicks, reset_clicks, quick_timeframe, trading_profile,
                      signal_tf,
                      rsi_period, rsi_os, rsi_ob, rsi_exit_os_min, rsi_exit_os_max, rsi_exit_ob_min, rsi_exit_ob_max,
                      stoch_k, stoch_d, stoch_os, stoch_ob,
                      bb_period, bb_std,
                      sma_short, sma_medium, sma_long,
                      macd_fast, macd_slow, macd_signal,
                      adx_period, adx_strong, adx_very_strong,
                      # Combinaisons d'achat
                      comb_divergence_bullish_stoch, comb_triple_confirm_buy, comb_macd_cross_rsi_low,
                      comb_bollinger_low_rsi_low, comb_rsi_low_stoch_bullish, comb_pattern_bullish_rsi_low,
                      comb_bollinger_low_stoch_bullish, comb_adx_strong_di_plus, comb_macd_bullish_trend_bullish,
                      comb_macd_positive_trend_bullish, comb_pattern_bullish_trend_bullish,
                      comb_stoch_cross_bullish_rsi_low, comb_rsi_exit_oversold_stoch,
                      # Combinaisons de vente
                      comb_divergence_bearish_stoch, comb_triple_confirm_sell, comb_macd_cross_bearish_rsi_high,
                      comb_bollinger_high_rsi_high, comb_rsi_high_stoch_bearish, comb_pattern_bearish_rsi_high,
                      comb_bollinger_high_stoch_bearish, comb_adx_strong_di_minus, comb_macd_bearish_trend_bearish,
                      comb_macd_negative_trend_bearish, comb_pattern_bearish_trend_bearish,
                      comb_stoch_cross_bearish_rsi_high, comb_rsi_exit_overbought_stoch,
                      comb_price_below_mas_macd_negative,
                      # Indicateurs individuels
                      ind_divergence, ind_trend_strong, ind_trend_weak, ind_pattern,
                      ind_rsi_extreme, ind_stoch, ind_macd, ind_bollinger,
                      dec_threshold, dec_diff, dec_penalty, dec_adx_level, dec_adx_bonus, dec_min_combos,
                      div_lookback, div_rsi_low, div_rsi_high,
                      current_config):
        
        triggered = ctx.triggered_id
        
        print(f"\n{'='*60}")
        print(f"🔧 update_config TRIGGERED by: {triggered}")
        print(f"   dec_threshold reçu = {dec_threshold}")
        print(f"   ind_divergence reçu = {ind_divergence}")
        print(f"{'='*60}")
        
        # Reset
        if triggered == 'config-reset-btn':
            config = get_default_config()
            summary = "🔄 Configuration réinitialisée"
            return config, summary, config['signal_timeframe']
        
        # Changement de profil de trading
        if triggered == 'config-trading-profile' and trading_profile:
            config = get_profile_config(trading_profile)
            summary = f"🎯 Profil '{TRADING_PROFILES[trading_profile]['name']}' appliqué"
            return config, summary, config['signal_timeframe']
        
        # Changement rapide du timeframe - GARDER la config actuelle MAIS mettre à jour le timeframe
        if triggered == 'signal-timeframe-quick':
            config = current_config.copy() if current_config else get_default_config()
            config['signal_timeframe'] = quick_timeframe
            summary = f"⏱️ Fenêtre: {quick_timeframe}j | Seuil: {config['decision']['min_conviction_threshold']}"
            return config, summary, quick_timeframe
        
        # Application manuelle des paramètres (triggered == 'config-apply-btn')
        config = build_config_from_inputs(
            signal_tf,
            rsi_period, rsi_os, rsi_ob, rsi_exit_os_min, rsi_exit_os_max, rsi_exit_ob_min, rsi_exit_ob_max,
            stoch_k, stoch_d, stoch_os, stoch_ob,
            bb_period, bb_std,
            sma_short, sma_medium, sma_long,
            macd_fast, macd_slow, macd_signal,
            adx_period, adx_strong, adx_very_strong,
            # Combinaisons d'achat
            comb_divergence_bullish_stoch, comb_triple_confirm_buy, comb_macd_cross_rsi_low,
            comb_bollinger_low_rsi_low, comb_rsi_low_stoch_bullish, comb_pattern_bullish_rsi_low,
            comb_bollinger_low_stoch_bullish, comb_adx_strong_di_plus, comb_macd_bullish_trend_bullish,
            comb_macd_positive_trend_bullish, comb_pattern_bullish_trend_bullish,
            comb_stoch_cross_bullish_rsi_low, comb_rsi_exit_oversold_stoch,
            # Combinaisons de vente
            comb_divergence_bearish_stoch, comb_triple_confirm_sell, comb_macd_cross_bearish_rsi_high,
            comb_bollinger_high_rsi_high, comb_rsi_high_stoch_bearish, comb_pattern_bearish_rsi_high,
            comb_bollinger_high_stoch_bearish, comb_adx_strong_di_minus, comb_macd_bearish_trend_bearish,
            comb_macd_negative_trend_bearish, comb_pattern_bearish_trend_bearish,
            comb_stoch_cross_bearish_rsi_high, comb_rsi_exit_overbought_stoch,
            comb_price_below_mas_macd_negative,
            # Indicateurs individuels
            ind_divergence, ind_trend_strong, ind_trend_weak, ind_pattern,
            ind_rsi_extreme, ind_stoch, ind_macd, ind_bollinger,
            dec_threshold, dec_diff, dec_penalty, dec_adx_level, dec_adx_bonus, dec_min_combos,
            div_lookback, div_rsi_low, div_rsi_high,
            current_config
        )
        
        # Compter les combinaisons actives
        comb_weights = config.get('combination_weights', {})
        active_combos = sum(1 for v in comb_weights.values() if v and v > 0)
        
        # Compter les indicateurs individuels actifs
        ind_weights = config.get('individual_weights', {})
        active_inds = sum(1 for v in ind_weights.values() if v and v > 0)
        
        # DEBUG: Afficher les valeurs FINALES dans la config
        print(f"\n🔧 CONFIG FINALE CONSTRUITE:")
        print(f"   decision.min_conviction_threshold = {config['decision']['min_conviction_threshold']}")
        print(f"   decision.conviction_difference = {config['decision']['conviction_difference']}")
        print(f"   decision.min_combinations_for_signal = {config['decision']['min_combinations_for_signal']}")
        print(f"   individual_weights.rsi_divergence = {config['individual_weights']['rsi_divergence']}")
        print(f"   Active combos: {active_combos}, Active inds: {active_inds}")
        
        summary = f"✅ Config | ⏱️ {config['signal_timeframe']}j | Seuil: {config['decision']['min_conviction_threshold']} | Combos: {active_combos}/26 | Inds: {active_inds}"
        
        return config, summary, config['signal_timeframe']

    # Toggle collapse callbacks
    @app.callback(
        Output("collapse-technical-summary", "is_open"),
        Input("collapse-technical-summary-btn", "n_clicks"),
        State("collapse-technical-summary", "is_open"),
        prevent_initial_call=True
    )
    def toggle_technical_summary(n_clicks, is_open):
        return not is_open

    @app.callback(
        Output("collapse-fundamental-summary", "is_open"),
        Input("collapse-fundamental-summary-btn", "n_clicks"),
        State("collapse-fundamental-summary", "is_open"),
        prevent_initial_call=True
    )
    def toggle_fundamental_summary(n_clicks, is_open):
        return not is_open

    @app.callback(
        Output("collapse-technical", "is_open"),
        Input("collapse-technical-btn", "n_clicks"),
        State("collapse-technical", "is_open"),
        prevent_initial_call=True
    )
    def toggle_technical_collapse(n_clicks, is_open):
        return not is_open

    # Reset zoom quand on change d'actif
    @app.callback(
        Output('zoom-range-store', 'data', allow_duplicate=True),
        Input('asset-dropdown', 'value'),
        prevent_initial_call=True
    )
    def reset_zoom_on_asset_change(asset):
        return None


def build_config_from_inputs(
    signal_tf,
    rsi_period, rsi_os, rsi_ob, rsi_exit_os_min, rsi_exit_os_max, rsi_exit_ob_min, rsi_exit_ob_max,
    stoch_k, stoch_d, stoch_os, stoch_ob,
    bb_period, bb_std,
    sma_short, sma_medium, sma_long,
    macd_fast, macd_slow, macd_signal,
    adx_period, adx_strong, adx_very_strong,
    # Combinaisons d'achat (13)
    comb_divergence_bullish_stoch, comb_triple_confirm_buy, comb_macd_cross_rsi_low,
    comb_bollinger_low_rsi_low, comb_rsi_low_stoch_bullish, comb_pattern_bullish_rsi_low,
    comb_bollinger_low_stoch_bullish, comb_adx_strong_di_plus, comb_macd_bullish_trend_bullish,
    comb_macd_positive_trend_bullish, comb_pattern_bullish_trend_bullish,
    comb_stoch_cross_bullish_rsi_low, comb_rsi_exit_oversold_stoch,
    # Combinaisons de vente (13)
    comb_divergence_bearish_stoch, comb_triple_confirm_sell, comb_macd_cross_bearish_rsi_high,
    comb_bollinger_high_rsi_high, comb_rsi_high_stoch_bearish, comb_pattern_bearish_rsi_high,
    comb_bollinger_high_stoch_bearish, comb_adx_strong_di_minus, comb_macd_bearish_trend_bearish,
    comb_macd_negative_trend_bearish, comb_pattern_bearish_trend_bearish,
    comb_stoch_cross_bearish_rsi_high, comb_rsi_exit_overbought_stoch,
    comb_price_below_mas_macd_negative,
    # Indicateurs individuels
    ind_divergence, ind_trend_strong, ind_trend_weak, ind_pattern,
    ind_rsi_extreme, ind_stoch, ind_macd, ind_bollinger,
    dec_threshold, dec_diff, dec_penalty, dec_adx_level, dec_adx_bonus, dec_min_combos,
    div_lookback, div_rsi_low, div_rsi_high,
    current_config
):
    """
    Construit la configuration à partir des inputs du formulaire.
    VERSION CORRIGÉE: Utilise DIRECTEMENT les valeurs des inputs.
    """
    default = get_default_config()
    
    # Fonction pour récupérer une valeur - utilise la valeur par défaut SEULEMENT si None
    def val(v, default_val):
        """Retourne v si v n'est pas None, sinon default_val.
        IMPORTANT: 0 est une valeur valide, ne pas la traiter comme None!
        """
        if v is None:
            print(f"   [val] v=None, using default={default_val}")
            return default_val
        print(f"   [val] v={v} (type={type(v).__name__}), returning as-is")
        return v
    
    # DEBUG
    print(f"\n   build_config_from_inputs INPUTS:")
    print(f"      dec_threshold = {dec_threshold} (type: {type(dec_threshold)})")
    print(f"      dec_diff = {dec_diff}")
    print(f"      dec_min_combos = {dec_min_combos}")
    print(f"      ind_divergence = {ind_divergence}")
    
    # DEBUG: Afficher les valeurs BRUTES reçues
    print(f"\n   RAW INPUTS:")
    print(f"      dec_threshold RAW = {dec_threshold} (type: {type(dec_threshold)})")
    print(f"      dec_diff RAW = {dec_diff}")
    print(f"      dec_min_combos RAW = {dec_min_combos}")
    
    # IMPORTANT: Utiliser directement les valeurs reçues, pas les valeurs par défaut
    config = {
        'signal_timeframe': val(signal_tf, 1),
        'rsi': {
            'period': val(rsi_period, 14),
            'oversold': val(rsi_os, 30),
            'overbought': val(rsi_ob, 70),
            'exit_oversold_min': val(rsi_exit_os_min, 30),
            'exit_oversold_max': val(rsi_exit_os_max, 40),
            'exit_overbought_min': val(rsi_exit_ob_min, 60),
            'exit_overbought_max': val(rsi_exit_ob_max, 70),
        },
        'stochastic': {
            'k_period': val(stoch_k, 14),
            'd_period': val(stoch_d, 3),
            'smooth': 3,
            'oversold': val(stoch_os, 20),
            'overbought': val(stoch_ob, 80),
        },
        'bollinger': {
            'period': val(bb_period, 20),
            'std_dev': val(bb_std, 2.0),
            'squeeze_threshold': 0.05,
        },
        'moving_averages': {
            'sma_short': val(sma_short, 20),
            'sma_medium': val(sma_medium, 50),
            'sma_long': val(sma_long, 200),
            'ema_fast': 12,
            'ema_slow': 26,
        },
        'macd': {
            'fast': val(macd_fast, 12),
            'slow': val(macd_slow, 26),
            'signal': val(macd_signal, 9),
        },
        'adx': {
            'period': val(adx_period, 14),
            'weak': 20,
            'strong': val(adx_strong, 25),
            'very_strong': val(adx_very_strong, 40),
        },
        # === COMBINAISONS ===
        'combination_weights': {
            # Combinaisons d'achat (13)
            'divergence_bullish_stoch': val(comb_divergence_bullish_stoch, 0),
            'triple_confirm_buy': val(comb_triple_confirm_buy, 0),
            'macd_cross_rsi_low': val(comb_macd_cross_rsi_low, 0),
            'bollinger_low_rsi_low': val(comb_bollinger_low_rsi_low, 0),
            'rsi_low_stoch_bullish': val(comb_rsi_low_stoch_bullish, 0),
            'pattern_bullish_rsi_low': val(comb_pattern_bullish_rsi_low, 0),
            'bollinger_low_stoch_bullish': val(comb_bollinger_low_stoch_bullish, 0),
            'adx_strong_di_plus': val(comb_adx_strong_di_plus, 0),
            'macd_bullish_trend_bullish': val(comb_macd_bullish_trend_bullish, 0),
            'macd_positive_trend_bullish': val(comb_macd_positive_trend_bullish, 0),
            'pattern_bullish_trend_bullish': val(comb_pattern_bullish_trend_bullish, 0),
            'stoch_cross_bullish_rsi_low': val(comb_stoch_cross_bullish_rsi_low, 0),
            'rsi_exit_oversold_stoch': val(comb_rsi_exit_oversold_stoch, 0),
            # Combinaisons de vente (13)
            'divergence_bearish_stoch': val(comb_divergence_bearish_stoch, 0),
            'triple_confirm_sell': val(comb_triple_confirm_sell, 0),
            'macd_cross_bearish_rsi_high': val(comb_macd_cross_bearish_rsi_high, 0),
            'bollinger_high_rsi_high': val(comb_bollinger_high_rsi_high, 0),
            'rsi_high_stoch_bearish': val(comb_rsi_high_stoch_bearish, 0),
            'pattern_bearish_rsi_high': val(comb_pattern_bearish_rsi_high, 0),
            'bollinger_high_stoch_bearish': val(comb_bollinger_high_stoch_bearish, 0),
            'adx_strong_di_minus': val(comb_adx_strong_di_minus, 0),
            'macd_bearish_trend_bearish': val(comb_macd_bearish_trend_bearish, 0),
            'macd_negative_trend_bearish': val(comb_macd_negative_trend_bearish, 0),
            'pattern_bearish_trend_bearish': val(comb_pattern_bearish_trend_bearish, 0),
            'stoch_cross_bearish_rsi_high': val(comb_stoch_cross_bearish_rsi_high, 0),
            'rsi_exit_overbought_stoch': val(comb_rsi_exit_overbought_stoch, 0),
            'price_below_mas_macd_negative': val(comb_price_below_mas_macd_negative, 0),
        },
        # === INDICATEURS INDIVIDUELS ===
        'individual_weights': {
            'rsi_divergence': val(ind_divergence, 0),
            'trend_strong': val(ind_trend_strong, 0),
            'trend_weak': val(ind_trend_weak, 0),
            'pattern_signal': val(ind_pattern, 0),
            'rsi_extreme': val(ind_rsi_extreme, 0),
            'rsi_exit_zone': 0,
            'stoch_cross': val(ind_stoch, 0),
            'stoch_extreme': 0,
            'macd_cross': val(ind_macd, 0),
            'macd_histogram': val(ind_macd, 0) * 0.5 if ind_macd else 0,
            'bollinger_touch': val(ind_bollinger, 0),
            'bollinger_zone': val(ind_bollinger, 0) * 0.6 if ind_bollinger else 0,
            'adx_direction': 0,
        },
        # Ancien format pour compatibilité
        'signal_weights': {
            'rsi_exit_oversold': val(ind_divergence, 0),
            'rsi_exit_overbought': val(ind_divergence, 0),
            'stoch_bullish_cross': val(ind_stoch, 0),
            'stoch_bearish_cross': val(ind_stoch, 0),
            'macd_bullish': val(ind_macd, 0),
            'macd_bearish': val(ind_macd, 0),
            'macd_histogram_positive': 0,
            'macd_histogram_negative': 0,
            'rsi_divergence': val(ind_divergence, 0),
            'pattern_bullish': val(ind_pattern, 0),
            'pattern_bearish': val(ind_pattern, 0),
            'trend_bonus': val(ind_trend_strong, 0),
            'bollinger_lower': val(ind_bollinger, 0),
            'bollinger_upper': val(ind_bollinger, 0),
        },
        # === DÉCISION - C'EST ICI LE PROBLÈME ===
        'decision': {
            'min_conviction_threshold': val(dec_threshold, 2.5),
            'conviction_difference': val(dec_diff, 0.5),
            'against_trend_penalty': val(dec_penalty, 0.5),
            'adx_confirmation_level': val(dec_adx_level, 30),
            'adx_confirmation_bonus': val(dec_adx_bonus, 1.2),
            'max_conviction': 5,
            'use_combinations': True,
            'combination_bonus': 1.3,
            'min_combinations_for_signal': val(dec_min_combos, 1),
        },
        'trend': current_config.get('trend', default['trend']) if current_config else default['trend'],
        'divergence': {
            'lookback_period': val(div_lookback, 14),
            'rsi_low_threshold': val(div_rsi_low, 40),
            'rsi_high_threshold': val(div_rsi_high, 60),
        },
        'optional_filters': current_config.get('optional_filters', default['optional_filters']) if current_config else default['optional_filters'],
        'trading_profile': 'custom',
    }
    
    # DEBUG FINAL
    print(f"\n   build_config_from_inputs OUTPUT:")
    print(f"      config['decision']['min_conviction_threshold'] = {config['decision']['min_conviction_threshold']}")
    print(f"      config['individual_weights']['rsi_divergence'] = {config['individual_weights']['rsi_divergence']}")
    
    return config