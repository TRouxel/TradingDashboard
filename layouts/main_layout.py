# layouts/main_layout.py
"""
Layout principal de l'application.
"""
from datetime import date
from dash import dcc, html
import dash_bootstrap_components as dbc

from config import SIGNAL_TIMEFRAME, INDICATOR_DESCRIPTIONS, load_user_assets, get_default_config
from .config_modal import create_config_modal
from components.summary_table import create_summary_section


def get_display_options():
    """Retourne les options d'affichage avec descriptions."""
    return [
        {'label': f" Prix", 'value': 'price', 'title': INDICATOR_DESCRIPTIONS['price']},
        {'label': f" MAs", 'value': 'moving_averages', 'title': INDICATOR_DESCRIPTIONS['moving_averages']},
        {'label': f" Bollinger", 'value': 'bollinger', 'title': INDICATOR_DESCRIPTIONS['bollinger']},
        {'label': f" Recos", 'value': 'recommendations', 'title': INDICATOR_DESCRIPTIONS['recommendations']},
        {'label': f" Tendance", 'value': 'trend', 'title': INDICATOR_DESCRIPTIONS['trend']},
        {'label': f" MACD", 'value': 'macd', 'title': INDICATOR_DESCRIPTIONS['macd']},
        {'label': f" Volume", 'value': 'volume', 'title': INDICATOR_DESCRIPTIONS['volume']},
        {'label': f" RSI", 'value': 'rsi', 'title': INDICATOR_DESCRIPTIONS['rsi']},
        {'label': f" Stoch", 'value': 'stochastic', 'title': INDICATOR_DESCRIPTIONS['stochastic']},
        {'label': f" Patterns", 'value': 'patterns', 'title': INDICATOR_DESCRIPTIONS['patterns']},
    ]


