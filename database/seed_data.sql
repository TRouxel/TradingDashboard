-- database/seed_data.sql
-- Insertion des catégories et actifs par défaut

-- ============================================================
-- INSERTION DES CATÉGORIES D'ACTIFS
-- ============================================================

INSERT INTO asset_categories (category_key, name, description, icon, color, 
    market_close_time, trading_days, close_time_notes,
    weight_modifiers, combination_modifiers, decision_modifiers, rsi_thresholds)
VALUES

-- CRYPTO EUR - Trading 24/7
('crypto_eur', 'Crypto EUR', 'Cryptomonnaies vs EUR (BTC-EUR, ETH-EUR, SOL-EUR...)', '💶', '#ff9500',
 NULL, 'Mon-Sun', 
 'Trading 24h/24, 7j/7. Yahoo Finance enregistre la clôture à minuit UTC (01h00 heure française en hiver, 02h00 en été).',
 '{"rsi_divergence": 1.5, "trend_strong": 1.6, "trend_weak": 0.8, "pattern_signal": 0.5, "rsi_extreme": 0.5, "macd_cross": 1.2, "macd_histogram": 1.3, "stoch_cross": 1.2, "bollinger_touch": 0.5, "bollinger_zone": 0.4, "adx_direction": 1.4}',
 '{"divergence_bullish_stoch": 1.4, "divergence_bearish_stoch": 1.4, "triple_confirm_buy": 1.2, "triple_confirm_sell": 1.2, "macd_bullish_trend_bullish": 1.4, "macd_bearish_trend_bearish": 1.4}',
 '{"min_conviction_threshold": 3.5, "conviction_difference": 1.0, "against_trend_penalty": 0.2, "adx_confirmation_bonus": 1.5}',
 '{"oversold": 20, "overbought": 80}'),

-- CRYPTO USD - Trading 24/7
('crypto', 'Crypto USD', 'Cryptomonnaies vs USD (BTC-USD, ETH-USD, SOL-USD...)', '₿', '#f7931a',
 NULL, 'Mon-Sun',
 'Trading 24h/24, 7j/7. Yahoo Finance enregistre la clôture à minuit UTC.',
 '{"rsi_divergence": 1.5, "trend_strong": 1.6, "trend_weak": 0.8, "pattern_signal": 0.5, "rsi_extreme": 0.5, "macd_cross": 1.2, "macd_histogram": 1.3, "stoch_cross": 1.2, "bollinger_touch": 0.5, "bollinger_zone": 0.4, "adx_direction": 1.4}',
 '{"divergence_bullish_stoch": 1.4, "divergence_bearish_stoch": 1.4, "triple_confirm_buy": 1.2, "triple_confirm_sell": 1.2, "macd_bullish_trend_bullish": 1.4, "macd_bearish_trend_bearish": 1.4}',
 '{"min_conviction_threshold": 3.5, "conviction_difference": 1.0, "against_trend_penalty": 0.2, "adx_confirmation_bonus": 1.5}',
 '{"oversold": 20, "overbought": 80}'),

-- FOREX EUR - Trading quasi 24h
('forex_eur', 'Forex vs EUR', 'Devises vs EUR pour portefeuille EUR (USD, AUD, GBP...)', '💱🇪🇺', '#17a2b8',
 '23:00', 'Mon-Fri',
 'Forex trading du dimanche 23h au vendredi 23h (heure française). Clôture quotidienne à 23h00 heure française (22h00 UTC). Attention: pas de cotation le week-end.',
 '{"rsi_divergence": 1.4, "trend_strong": 1.2, "trend_weak": 1.0, "pattern_signal": 1.2, "rsi_extreme": 1.1, "stoch_cross": 1.4, "stoch_extreme": 1.2, "macd_cross": 1.1, "bollinger_touch": 1.5, "bollinger_zone": 1.3}',
 '{"bollinger_low_rsi_low": 1.4, "bollinger_high_rsi_high": 1.4, "bollinger_low_stoch_bullish": 1.4, "bollinger_high_stoch_bearish": 1.4, "rsi_low_stoch_bullish": 1.3, "rsi_high_stoch_bearish": 1.3}',
 '{"min_conviction_threshold": 2.0, "conviction_difference": 0.4, "against_trend_penalty": 0.5}',
 '{"oversold": 30, "overbought": 70}'),

