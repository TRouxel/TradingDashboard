# layouts/config_modal.py
"""
Modal de configuration des paramètres.
VERSION 2.2 - CORRECTION des limites min pour permettre 0 et valeurs décimales basses
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from config import SIGNAL_TIMEFRAME, TRADING_PROFILES, get_default_config


def create_config_modal():
    """Crée le modal de configuration des paramètres."""
    default_config = get_default_config()
    comb_weights = default_config.get('combination_weights', {})
    
    # Créer les options pour le sélecteur de profil
    profile_options = [
        {'label': f"{profile['name']} - {profile['description']}", 'value': key}
        for key, profile in TRADING_PROFILES.items()
    ]
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("⚙️ Configuration des Paramètres"), close_button=True),
        dbc.ModalBody([
            dbc.Accordion([
                # === PROFIL DE TRADING ===
                dbc.AccordionItem([
                    html.P("Sélectionnez un profil prédéfini qui ajuste automatiquement tous les paramètres.", className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Profil de Trading :"),
                            dcc.Dropdown(
                                id='config-trading-profile',
                                options=profile_options,
                                value='balanced',
                                clearable=False
                            ),
                        ], width=12),
                    ]),
                    html.Hr(),
                    html.Div(id='profile-description', className="mt-2"),
                    html.Div([
                        html.H6("Caractéristiques du profil sélectionné :", className="mt-3"),
                        html.Div(id='profile-details', className="small text-muted")
                    ]),
                ], title="🎯 Profil de Trading", className="bg-primary"),
                
                # === GESTION DES ACTIFS ===
                dbc.AccordionItem([
                    html.P("Ajoutez ou supprimez des actifs à suivre (symboles Yahoo Finance).", className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.InputGroup([
                                dbc.Input(id='new-asset-input', placeholder='Ex: NVDA, AMZN, GC=F...', type='text'),
                                dbc.Button("➕ Ajouter", id='add-asset-btn', color='success', size='sm'),
                            ]),
                        ], width=6),
                        dbc.Col([
                            dbc.InputGroup([
                                dcc.Dropdown(id='remove-asset-dropdown', placeholder='Sélectionner...', style={'minWidth': '150px'}),
                                dbc.Button("🗑️ Supprimer", id='remove-asset-btn', color='danger', size='sm'),
                            ]),
                        ], width=6),
                    ]),
                    html.Div(id='asset-management-status', className='mt-2'),
                    html.Hr(),
                    html.Label("Actifs actuellement suivis :", className="mt-2"),
                    html.Div(id='current-assets-list', className="mt-1"),
                ], title="📋 Gestion des Actifs"),
                
                # === ÉCHELLE DE TEMPS ===
                dbc.AccordionItem([
                    html.P("Définit sur combien de jours les signaux sont analysés.", className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Fenêtre d'analyse des signaux :"),
                            dcc.Dropdown(
                                id='config-signal-timeframe',
                                options=SIGNAL_TIMEFRAME['options'],
                                value=default_config['signal_timeframe'],
                                clearable=False
                            ),
                        ], width=6),
                    ]),
                ], title="📅 Échelle de Temps"),
                
                # === TOUTES LES COMBINAISONS D'ACHAT ===
                dbc.AccordionItem([
                    html.P([
                        "Les combinaisons d'indicateurs sont plus fiables que les indicateurs seuls. ",
                        html.Strong("Mettez à 0 pour désactiver une combinaison.")
                    ], className="text-muted mb-3"),
                    
                    # Ligne 1 - Très haute fiabilité
                    html.H6("🏆 Très Haute Fiabilité", className="text-success mt-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Divergence Haussière + Stoch :", className="small"),
                            dbc.Input(id='config-comb-divergence-bullish-stoch', type='number', 
                                     value=comb_weights.get('divergence_bullish_stoch', 3.0), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Triple Confirm Achat :", className="small"),
                            dbc.Input(id='config-comb-triple-confirm-buy', type='number', 
                                     value=comb_weights.get('triple_confirm_buy', 2.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Cross + RSI Bas :", className="small"),
                            dbc.Input(id='config-comb-macd-cross-rsi-low', type='number', 
                                     value=comb_weights.get('macd_cross_rsi_low', 2.5), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    
                    # Ligne 2 - Haute fiabilité
                    html.H6("⭐ Haute Fiabilité", className="text-primary mt-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Bollinger Basse + RSI Bas :", className="small"),
                            dbc.Input(id='config-comb-bollinger-low-rsi-low', type='number', 
                                     value=comb_weights.get('bollinger_low_rsi_low', 2.3), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("RSI Bas + Stoch Haussier :", className="small"),
                            dbc.Input(id='config-comb-rsi-low-stoch-bullish', type='number', 
                                     value=comb_weights.get('rsi_low_stoch_bullish', 2.2), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern Haussier + RSI Bas :", className="small"),
                            dbc.Input(id='config-comb-pattern-bullish-rsi-low', type='number', 
                                     value=comb_weights.get('pattern_bullish_rsi_low', 2.2), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Bollinger Basse + Stoch :", className="small"),
                            dbc.Input(id='config-comb-bollinger-low-stoch-bullish', type='number', 
                                     value=comb_weights.get('bollinger_low_stoch_bullish', 2.0), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    
                    # Ligne 3 - Fiabilité moyenne
                    html.H6("📊 Fiabilité Moyenne", className="text-warning mt-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("ADX Fort + DI+ :", className="small"),
                            dbc.Input(id='config-comb-adx-strong-di-plus', type='number', 
                                     value=comb_weights.get('adx_strong_di_plus', 1.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Haussier + Trend :", className="small"),
                            dbc.Input(id='config-comb-macd-bullish-trend-bullish', type='number', 
                                     value=comb_weights.get('macd_bullish_trend_bullish', 1.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Positif + Trend :", className="small"),
                            dbc.Input(id='config-comb-macd-positive-trend-bullish', type='number', 
                                     value=comb_weights.get('macd_positive_trend_bullish', 1.7), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern + Trend Haussier :", className="small"),
                            dbc.Input(id='config-comb-pattern-bullish-trend-bullish', type='number', 
                                     value=comb_weights.get('pattern_bullish_trend_bullish', 1.6), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Stoch Cross + RSI Bas :", className="small"),
                            dbc.Input(id='config-comb-stoch-cross-bullish-rsi-low', type='number', 
                                     value=comb_weights.get('stoch_cross_bullish_rsi_low', 1.6), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("RSI Sortie Survente + Stoch :", className="small"),
                            dbc.Input(id='config-comb-rsi-exit-oversold-stoch', type='number', 
                                     value=comb_weights.get('rsi_exit_oversold_stoch', 1.5), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                ], title="🟢 Combinaisons d'ACHAT (13)"),
                
                # === TOUTES LES COMBINAISONS DE VENTE ===
                dbc.AccordionItem([
                    html.P([
                        "Les combinaisons de vente fonctionnent de manière symétrique aux combinaisons d'achat. ",
                        html.Strong("Mettez à 0 pour désactiver une combinaison.")
                    ], className="text-muted mb-3"),
                    
                    # Ligne 1 - Très haute fiabilité
                    html.H6("🏆 Très Haute Fiabilité", className="text-danger mt-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Divergence Baissière + Stoch :", className="small"),
                            dbc.Input(id='config-comb-divergence-bearish-stoch', type='number', 
                                     value=comb_weights.get('divergence_bearish_stoch', 3.0), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Triple Confirm Vente :", className="small"),
                            dbc.Input(id='config-comb-triple-confirm-sell', type='number', 
                                     value=comb_weights.get('triple_confirm_sell', 2.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Cross Baissier + RSI :", className="small"),
                            dbc.Input(id='config-comb-macd-cross-bearish-rsi-high', type='number', 
                                     value=comb_weights.get('macd_cross_bearish_rsi_high', 2.5), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    
                    # Ligne 2 - Haute fiabilité
                    html.H6("⭐ Haute Fiabilité", className="text-warning mt-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Bollinger Haute + RSI Haut :", className="small"),
                            dbc.Input(id='config-comb-bollinger-high-rsi-high', type='number', 
                                     value=comb_weights.get('bollinger_high_rsi_high', 2.3), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("RSI Haut + Stoch Baissier :", className="small"),
                            dbc.Input(id='config-comb-rsi-high-stoch-bearish', type='number', 
                                     value=comb_weights.get('rsi_high_stoch_bearish', 2.2), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern Baissier + RSI Haut :", className="small"),
                            dbc.Input(id='config-comb-pattern-bearish-rsi-high', type='number', 
                                     value=comb_weights.get('pattern_bearish_rsi_high', 2.2), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Bollinger Haute + Stoch :", className="small"),
                            dbc.Input(id='config-comb-bollinger-high-stoch-bearish', type='number', 
                                     value=comb_weights.get('bollinger_high_stoch_bearish', 2.0), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    
                    # Ligne 3 - Fiabilité moyenne
                    html.H6("📊 Fiabilité Moyenne", className="text-secondary mt-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("ADX Fort + DI- :", className="small"),
                            dbc.Input(id='config-comb-adx-strong-di-minus', type='number', 
                                     value=comb_weights.get('adx_strong_di_minus', 1.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Baissier + Trend :", className="small"),
                            dbc.Input(id='config-comb-macd-bearish-trend-bearish', type='number', 
                                     value=comb_weights.get('macd_bearish_trend_bearish', 1.8), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Négatif + Trend :", className="small"),
                            dbc.Input(id='config-comb-macd-negative-trend-bearish', type='number', 
                                     value=comb_weights.get('macd_negative_trend_bearish', 1.7), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern + Trend Baissier :", className="small"),
                            dbc.Input(id='config-comb-pattern-bearish-trend-bearish', type='number', 
                                     value=comb_weights.get('pattern_bearish_trend_bearish', 1.6), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Stoch Cross Baissier + RSI :", className="small"),
                            dbc.Input(id='config-comb-stoch-cross-bearish-rsi-high', type='number', 
                                     value=comb_weights.get('stoch_cross_bearish_rsi_high', 1.6), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("RSI Sortie Surachat + Stoch :", className="small"),
                            dbc.Input(id='config-comb-rsi-exit-overbought-stoch', type='number', 
                                     value=comb_weights.get('rsi_exit_overbought_stoch', 1.5), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                        dbc.Col([
                            html.Label("Prix Sous MAs + MACD Neg :", className="small"),
                            dbc.Input(id='config-comb-price-below-mas-macd-negative', type='number', 
                                     value=comb_weights.get('price_below_mas_macd_negative', 1.5), min=0, max=5, step=0.1, size="sm"),
                        ], width=3),
                    ], className="mb-2"),
                ], title="🔴 Combinaisons de VENTE (13)"),
                
                # === INDICATEURS INDIVIDUELS ===
                dbc.AccordionItem([
                    html.P([
                        "Les indicateurs individuels ont un poids réduit car ils sont moins fiables seuls. ",
                        "La Divergence RSI et la Tendance sont les plus fiables."
                    ], className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Divergence RSI :"),
                            dbc.Input(id='config-ind-divergence', type='number', value=2.0, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("Tendance Forte :"),
                            dbc.Input(id='config-ind-trend-strong', type='number', value=1.5, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("Tendance Faible :"),
                            dbc.Input(id='config-ind-trend-weak', type='number', value=0.8, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern :"),
                            dbc.Input(id='config-ind-pattern', type='number', value=0.8, min=0, max=5, step=0.1),
                        ], width=3),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("RSI Extrême :"),
                            dbc.Input(id='config-ind-rsi-extreme', type='number', value=0.8, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("Stoch Cross :"),
                            dbc.Input(id='config-ind-stoch', type='number', value=0.5, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD Cross :"),
                            dbc.Input(id='config-ind-macd', type='number', value=0.6, min=0, max=5, step=0.1),
                        ], width=3),
                        dbc.Col([
                            html.Label("Bollinger :"),
                            dbc.Input(id='config-ind-bollinger', type='number', value=0.5, min=0, max=5, step=0.1),
                        ], width=3),
                    ]),
                ], title="📊 Poids Indicateurs Individuels"),
                
                # === RSI ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période RSI :"),
                            dbc.Input(id='config-rsi-period', type='number', value=default_config['rsi']['period'], min=5, max=50),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seuil Survente :"),
                            dbc.Input(id='config-rsi-oversold', type='number', value=default_config['rsi']['oversold'], min=10, max=40),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seuil Surachat :"),
                            dbc.Input(id='config-rsi-overbought', type='number', value=default_config['rsi']['overbought'], min=60, max=90),
                        ], width=4),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Zone sortie survente (min) :"),
                            dbc.Input(id='config-rsi-exit-oversold-min', type='number', value=default_config['rsi']['exit_oversold_min'], min=20, max=40),
                        ], width=3),
                        dbc.Col([
                            html.Label("Zone sortie survente (max) :"),
                            dbc.Input(id='config-rsi-exit-oversold-max', type='number', value=default_config['rsi']['exit_oversold_max'], min=30, max=50),
                        ], width=3),
                        dbc.Col([
                            html.Label("Zone sortie surachat (min) :"),
                            dbc.Input(id='config-rsi-exit-overbought-min', type='number', value=default_config['rsi']['exit_overbought_min'], min=50, max=70),
                        ], width=3),
                        dbc.Col([
                            html.Label("Zone sortie surachat (max) :"),
                            dbc.Input(id='config-rsi-exit-overbought-max', type='number', value=default_config['rsi']['exit_overbought_max'], min=60, max=80),
                        ], width=3),
                    ]),
                ], title="📊 RSI"),
                
                # === STOCHASTIQUE ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période %K :"),
                            dbc.Input(id='config-stoch-k', type='number', value=default_config['stochastic']['k_period'], min=5, max=30),
                        ], width=3),
                        dbc.Col([
                            html.Label("Période %D :"),
                            dbc.Input(id='config-stoch-d', type='number', value=default_config['stochastic']['d_period'], min=1, max=10),
                        ], width=3),
                        dbc.Col([
                            html.Label("Seuil Survente :"),
                            dbc.Input(id='config-stoch-oversold', type='number', value=default_config['stochastic']['oversold'], min=10, max=30),
                        ], width=3),
                        dbc.Col([
                            html.Label("Seuil Surachat :"),
                            dbc.Input(id='config-stoch-overbought', type='number', value=default_config['stochastic']['overbought'], min=70, max=95),
                        ], width=3),
                    ]),
                ], title="📈 Stochastique"),
                
                # === BANDES DE BOLLINGER ===
                dbc.AccordionItem([
                    html.P("Les bandes de Bollinger mesurent la volatilité et définissent des zones de support/résistance dynamiques.", className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période :"),
                            dbc.Input(id='config-bb-period', type='number', value=default_config['bollinger']['period'], min=5, max=50),
                        ], width=4),
                        dbc.Col([
                            html.Label("Écart-type :"),
                            dbc.Input(id='config-bb-std', type='number', value=default_config['bollinger']['std_dev'], min=1, max=4, step=0.5),
                        ], width=4),
                    ]),
                ], title="📊 Bandes de Bollinger"),
                
                # === MOYENNES MOBILES ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("SMA Court terme :"),
                            dbc.Input(id='config-sma-short', type='number', value=default_config['moving_averages']['sma_short'], min=5, max=50),
                        ], width=4),
                        dbc.Col([
                            html.Label("SMA Moyen terme :"),
                            dbc.Input(id='config-sma-medium', type='number', value=default_config['moving_averages']['sma_medium'], min=20, max=100),
                        ], width=4),
                        dbc.Col([
                            html.Label("SMA Long terme :"),
                            dbc.Input(id='config-sma-long', type='number', value=default_config['moving_averages']['sma_long'], min=100, max=300),
                        ], width=4),
                    ]),
                ], title="📉 Moyennes Mobiles"),
                
                # === MACD ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période Rapide :"),
                            dbc.Input(id='config-macd-fast', type='number', value=default_config['macd']['fast'], min=5, max=20),
                        ], width=4),
                        dbc.Col([
                            html.Label("Période Lente :"),
                            dbc.Input(id='config-macd-slow', type='number', value=default_config['macd']['slow'], min=15, max=40),
                        ], width=4),
                        dbc.Col([
                            html.Label("Période Signal :"),
                            dbc.Input(id='config-macd-signal', type='number', value=default_config['macd']['signal'], min=5, max=15),
                        ], width=4),
                    ]),
                ], title="📊 MACD"),
                
                # === ADX ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période ADX :"),
                            dbc.Input(id='config-adx-period', type='number', value=default_config['adx']['period'], min=7, max=30),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seuil Tendance Forte :"),
                            dbc.Input(id='config-adx-strong', type='number', value=default_config['adx']['strong'], min=15, max=40),
                        ], width=4),
                        dbc.Col([
                            html.Label("Seuil Tendance Très Forte :"),
                            dbc.Input(id='config-adx-very-strong', type='number', value=default_config['adx']['very_strong'], min=30, max=60),
                        ], width=4),
                    ]),
                ], title="💪 ADX (Force de Tendance)"),
                
                # === SEUILS DE DÉCISION - CORRIGÉ ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Seuil Conviction Minimum :"),
                            # CORRECTION: min=0 au lieu de min=1, step=0.1 pour les décimales
                            dbc.Input(id='config-decision-threshold', type='number', 
                                     value=default_config['decision']['min_conviction_threshold'], 
                                     min=0, max=10, step=0.1),
                        ], width=4),
                        dbc.Col([
                            html.Label("Écart Min Achat/Vente :"),
                            # CORRECTION: min=0 pour permettre 0
                            dbc.Input(id='config-decision-difference', type='number', 
                                     value=default_config['decision']['conviction_difference'], 
                                     min=0, max=5, step=0.1),
                        ], width=4),
                        dbc.Col([
                            html.Label("Pénalité Contre-Tendance :"),
                            dbc.Input(id='config-decision-penalty', type='number', 
                                     value=default_config['decision']['against_trend_penalty'], 
                                     min=0, max=1, step=0.1),
                        ], width=4),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Niveau ADX pour Bonus :"),
                            # CORRECTION: min=0 pour permettre 0
                            dbc.Input(id='config-decision-adx-level', type='number', 
                                     value=default_config['decision']['adx_confirmation_level'], 
                                     min=0, max=50, step=1),
                        ], width=4),
                        dbc.Col([
                            html.Label("Multiplicateur Bonus ADX :"),
                            dbc.Input(id='config-decision-adx-bonus', type='number', 
                                     value=default_config['decision']['adx_confirmation_bonus'], 
                                     min=1, max=2, step=0.1),
                        ], width=4),
                        dbc.Col([
                            html.Label("Min. Combos pour Signal :"),
                            # CORRECTION: min=0 pour permettre 0
                            dbc.Input(id='config-decision-min-combos', type='number', 
                                     value=default_config['decision'].get('min_combinations_for_signal', 1), 
                                     min=0, max=5, step=1),
                        ], width=4),
                    ]),
                ], title="🎯 Seuils de Décision"),
                
                # === DIVERGENCES ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Période Lookback :"),
                            dbc.Input(id='config-div-lookback', type='number', value=default_config['divergence']['lookback_period'], min=5, max=30),
                        ], width=4),
                        dbc.Col([
                            html.Label("RSI Seuil Bas :"),
                            dbc.Input(id='config-div-rsi-low', type='number', value=default_config['divergence']['rsi_low_threshold'], min=30, max=50),
                        ], width=4),
                        dbc.Col([
                            html.Label("RSI Seuil Haut :"),
                            dbc.Input(id='config-div-rsi-high', type='number', value=default_config['divergence']['rsi_high_threshold'], min=50, max=70),
                        ], width=4),
                    ]),
                ], title="🔀 Détection des Divergences"),
                
            ], start_collapsed=True, always_open=True),
        ]),
        dbc.ModalFooter([
            dbc.Button("Réinitialiser", id="config-reset-btn", color="warning", className="me-2"),
            dbc.Button("Appliquer", id="config-apply-btn", color="success"),
        ]),
    ], id="config-modal", size="xl", scrollable=True)