def create_main_layout():
    """Crée le layout principal de l'application."""
    default_config = get_default_config()
    
    return dbc.Container([
        # Stores
        dcc.Store(id='config-store', data=default_config),
        dcc.Store(id='assets-store', data=load_user_assets()),
        dcc.Store(id='fundamental-store', data={}),
        dcc.Store(id='technical-data-store', data={}),
        dcc.Store(id='full-data-store', data={}),
        dcc.Store(id='zoom-range-store', data=None),
        dcc.Store(id='performance-store', data={}),
        dcc.Store(id='summary-store', data={}),
        
        # Modal de configuration
        create_config_modal(),
        
        # Titre
        html.H1("Dashboard d'Analyse Technique & Fondamentale", className="text-center my-3"),

        # Ligne de contrôles principaux
        dbc.Row([
            dbc.Col([
                html.Label("Actif :"),
                dcc.Dropdown(id='asset-dropdown', clearable=False)
            ], width=2),
            dbc.Col([
                html.Label("Date :"),
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=date(2015, 1, 1),
                    max_date_allowed=date.today(),
                    initial_visible_month=date.today(),
                    date=date.today(),
                    display_format='DD/MM/YYYY'
                )
            ], width=2),
            dbc.Col([
                html.Label("Période :"),
                dcc.Dropdown(
                    id='period-dropdown',
                    options=[
                        {'label': '3 Mois', 'value': '3mo'},
                        {'label': '6 Mois', 'value': '6mo'},
                        {'label': '1 An', 'value': '1y'},
                        {'label': '2 Ans', 'value': '2y'},
                        {'label': '5 Ans', 'value': '5y'},
                        {'label': '10 Ans', 'value': '10y'},
                        {'label': '15 Ans', 'value': '15y'},
                        {'label': '20 Ans', 'value': '20y'},
                        {'label': '25 Ans', 'value': '25y'},
                        {'label': 'Maximum', 'value': 'max'},
                    ],
                    value='2y',
                    clearable=False
                )
            ], width=1),
            dbc.Col([
                html.Label("Signaux :"),
                dcc.Dropdown(
                    id='signal-timeframe-quick',
                    options=SIGNAL_TIMEFRAME['options'],
                    value=1,
                    clearable=False
                )
            ], width=2),
            dbc.Col([
                html.Label("Afficher :"),
                dcc.Checklist(
                    id='display-options',
                    options=get_display_options(),
                    value=['price', 'moving_averages', 'bollinger', 'recommendations', 'trend', 'macd', 'volume', 'rsi', 'stochastic', 'patterns'],
                    inline=True,
                    className="mt-1",
                    inputStyle={"marginRight": "3px", "marginLeft": "8px"}
                )
            ], width=3),
            dbc.Col([
                html.Br(),
                dbc.ButtonGroup([
                    dbc.Button("⚙️ Config", id="open-config-btn", color="secondary", size="sm"),
                    dbc.Button("🔄 Reset Zoom", id='reset-zoom-btn', n_clicks=0, color="info", size="sm"),
                    dbc.Button("💾 Sauver", id='save-button', n_clicks=0, color="primary", size="sm"),
                ], className="mt-1")
            ], width=2)
        ], className="mb-2"),
        
        # Info zoom actif
        dbc.Row([
            dbc.Col([
                html.Div(id='zoom-info', className="text-info small")
            ], width=6),
            dbc.Col([
                html.Div(id='config-summary', className="text-muted small text-end")
            ], width=6),
        ], className="mb-2"),
        
        html.Div(id='save-status', className="text-center mb-1"),

        # === 0. TABLEAU RÉCAPITULATIF DES ACTIFS (NOUVEAU) ===
        create_summary_section(),

        # === 1. SYNTHÈSE TECHNIQUE (COLLAPSIBLE) ===
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            id="collapse-technical-summary-btn",
                            color="link",
                            className="text-white text-decoration-none p-0",
                            children=[
                                html.H5("📊 Analyse Technique", className="mb-0 d-inline me-2"),
                            ]
                        ),
                    ], width="auto"),
                    dbc.Col([
                        html.Div(id='technical-summary-header', className="d-flex align-items-center")
                    ]),
                ], align="center", className="g-0"),
            ]),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Loading(
                        html.Div(id='technical-indicators-table'),
                        type="circle"
                    )
                ], className="p-2"),
                id="collapse-technical-summary",
                is_open=False,
            ),
        ], className="mb-3", color="dark", outline=True),

        # === 2. SYNTHÈSE FONDAMENTALE (COLLAPSIBLE) ===
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            id="collapse-fundamental-summary-btn",
                            color="link",
                            className="text-white text-decoration-none p-0",
                            children=[
                                html.H5("💰 Analyse Fondamentale", className="mb-0 d-inline me-2"),
                            ]
                        ),
                    ], width="auto"),
                    dbc.Col([
                        html.Div(id='fundamental-summary-header', className="d-flex align-items-center")
                    ]),
                ], align="center", className="g-0"),
            ]),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Loading(
                        html.Div(id='fundamental-details-container'),
                        type="circle"
                    )
                ], className="p-2"),
                id="collapse-fundamental-summary",
                is_open=False,
            ),
        ], className="mb-3", color="dark", outline=True),

        # === 3. BACKTESTING DES INDICATEURS (COLLAPSIBLE) ===
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            id="collapse-performance-btn",
                            color="link",
                            className="text-white text-decoration-none p-0",
                            children=[
                                html.H5("📈 Backtesting des Indicateurs", className="mb-0 d-inline me-2"),
                            ]
                        ),
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button("🔍 Analyser", id="analyze-performance-btn", color="info", size="sm", className="me-3"),
                        html.Span("Horizons: ", className="text-muted small me-1"),
                        dcc.Checklist(
                            id='performance-horizon-filter',
                            options=[
                                {'label': ' 1j', 'value': 1},
                                {'label': ' 2j', 'value': 2},
                                {'label': ' 5j', 'value': 5},
                                {'label': ' 10j', 'value': 10},
                                {'label': ' 20j', 'value': 20},
                            ],
                            value=[1, 2, 5, 10, 20],
                            inline=True,
                            inputStyle={"marginRight": "3px", "marginLeft": "8px"},
                            className="d-inline",
                            labelStyle={"fontSize": "12px"}
                        ),
                    ], className="d-flex align-items-center"),
                ], align="center", className="g-0"),
            ]),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Loading(
                        html.Div(id='performance-content', children=[
                            html.P([
                                "Cliquez sur ",
                                html.Strong("'Analyser'"),
                                " pour évaluer la performance historique de chaque indicateur. ",
                                "Cela compare les signaux passés avec l'évolution réelle des prix."
                            ], className="text-muted")
                        ]),
                        type="circle"
                    )
                ], className="p-2"),
                id="collapse-performance",
                is_open=False,
            ),
        ], className="mb-3", color="dark", outline=True),

        # === 4. SIMULATIONS DE TRADING (COLLAPSIBLE) ===
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            id="collapse-strategy-btn",
                            color="link",
                            className="text-white text-decoration-none p-0",
                            children=[
                                html.H5("🎯 Simulations de Trading", className="mb-0 d-inline me-2"),
                            ]
                        ),
                    ], width="auto"),
                    dbc.Col([
                        dbc.Button("🚀 Simuler", id="analyze-strategy-btn", color="success", size="sm", className="me-3"),
                        html.Span([
                            html.Small("Stratégies basées sur la ", className="text-muted"),
                            html.Small("divergence RSI", className="text-info fw-bold"),
                        ]),
                    ], className="d-flex align-items-center"),
                ], align="center", className="g-0"),
            ]),
            dbc.Collapse(
                dbc.CardBody([
                    dcc.Loading(
                        html.Div(id='strategy-content', children=[
                            html.P([
                                "Cliquez sur ",
                                html.Strong("'Simuler'"),
                                " pour exécuter deux stratégies de trading basées sur la divergence RSI:",
                            ], className="text-muted mb-2"),
                            html.Ul([
                                html.Li([
                                    html.Strong("Hold & Sell: "),
                                    "Achat initial, vente sur divergence baissière, rachat après N jours. ",
                                    html.Em("Pour actifs long terme (ETF, blue chips).")
                                ], className="text-muted small"),
                                html.Li([
                                    html.Strong("Buy on Divergence: "),
                                    "Achat uniquement sur divergence haussière, vente après N jours. ",
                                    html.Em("Pour actifs plus spéculatifs.")
                                ], className="text-muted small"),
                            ]),
                            html.P([
                                "Le ",
                                html.Strong("spread"),
                                " (coût de transaction) utilise la valeur '",
                                html.Em("Écart Min Achat/Vente"),
                                "' des seuils de décision."
                            ], className="text-muted small"),
                        ]),
                        type="circle"
                    )
                ], className="p-2"),
                id="collapse-strategy",
                is_open=False,
            ),
        ], className="mb-3", color="dark", outline=True),

        # === 5. GRAPHIQUES PRINCIPAUX ===
        html.Div(id='main-charts-container'),

        # === 6. GRAPHIQUES TECHNIQUES DÉTAILLÉS (COLLAPSE) ===
        dbc.Card([
            dbc.CardHeader([
                dbc.Button(
                    "📈 Graphiques Techniques Détaillés",
                    id="collapse-technical-btn",
                    color="link",
                    className="text-white text-decoration-none p-0",
                ),
            ], className="bg-secondary"),
            dbc.Collapse(
                dbc.CardBody([
                    html.Div(id='technical-charts-container')
                ], className="p-2"),
                id="collapse-technical",
                is_open=False,
            ),
        ], className="mb-3"),

    ], fluid=True)