-- BLUE CHIPS US
('blue_chip_us', 'Blue Chip US', 'Actions US stables (Apple, Microsoft, Coca-Cola, J&J...)', '🇺🇸', '#0d6efd',
 '22:00', 'Mon-Fri',
 'NYSE/NASDAQ: Ouverture 15h30, Clôture 22h00 heure française. After-hours jusqu''à 02h00.',
 '{"rsi_divergence": 1.3, "trend_strong": 1.4, "trend_weak": 1.2, "pattern_signal": 1.1, "rsi_extreme": 1.0, "macd_cross": 1.1, "bollinger_touch": 1.2}',
 '{"divergence_bullish_stoch": 1.2, "divergence_bearish_stoch": 1.2, "macd_bullish_trend_bullish": 1.3, "macd_bearish_trend_bearish": 1.3}',
 '{"min_conviction_threshold": 2.5, "conviction_difference": 0.5, "against_trend_penalty": 0.6}',
 '{"oversold": 30, "overbought": 70}'),

-- TECH VOLATILE US
('tech_volatile_us', 'Tech Volatile US', 'Tech US à forte volatilité (Tesla, NVIDIA, AMD, Amazon, Meta...)', '⚡🇺🇸', '#6f42c1',
 '22:00', 'Mon-Fri',
 'NYSE/NASDAQ: Ouverture 15h30, Clôture 22h00 heure française. Volatilité élevée, attention aux gaps.',
 '{"rsi_divergence": 0.8, "trend_strong": 1.5, "trend_weak": 1.0, "pattern_signal": 0.7, "rsi_extreme": 0.6, "macd_cross": 1.3, "macd_histogram": 1.4, "bollinger_touch": 0.6, "adx_direction": 1.5}',
 '{"triple_confirm_buy": 1.3, "triple_confirm_sell": 1.3, "adx_strong_di_plus": 1.4, "adx_strong_di_minus": 1.4, "macd_positive_trend_bullish": 1.3, "macd_negative_trend_bearish": 1.3}',
 '{"min_conviction_threshold": 3.0, "conviction_difference": 0.8, "against_trend_penalty": 0.3, "adx_confirmation_bonus": 1.4}',
 '{"oversold": 25, "overbought": 75}'),

-- BLUE CHIPS EUR
('blue_chip_eur', 'Blue Chip EUR', 'Actions européennes stables (LVMH, Air Liquide, SAP...)', '🇪🇺', '#003399',
 '17:30', 'Mon-Fri',
 'Euronext Paris: 09h00-17h30. Xetra (Allemagne): 09h00-17:30. Amsterdam: 09h00-17:30. Heure française.',
 '{"rsi_divergence": 1.3, "trend_strong": 1.4, "trend_weak": 1.2, "pattern_signal": 1.1, "rsi_extreme": 1.0, "macd_cross": 1.1, "bollinger_touch": 1.2}',
 '{"divergence_bullish_stoch": 1.2, "divergence_bearish_stoch": 1.2, "macd_bullish_trend_bullish": 1.3, "macd_bearish_trend_bearish": 1.3}',
 '{"min_conviction_threshold": 2.5, "conviction_difference": 0.5, "against_trend_penalty": 0.6}',
 '{"oversold": 30, "overbought": 70}'),

-- INDICES
('indices', 'Indices', 'Indices boursiers (S&P 500, NASDAQ, DAX, CAC 40...)', '📊', '#198754',
 NULL, 'Mon-Fri',
 'Varie selon l''indice. US: 22h00 heure FR. Europe: 17h30 heure FR. Asie: matin heure FR.',
 '{"rsi_divergence": 1.5, "trend_strong": 1.4, "trend_weak": 1.2, "pattern_signal": 1.1, "rsi_extreme": 1.2, "rsi_exit_zone": 1.2, "macd_cross": 1.2, "bollinger_touch": 1.3, "bollinger_zone": 1.1}',
 '{"divergence_bullish_stoch": 1.4, "divergence_bearish_stoch": 1.4, "bollinger_low_rsi_low": 1.3, "macd_bullish_trend_bullish": 1.2}',
 '{"min_conviction_threshold": 2.0, "conviction_difference": 0.4, "against_trend_penalty": 0.7}',
 '{"oversold": 30, "overbought": 70}'),

