# callbacks/config_callbacks.py
"""
Callbacks pour la gestion de la configuration.
"""
from dash import Input, Output, State, ctx
from config import get_default_config


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
        [Output('config-store', 'data'),
         Output('config-summary', 'children'),
         Output('signal-timeframe-quick', 'value')],
        [Input('config-apply-btn', 'n_clicks'),
         Input('config-reset-btn', 'n_clicks'),
         Input('signal-timeframe-quick', 'value')],
        [State('config-signal-timeframe', 'value'),
         State('config-rsi-period', 'value'),
         State('config-rsi-oversold', 'value'),
         State('config-rsi-overbought', 'value'),
         State('config-rsi-exit-oversold-min', 'value'),
         State('config-rsi-exit-oversold-max', 'value'),
         State('config-rsi-exit-overbought-min', 'value'),
         State('config-rsi-exit-overbought-max', 'value'),
         State('config-stoch-k', 'value'),
         State('config-stoch-d', 'value'),
         State('config-stoch-oversold', 'value'),
         State('config-stoch-overbought', 'value'),
         State('config-sma-short', 'value'),
         State('config-sma-medium', 'value'),
         State('config-sma-long', 'value'),
         State('config-macd-fast', 'value'),
         State('config-macd-slow', 'value'),
         State('config-macd-signal', 'value'),
         State('config-adx-period', 'value'),
         State('config-adx-strong', 'value'),
         State('config-adx-very-strong', 'value'),
         State('config-weight-rsi', 'value'),
         State('config-weight-stoch', 'value'),
         State('config-weight-macd', 'value'),
         State('config-weight-macd-hist', 'value'),
         State('config-weight-divergence', 'value'),
         State('config-weight-pattern', 'value'),
         State('config-weight-trend', 'value'),
         State('config-decision-threshold', 'value'),
         State('config-decision-difference', 'value'),
         State('config-decision-penalty', 'value'),
         State('config-decision-adx-level', 'value'),
         State('config-decision-adx-bonus', 'value'),
         State('config-div-lookback', 'value'),
         State('config-div-rsi-low', 'value'),
         State('config-div-rsi-high', 'value'),
         State('config-store', 'data')],
        prevent_initial_call=True
    )
    def update_config(apply_clicks, reset_clicks, quick_timeframe,
                      signal_tf, rsi_period, rsi_os, rsi_ob, rsi_exit_os_min, rsi_exit_os_max, rsi_exit_ob_min, rsi_exit_ob_max,
                      stoch_k, stoch_d, stoch_os, stoch_ob,
                      sma_short, sma_medium, sma_long,
                      macd_fast, macd_slow, macd_signal,
                      adx_period, adx_strong, adx_very_strong,
                      w_rsi, w_stoch, w_macd, w_macd_hist, w_div, w_pattern, w_trend,
                      dec_threshold, dec_diff, dec_penalty, dec_adx_level, dec_adx_bonus,
                      div_lookback, div_rsi_low, div_rsi_high,
                      current_config):
        
        triggered = ctx.triggered_id
        
        if triggered == 'config-reset-btn':
            config = get_default_config()
            summary = "🔄 Configuration réinitialisée"
            return config, summary, config['signal_timeframe']
        
        if triggered == 'signal-timeframe-quick':
            config = current_config.copy()
            config['signal_timeframe'] = quick_timeframe
            summary = f"⏱️ Fenêtre: {quick_timeframe}j | Seuil: {config['decision']['min_conviction_threshold']} | RSI: {config['rsi']['oversold']}-{config['rsi']['overbought']}"
            return config, summary, quick_timeframe
        
        config = {
            'signal_timeframe': signal_tf or 1,
            'rsi': {
                'period': rsi_period or 14,
                'oversold': rsi_os or 30,
                'overbought': rsi_ob or 70,
                'exit_oversold_min': rsi_exit_os_min or 30,
                'exit_oversold_max': rsi_exit_os_max or 40,
                'exit_overbought_min': rsi_exit_ob_min or 60,
                'exit_overbought_max': rsi_exit_ob_max or 70,
            },
            'stochastic': {
                'k_period': stoch_k or 14,
                'd_period': stoch_d or 3,
                'smooth': 3,
                'oversold': stoch_os or 20,
                'overbought': stoch_ob or 80,
            },
            'moving_averages': {
                'sma_short': sma_short or 20,
                'sma_medium': sma_medium or 50,
                'sma_long': sma_long or 200,
                'ema_fast': 12,
                'ema_slow': 26,
            },
            'macd': {
                'fast': macd_fast or 12,
                'slow': macd_slow or 26,
                'signal': macd_signal or 9,
            },
            'adx': {
                'period': adx_period or 14,
                'weak': 20,
                'strong': adx_strong or 25,
                'very_strong': adx_very_strong or 40,
            },
            'signal_weights': {
                'rsi_exit_oversold': w_rsi or 2.0,
                'rsi_exit_overbought': w_rsi or 2.0,
                'stoch_bullish_cross': w_stoch or 1.0,
                'stoch_bearish_cross': w_stoch or 1.0,
                'macd_bullish': w_macd or 1.0,
                'macd_bearish': w_macd or 1.0,
                'macd_histogram_positive': w_macd_hist or 0.5,
                'macd_histogram_negative': w_macd_hist or 0.5,
                'rsi_divergence': w_div or 2.0,
                'pattern_bullish': w_pattern or 1.5,
                'pattern_bearish': w_pattern or 1.5,
                'trend_bonus': w_trend or 1.0,
            },
            'decision': {
                'min_conviction_threshold': dec_threshold or 2.5,
                'conviction_difference': dec_diff or 0.5,
                'against_trend_penalty': dec_penalty or 0.5,
                'adx_confirmation_level': dec_adx_level or 30,
                'adx_confirmation_bonus': dec_adx_bonus or 1.2,
                'max_conviction': 5,
            },
            'trend': current_config.get('trend', get_default_config()['trend']),
            'divergence': {
                'lookback_period': div_lookback or 14,
                'rsi_low_threshold': div_rsi_low or 40,
                'rsi_high_threshold': div_rsi_high or 60,
            },
            'optional_filters': current_config.get('optional_filters', get_default_config()['optional_filters']),
        }
        
        summary = f"✅ Config | ⏱️ {config['signal_timeframe']}j | Seuil: {config['decision']['min_conviction_threshold']} | RSI: {config['rsi']['oversold']}-{config['rsi']['overbought']}"
        
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