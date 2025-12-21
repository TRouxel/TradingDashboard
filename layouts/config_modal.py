# layouts/config_modal.py
"""
Modal de configuration des paramètres.
"""
from dash import dcc, html
import dash_bootstrap_components as dbc

from config import SIGNAL_TIMEFRAME, get_default_config


def create_config_modal():
    """Crée le modal de configuration des paramètres."""
    default_config = get_default_config()
    
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("⚙️ Configuration des Paramètres"), close_button=True),
        dbc.ModalBody([
            dbc.Accordion([
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
                        dbc.Col([
                            html.Label("Poids signal :"),
                            dbc.Input(id='config-weight-bollinger', type='number', value=default_config['signal_weights']['bollinger_lower'], min=0, max=5, step=0.5),
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
                
                # === PONDÉRATIONS DES SIGNAUX ===
                dbc.AccordionItem([
                    html.P("Ajustez le poids de chaque signal dans le calcul de la conviction.", className="text-muted mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("RSI sortie zone :"),
                            dbc.Input(id='config-weight-rsi', type='number', value=default_config['signal_weights']['rsi_exit_oversold'], min=0, max=5, step=0.5),
                        ], width=3),
                        dbc.Col([
                            html.Label("Croisement Stoch :"),
                            dbc.Input(id='config-weight-stoch', type='number', value=default_config['signal_weights']['stoch_bullish_cross'], min=0, max=5, step=0.5),
                        ], width=3),
                        dbc.Col([
                            html.Label("MACD :"),
                            dbc.Input(id='config-weight-macd', type='number', value=default_config['signal_weights']['macd_bullish'], min=0, max=5, step=0.5),
                        ], width=3),
                        dbc.Col([
                            html.Label("Histogramme MACD :"),
                            dbc.Input(id='config-weight-macd-hist', type='number', value=default_config['signal_weights']['macd_histogram_positive'], min=0, max=5, step=0.5),
                        ], width=3),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Divergence RSI :"),
                            dbc.Input(id='config-weight-divergence', type='number', value=default_config['signal_weights']['rsi_divergence'], min=0, max=5, step=0.5),
                        ], width=3),
                        dbc.Col([
                            html.Label("Pattern Chandelier :"),
                            dbc.Input(id='config-weight-pattern', type='number', value=default_config['signal_weights']['pattern_bullish'], min=0, max=5, step=0.5),
                        ], width=3),
                        dbc.Col([
                            html.Label("Bonus Tendance :"),
                            dbc.Input(id='config-weight-trend', type='number', value=default_config['signal_weights']['trend_bonus'], min=0, max=5, step=0.5),
                        ], width=3),
                    ]),
                ], title="⚖️ Pondérations des Signaux"),
                
                # === SEUILS DE DÉCISION ===
                dbc.AccordionItem([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Seuil Conviction Minimum :"),
                            dbc.Input(id='config-decision-threshold', type='number', value=default_config['decision']['min_conviction_threshold'], min=1, max=5, step=0.5),
                        ], width=4),
                        dbc.Col([
                            html.Label("Écart Min Achat/Vente :"),
                            dbc.Input(id='config-decision-difference', type='number', value=default_config['decision']['conviction_difference'], min=0, max=2, step=0.1),
                        ], width=4),
                        dbc.Col([
                            html.Label("Pénalité Contre-Tendance :"),
                            dbc.Input(id='config-decision-penalty', type='number', value=default_config['decision']['against_trend_penalty'], min=0, max=1, step=0.1),
                        ], width=4),
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Niveau ADX pour Bonus :"),
                            dbc.Input(id='config-decision-adx-level', type='number', value=default_config['decision']['adx_confirmation_level'], min=20, max=50),
                        ], width=4),
                        dbc.Col([
                            html.Label("Multiplicateur Bonus ADX :"),
                            dbc.Input(id='config-decision-adx-bonus', type='number', value=default_config['decision']['adx_confirmation_bonus'], min=1, max=2, step=0.1),
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