-- MÉTAUX PRÉCIEUX EUR
('precious_metals_eur', 'Métaux Précieux EUR', 'Or, Argent cotés en EUR (4GLD.DE, VZLE.DE...)', '🥇🇪🇺', '#ffc107',
 '17:30', 'Mon-Fri',
 'ETCs cotés sur Xetra: 09h00-17:30 heure française.',
 '{"rsi_divergence": 1.4, "trend_strong": 1.5, "trend_weak": 1.1, "pattern_signal": 1.0, "rsi_extreme": 1.0, "macd_cross": 1.2, "bollinger_touch": 1.1}',
 '{"divergence_bullish_stoch": 1.3, "divergence_bearish_stoch": 1.3, "macd_bullish_trend_bullish": 1.3, "macd_bearish_trend_bearish": 1.3}',
 '{"min_conviction_threshold": 2.5, "conviction_difference": 0.5, "against_trend_penalty": 0.6}',
 '{"oversold": 30, "overbought": 70}'),

-- MÉTAUX PRÉCIEUX USD
('precious_metals', 'Métaux Précieux USD', 'Or, Argent, Platine en USD (GC=F, SI=F, GLD...)', '🥇', '#d4af37',
 '20:30', 'Mon-Fri',
 'COMEX Futures: Trading quasi 24h, clôture officielle à 20h30 heure française. ETFs US: 22h00.',
 '{"rsi_divergence": 1.4, "trend_strong": 1.5, "trend_weak": 1.1, "pattern_signal": 1.0, "rsi_extreme": 1.0, "macd_cross": 1.2, "bollinger_touch": 1.1}',
 '{"divergence_bullish_stoch": 1.3, "divergence_bearish_stoch": 1.3, "macd_bullish_trend_bullish": 1.3, "macd_bearish_trend_bearish": 1.3}',
 '{"min_conviction_threshold": 2.5, "conviction_difference": 0.5, "against_trend_penalty": 0.6}',
 '{"oversold": 30, "overbought": 70}'),

-- ETF SECTORIELS
('etf_sector', 'ETF Sectoriels', 'ETF sectoriels et thématiques', '📦', '#6c757d',
 '22:00', 'Mon-Fri',
 'ETFs US: NYSE/NASDAQ 22h00 heure française. ETFs européens: 17h30.',
 '{"rsi_divergence": 1.3, "trend_strong": 1.3, "trend_weak": 1.1, "pattern_signal": 1.0, "rsi_extreme": 1.0, "macd_cross": 1.1, "bollinger_touch": 1.1}',
 '{"divergence_bullish_stoch": 1.2, "divergence_bearish_stoch": 1.2}',
 '{"min_conviction_threshold": 2.5, "conviction_difference": 0.5, "against_trend_penalty": 0.5}',
 '{"oversold": 30, "overbought": 70}'),

-- MATIÈRES PREMIÈRES
('commodities', 'Matières Premières', 'Pétrole, Gaz, Blé, etc.', '🛢️', '#dc3545',
 '20:30', 'Mon-Fri',
 'NYMEX/CME Futures: Trading quasi 24h, clôtures officielles variables. Pétrole WTI: 20h30 heure FR.',
 '{"rsi_divergence": 1.0, "trend_strong": 1.4, "trend_weak": 0.9, "pattern_signal": 0.8, "rsi_extreme": 0.7, "macd_cross": 1.2, "macd_histogram": 1.3, "adx_direction": 1.4, "bollinger_touch": 0.7}',
 '{"adx_strong_di_plus": 1.4, "adx_strong_di_minus": 1.4, "triple_confirm_buy": 1.2, "triple_confirm_sell": 1.2}',
 '{"min_conviction_threshold": 3.0, "conviction_difference": 0.7, "against_trend_penalty": 0.3, "adx_confirmation_bonus": 1.4}',
 '{"oversold": 25, "overbought": 75}'),

-- CUSTOM/PAR DÉFAUT
('custom', 'Personnalisé', 'Catégorie par défaut - poids standards', '⚙️', '#adb5bd',
 NULL, 'Mon-Fri',
 'Catégorie par défaut pour les actifs non classifiés. Horaires à définir selon l''actif.',
 '{}', '{}', '{}',
 '{"oversold": 30, "overbought": 70}')

ON CONFLICT (category_key) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    color = EXCLUDED.color,
    market_close_time = EXCLUDED.market_close_time,
    trading_days = EXCLUDED.trading_days,
    close_time_notes = EXCLUDED.close_time_notes,
    weight_modifiers = EXCLUDED.weight_modifiers,
    combination_modifiers = EXCLUDED.combination_modifiers,
    decision_modifiers = EXCLUDED.decision_modifiers,
    rsi_thresholds = EXCLUDED.rsi_thresholds;