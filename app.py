# app.py
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback, ALL, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import pandas as pd
import numpy as np
import yfinance as yf

from data_handler import fetch_and_prepare_data, save_indicators_to_db
from config import (
    get_default_config, SIGNAL_TIMEFRAME, INDICATOR_DESCRIPTIONS,
    load_user_assets, save_user_assets, add_asset, remove_asset
)
from fundamental_analyzer import (
    get_fundamental_data, calculate_fundamental_score, 
    format_large_number, format_ratio, get_ratio_color,
    FUNDAMENTAL_THRESHOLDS
)

# app.py
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback, ALL, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import pandas as pd
import numpy as np
import yfinance as yf

# === INITIALISATION DE LA BASE DE DONNÉES ===
try:
    from db_manager import init_database, check_database_connection
    db_ok, db_msg = check_database_connection()
    if db_ok:
        print("✅ Connexion à PostgreSQL établie")
        init_database()
    else:
        print(f"⚠️ Impossible de se connecter à PostgreSQL: {db_msg}")
except Exception as e:
    print(f"⚠️ Erreur d'initialisation DB: {e}")

from data_handler import fetch_and_prepare_data, save_indicators_to_db
from config import (
    get_default_config, SIGNAL_TIMEFRAME, INDICATOR_DESCRIPTIONS,
    load_user_assets, save_user_assets, add_asset, remove_asset
)
from fundamental_analyzer import (
    get_fundamental_data, calculate_fundamental_score, 
    format_large_number, format_ratio, get_ratio_color,
    FUNDAMENTAL_THRESHOLDS
)

# ... reste du code inchangé ...


# --- Initialisation de l'application Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

# --- Store pour la configuration ---
default_config = get_default_config()


# === DESCRIPTIONS DES INDICATEURS POUR LE TABLEAU ===
INDICATOR_DETAILS = {
    'rsi': {
        'name': 'RSI (Relative Strength Index)',
        'interpretation': 'Mesure la vitesse et l\'amplitude des mouvements de prix. <30 = survente (achat potentiel), >70 = surachat (vente potentielle).',
        'weight_key': 'rsi_exit_oversold'
    },
    'stochastic': {
        'name': 'Stochastique (%K/%D)',
        'interpretation': 'Compare le prix de clôture à sa plage de prix. Croisement %K > %D en zone basse = signal achat.',
        'weight_key': 'stoch_bullish_cross'
    },
    'macd': {
        'name': 'MACD',
        'interpretation': 'Différence entre 2 moyennes mobiles. Croisement au-dessus du signal = momentum haussier.',
        'weight_key': 'macd_bullish'
    },
    'macd_histogram': {
        'name': 'Histogramme MACD',
        'interpretation': 'Visualise la force du momentum. Barres vertes croissantes = momentum haussier qui s\'accélère.',
        'weight_key': 'macd_histogram_positive'
    },
    'trend': {
        'name': 'Tendance (MAs + ADX)',
        'interpretation': 'Alignement des moyennes mobiles et force via ADX. Prix > SMA20 > SMA50 > SMA200 = tendance haussière forte.',
        'weight_key': 'trend_bonus'
    },
    'divergence': {
        'name': 'Divergence RSI',
        'interpretation': 'Prix fait nouveau bas mais RSI fait un bas plus haut = divergence haussière (retournement potentiel).',
        'weight_key': 'rsi_divergence'
    },
    'pattern': {
        'name': 'Pattern Chandelier',
        'interpretation': 'Figures de chandeliers japonais. Ex: Engulfing haussier, Doji, Hammer signalent des retournements.',
        'weight_key': 'pattern_bullish'
    },
    'adx': {
        'name': 'ADX (Force de Tendance)',
        'interpretation': 'Mesure la force de la tendance (pas la direction). >25 = tendance forte, >40 = très forte.',
        'weight_key': None
    },
}

# === DESCRIPTIONS DÉTAILLÉES DES RATIOS FONDAMENTAUX ===
FUNDAMENTAL_DESCRIPTIONS = {
    # Valorisation
    'pe_ratio': "Le P/E (Price-to-Earnings) compare le prix de l'action au bénéfice par action. Un P/E de 15 signifie que vous payez 15€ pour chaque 1€ de bénéfice annuel. Un P/E bas peut indiquer une action sous-évaluée, mais peut aussi refléter des problèmes. À comparer avec le secteur.",
    'forward_pe': "P/E calculé avec les bénéfices PRÉVUS des 12 prochains mois (estimations analystes). Plus pertinent que le P/E trailing car il anticipe la croissance future. Un forward P/E < trailing P/E suggère une croissance attendue.",
    'peg_ratio': "PEG = P/E divisé par le taux de croissance des bénéfices. Permet de comparer des entreprises à croissance différente. PEG < 1 = potentiellement sous-évalué compte tenu de la croissance. PEG > 2 = potentiellement surévalué.",
    'pb_ratio': "P/B (Price-to-Book) compare le prix de marché à la valeur comptable (actifs - dettes). P/B < 1 signifie que l'action cote sous sa valeur comptable. Utile pour les secteurs à actifs tangibles (banques, industrie).",
    'ps_ratio': "P/S (Price-to-Sales) compare la capitalisation au chiffre d'affaires. Utile pour les entreprises non rentables ou en forte croissance. Moins manipulable que le bénéfice. P/S < 1 est généralement attractif.",
    'ev_ebitda': "EV/EBITDA compare la valeur d'entreprise (market cap + dette - cash) à l'EBITDA. Mesure combien d'années d'EBITDA il faudrait pour \"racheter\" l'entreprise. Indépendant de la structure financière.",
    'ev_revenue': "EV/Revenue compare la valeur d'entreprise au CA. Utile pour comparer des entreprises du même secteur avec des marges différentes. Particulièrement utilisé pour les entreprises tech en croissance.",
    
    # Rentabilité
    'roe': "ROE (Return on Equity) = Bénéfice net / Capitaux propres. Mesure combien l'entreprise génère de profit pour chaque euro investi par les actionnaires. ROE > 15% est généralement bon. Attention : un ROE très élevé peut venir d'un endettement excessif.",
    'roa': "ROA (Return on Assets) = Bénéfice net / Total des actifs. Mesure l'efficacité de l'utilisation de TOUS les actifs (pas seulement les capitaux propres). Plus pertinent pour comparer des entreprises avec des niveaux d'endettement différents.",
    'gross_margin': "Marge brute = (CA - Coûts directs) / CA. Représente le pourcentage du CA restant après les coûts de production/achat. Une marge brute élevée indique un pouvoir de pricing ou des coûts maîtrisés.",
    'operating_margin': "Marge opérationnelle = Résultat opérationnel / CA. Inclut tous les coûts d'exploitation (salaires, marketing, R&D...). Mesure la rentabilité du cœur de métier avant intérêts et impôts.",
    'net_margin': "Marge nette = Bénéfice net / CA. Le pourcentage du CA qui se transforme réellement en profit après TOUTES les charges (opérationnelles, financières, fiscales). C'est le \"bottom line\".",
    
    # Santé financière
    'debt_equity': "Dette/Equity = Dette totale / Capitaux propres. Mesure le levier financier. Ratio > 1 signifie plus de dette que de fonds propres. Un ratio élevé augmente le risque mais peut booster le ROE.",
    'current_ratio': "Current Ratio = Actifs court terme / Passifs court terme. Mesure la capacité à payer les dettes à moins d'un an. Ratio > 1 = l'entreprise peut couvrir ses obligations. Ratio > 2 peut indiquer une gestion inefficace du cash.",
    'quick_ratio': "Quick Ratio = (Actifs CT - Stocks) / Passifs CT. Plus conservateur que le Current Ratio car exclut les stocks (moins liquides). Ratio > 1 indique une bonne liquidité immédiate.",
    'interest_coverage': "Couverture des intérêts = EBIT / Charges d'intérêts. Mesure combien de fois l'entreprise peut payer ses intérêts avec son résultat opérationnel. Ratio < 2 est préoccupant.",
    'total_debt': "Montant total de la dette financière (court et long terme). À comparer avec les capitaux propres et la capacité de remboursement (cash flow).",
    'total_cash': "Trésorerie et équivalents de trésorerie. Argent immédiatement disponible. Important pour la flexibilité financière et les opportunités d'investissement.",
    'free_cash_flow': "FCF = Cash flow opérationnel - Investissements (CapEx). C'est l'argent réellement disponible après avoir maintenu/développé l'activité. Peut servir aux dividendes, rachats d'actions, acquisitions ou désendettement.",
    
    # Croissance
    'revenue_growth': "Croissance du chiffre d'affaires par rapport à la même période l'an dernier. Indicateur clé de la dynamique commerciale. Une croissance > 10% est généralement considérée comme forte.",
    'earnings_growth': "Croissance du bénéfice net par rapport à l'an dernier. Peut être volatile. Une croissance des bénéfices supérieure à celle du CA indique une amélioration des marges.",
    'eps_trailing': "EPS (Earnings Per Share) sur les 12 derniers mois. Bénéfice net divisé par le nombre d'actions. Base du calcul du P/E. Suivre son évolution est crucial.",
    'eps_forward': "EPS prévisionnel pour les 12 prochains mois (consensus analystes). Si EPS forward > EPS trailing, les analystes anticipent une croissance des bénéfices.",
    
    # Dividendes
    'dividend_yield': "Rendement du dividende = Dividende annuel / Prix de l'action. Représente le revenu passif en pourcentage. Un yield > 5% peut être attractif mais aussi signaler un prix déprimé ou un dividende non soutenable.",
    'dividend_rate': "Montant en dollars/euros du dividende versé par action sur une année. À multiplier par le nombre d'actions détenues pour connaître le revenu total.",
    'payout_ratio': "Payout = Dividendes versés / Bénéfice net. Pourcentage des bénéfices distribués. Ratio > 80% peut être risqué (peu de marge de sécurité). Ratio < 40% laisse de la place pour la croissance du dividende.",
    'five_year_avg_dividend_yield': "Moyenne du rendement du dividende sur 5 ans. Permet de voir si le yield actuel est historiquement haut (opportunité ?) ou bas.",
}


def create_config_modal():
    """Crée le modal de configuration des paramètres."""
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


def get_display_options():
    """Retourne les options d'affichage avec descriptions."""
    return [
        {'label': f" Prix", 'value': 'price', 'title': INDICATOR_DESCRIPTIONS['price']},
        {'label': f" MAs", 'value': 'moving_averages', 'title': INDICATOR_DESCRIPTIONS['moving_averages']},
        {'label': f" Recos", 'value': 'recommendations', 'title': INDICATOR_DESCRIPTIONS['recommendations']},
        {'label': f" Tendance", 'value': 'trend', 'title': INDICATOR_DESCRIPTIONS['trend']},
        {'label': f" MACD", 'value': 'macd', 'title': INDICATOR_DESCRIPTIONS['macd']},
        {'label': f" Volume", 'value': 'volume', 'title': INDICATOR_DESCRIPTIONS['volume']},
        {'label': f" RSI", 'value': 'rsi', 'title': INDICATOR_DESCRIPTIONS['rsi']},
        {'label': f" Stoch", 'value': 'stochastic', 'title': INDICATOR_DESCRIPTIONS['stochastic']},
        {'label': f" Patterns", 'value': 'patterns', 'title': INDICATOR_DESCRIPTIONS['patterns']},
    ]


# --- Définition de la mise en page ---
app.layout = dbc.Container([
    # Stores
    dcc.Store(id='config-store', data=default_config),
    dcc.Store(id='assets-store', data=load_user_assets()),
    dcc.Store(id='fundamental-store', data={}),
    dcc.Store(id='technical-data-store', data={}),
    
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
                value=['price', 'moving_averages', 'recommendations', 'trend', 'macd', 'volume', 'rsi', 'stochastic', 'patterns'],
                inline=True,
                className="mt-1",
                inputStyle={"marginRight": "3px", "marginLeft": "8px"}
            )
        ], width=3),
        dbc.Col([
            html.Br(),
            dbc.ButtonGroup([
                dbc.Button("⚙️ Config", id="open-config-btn", color="secondary", size="sm"),
                dbc.Button("💾 Sauver", id='save-button', n_clicks=0, color="primary", size="sm"),
            ], className="mt-1")
        ], width=2)
    ], className="mb-2"),
    
    # Résumé config
    dbc.Row([
        dbc.Col([html.Div(id='config-summary', className="text-muted small")])
    ], className="mb-2"),
    
    html.Div(id='save-status', className="text-center mb-1"),

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

    # === 3. GRAPHIQUES PRINCIPAUX ===
    html.Div(id='main-charts-container'),

    # === 4. GRAPHIQUES TECHNIQUES DÉTAILLÉS (COLLAPSE) ===
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


# --- Callbacks ---

# Toggle des différents collapse
@callback(
    Output("collapse-technical-summary", "is_open"),
    Input("collapse-technical-summary-btn", "n_clicks"),
    State("collapse-technical-summary", "is_open"),
    prevent_initial_call=True
)
def toggle_technical_summary(n_clicks, is_open):
    return not is_open


@callback(
    Output("collapse-fundamental-summary", "is_open"),
    Input("collapse-fundamental-summary-btn", "n_clicks"),
    State("collapse-fundamental-summary", "is_open"),
    prevent_initial_call=True
)
def toggle_fundamental_summary(n_clicks, is_open):
    return not is_open


@callback(
    Output("collapse-technical", "is_open"),
    Input("collapse-technical-btn", "n_clicks"),
    State("collapse-technical", "is_open"),
    prevent_initial_call=True
)
def toggle_technical_collapse(n_clicks, is_open):
    return not is_open


# Mettre à jour le dropdown des actifs
@callback(
    [Output('asset-dropdown', 'options'),
     Output('asset-dropdown', 'value'),
     Output('remove-asset-dropdown', 'options'),
     Output('current-assets-list', 'children')],
    [Input('assets-store', 'data')]
)
def update_asset_dropdowns(assets):
    if not assets:
        assets = load_user_assets()
    
    options = [{'label': a, 'value': a} for a in assets]
    remove_options = [{'label': a, 'value': a} for a in assets]
    
    badges = [dbc.Badge(a, color="info", className="me-1 mb-1") for a in assets]
    
    return options, assets[0] if assets else None, remove_options, badges


# Gestion des actifs (ajout/suppression)
@callback(
    [Output('assets-store', 'data'),
     Output('asset-management-status', 'children'),
     Output('new-asset-input', 'value')],
    [Input('add-asset-btn', 'n_clicks'),
     Input('remove-asset-btn', 'n_clicks')],
    [State('new-asset-input', 'value'),
     State('remove-asset-dropdown', 'value'),
     State('assets-store', 'data')],
    prevent_initial_call=True
)
def manage_assets(add_clicks, remove_clicks, new_asset, asset_to_remove, current_assets):
    triggered = ctx.triggered_id
    
    if triggered == 'add-asset-btn' and new_asset:
        new_asset = new_asset.upper().strip()
        try:
            ticker = yf.Ticker(new_asset)
            hist = ticker.history(period='5d')
            if hist.empty:
                return current_assets, dbc.Alert(f"❌ '{new_asset}' non trouvé sur Yahoo Finance", color="danger", duration=4000), ""
        except Exception:
            return current_assets, dbc.Alert(f"❌ Erreur lors de la vérification de '{new_asset}'", color="danger", duration=4000), ""
        
        if new_asset in current_assets:
            return current_assets, dbc.Alert(f"⚠️ '{new_asset}' existe déjà", color="warning", duration=3000), ""
        
        current_assets.append(new_asset)
        save_user_assets(current_assets)
        return current_assets, dbc.Alert(f"✅ '{new_asset}' ajouté avec succès", color="success", duration=3000), ""
    
    elif triggered == 'remove-asset-btn' and asset_to_remove:
        if len(current_assets) <= 1:
            return current_assets, dbc.Alert("⚠️ Impossible de supprimer le dernier actif", color="warning", duration=3000), ""
        
        current_assets.remove(asset_to_remove)
        save_user_assets(current_assets)
        return current_assets, dbc.Alert(f"🗑️ '{asset_to_remove}' supprimé", color="info", duration=3000), ""
    
    return current_assets, "", ""


# Ouvrir/Fermer le modal
@callback(
    Output("config-modal", "is_open"),
    [Input("open-config-btn", "n_clicks"),
     Input("config-apply-btn", "n_clicks"),
     Input("config-reset-btn", "n_clicks")],
    [State("config-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_config_modal(open_clicks, apply_clicks, reset_clicks, is_open):
    return not is_open


# Appliquer la configuration
@callback(
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


# === CALLBACK POUR L'ANALYSE FONDAMENTALE ===
@callback(
    [Output('fundamental-summary-header', 'children'),
     Output('fundamental-details-container', 'children'),
     Output('fundamental-store', 'data')],
    [Input('asset-dropdown', 'value')],
    prevent_initial_call=True
)
def update_fundamental_analysis(selected_asset):
    if not selected_asset:
        return [], [], {}
    
    # Récupérer les données fondamentales
    current_data, quarterly_history = get_fundamental_data(selected_asset)
    
    if not current_data:
        header = [
            dbc.Badge("N/A", color="secondary", className="me-2"),
            html.Span("Données non disponibles (crypto, ETF, etc.)", className="text-muted small")
        ]
        return header, html.P("Analyse fondamentale non disponible pour cet actif.", className="text-muted"), {}
    
    # Calculer le score
    score, score_details = calculate_fundamental_score(current_data)
    
    # === HEADER AVEC SCORE ===
    if score:
        if score >= 4:
            badge_color = "success"
            score_text = "Excellent"
        elif score >= 3:
            badge_color = "primary"
            score_text = "Bon"
        elif score >= 2:
            badge_color = "warning"
            score_text = "Moyen"
        else:
            badge_color = "danger"
            score_text = "Faible"
        
        header = [
            dbc.Badge(f"Score: {score}/5", color=badge_color, className="me-2 fs-6"),
            dbc.Badge(score_text, color=badge_color, className="me-3"),
            html.Span(f"Secteur: {current_data.get('sector', 'N/A')}", className="text-muted small me-3"),
            html.Span(f"Cap: {format_large_number(current_data.get('market_cap'))}", className="text-muted small"),
        ]
    else:
        header = [dbc.Badge("Score N/A", color="secondary", className="me-2")]
    
    # === DÉTAILS FONDAMENTAUX ===
    details = create_fundamental_details(current_data, quarterly_history)
    
    # Stocker les données
    store_data = {
        'current': current_data,
        'history': quarterly_history.to_dict('records') if not quarterly_history.empty else []
    }
    
    return header, details, store_data


def create_fundamental_details(current_data, quarterly_history):
    """Crée la section détaillée avec les 5 catégories et l'historique."""
    
    tabs = dbc.Tabs([
        # === TAB 1: VALORISATION ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Valorisation", [
                    ("P/E Ratio", current_data.get('pe_ratio'), "pe_ratio", "< 20-25"),
                    ("P/E Forward", current_data.get('forward_pe'), "forward_pe", "< 20"),
                    ("PEG Ratio", current_data.get('peg_ratio'), "peg_ratio", "< 1.5"),
                    ("P/B Ratio", current_data.get('pb_ratio'), "pb_ratio", "< 3"),
                    ("P/S Ratio", current_data.get('ps_ratio'), "ps_ratio", "< 2-3"),
                    ("EV/EBITDA", current_data.get('ev_ebitda'), "ev_ebitda", "< 12-15"),
                    ("EV/Revenue", current_data.get('ev_revenue'), "ev_revenue", "< 3"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['pe_ratio', 'pb_ratio', 'ps_ratio'], 
                                      ['P/E', 'P/B', 'P/S'], "Ratios de Valorisation")
            ], className="p-2")
        ], label="💵 Valorisation", tab_id="tab-valuation"),
        
        # === TAB 2: RENTABILITÉ ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Rentabilité", [
                    ("ROE", current_data.get('roe'), "roe", "> 15%", "%"),
                    ("ROA", current_data.get('roa'), "roa", "> 5%", "%"),
                    ("Marge Brute", current_data.get('gross_margin'), "gross_margin", "> 40%", "%"),
                    ("Marge Opérationnelle", current_data.get('operating_margin'), "operating_margin", "> 15%", "%"),
                    ("Marge Nette", current_data.get('net_margin'), "net_margin", "> 10%", "%"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['roe', 'net_margin', 'gross_margin'], 
                                      ['ROE', 'Marge Nette', 'Marge Brute'], "Ratios de Rentabilité (%)")
            ], className="p-2")
        ], label="💰 Rentabilité", tab_id="tab-profitability"),
        
        # === TAB 3: SANTÉ FINANCIÈRE ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Santé Financière", [
                    ("Dette/Equity", current_data.get('debt_equity'), "debt_equity", "< 0.5-1"),
                    ("Current Ratio", current_data.get('current_ratio'), "current_ratio", "> 1.5"),
                    ("Quick Ratio", current_data.get('quick_ratio'), "quick_ratio", "> 1"),
                    ("Dette Totale", format_large_number(current_data.get('total_debt')), "total_debt", "—"),
                    ("Cash Disponible", format_large_number(current_data.get('total_cash')), "total_cash", "—"),
                    ("Free Cash Flow", format_large_number(current_data.get('free_cash_flow')), "free_cash_flow", "Positif"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['debt_equity', 'current_ratio', 'quick_ratio'], 
                                      ['Dette/Equity', 'Current Ratio', 'Quick Ratio'], "Ratios de Santé Financière")
            ], className="p-2")
        ], label="🏦 Santé Financière", tab_id="tab-health"),
        
        # === TAB 4: CROISSANCE ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Croissance", [
                    ("Croissance CA (YoY)", current_data.get('revenue_growth'), "revenue_growth", "> 5-10%", "%"),
                    ("Croissance Bénéfices", current_data.get('earnings_growth'), "earnings_growth", "> 10%", "%"),
                    ("EPS (TTM)", current_data.get('eps_trailing'), "eps_trailing", "—"),
                    ("EPS (Forward)", current_data.get('eps_forward'), "eps_forward", "—"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel - Revenus et Bénéfices", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['revenue', 'net_income'], 
                                      ['Revenus', 'Bénéfice Net'], "Revenus et Bénéfices (normalisé)", normalize=True),
                html.Br(),
                html.H6("📈 Croissance Year-over-Year", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['revenue_yoy', 'net_income_yoy'], 
                                      ['Croiss. CA YoY', 'Croiss. Bénéf. YoY'], "Croissance YoY (%)")
            ], className="p-2")
        ], label="📈 Croissance", tab_id="tab-growth"),
        
        # === TAB 5: DIVIDENDES ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Dividendes", [
                    ("Dividend Yield", current_data.get('dividend_yield'), "dividend_yield", "2-5%", "%"),
                    ("Dividende Annuel", current_data.get('dividend_rate'), "dividend_rate", "—", "$"),
                    ("Payout Ratio", current_data.get('payout_ratio'), "payout_ratio", "< 60%", "%"),
                    ("Yield Moyen 5 ans", current_data.get('five_year_avg_dividend_yield'), "five_year_avg_dividend_yield", "—", "%"),
                ]),
            ], className="p-2")
        ], label="💸 Dividendes", tab_id="tab-dividends"),
        
    ], id="fundamental-tabs", active_tab="tab-valuation")
    
    return tabs


def create_ratio_table(title, ratios):
    """
    Crée un tableau pour afficher les ratios avec descriptions détaillées.
    
    Args:
        title: Titre du tableau
        ratios: Liste de tuples (nom, valeur, clé_description, zone_idéale, [suffixe])
    """
    rows = []
    for ratio in ratios:
        name = ratio[0]
        value = ratio[1]
        desc_key = ratio[2]
        ideal = ratio[3]
        suffix = ratio[4] if len(ratio) > 4 else ''
        
        # Récupérer la description depuis le dictionnaire
        description = FUNDAMENTAL_DESCRIPTIONS.get(desc_key, "Description non disponible.")
        
        # Formater la valeur
        if isinstance(value, (int, float)) and value is not None:
            display_value = f"{value:.2f}{suffix}"
        elif isinstance(value, str):
            display_value = value  # Déjà formaté (comme format_large_number)
        else:
            display_value = "N/A"
        
        rows.append(
            html.Tr([
                html.Td(name, style={'fontWeight': 'bold', 'width': '12%', 'verticalAlign': 'top'}),
                html.Td(display_value, className="text-end", style={'width': '8%', 'verticalAlign': 'top'}),
                html.Td(description, className="text-muted small", style={'width': '65%', 'lineHeight': '1.4'}),
                html.Td(ideal, className="text-info small text-end", style={'width': '15%', 'verticalAlign': 'top'}),
            ])
        )
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Indicateur"),
            html.Th("Valeur", className="text-end"),
            html.Th("Explication détaillée"),
            html.Th("Zone Idéale", className="text-end"),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", className="mb-0")


def create_quarterly_chart(df, columns, names, title, normalize=False):
    """Crée un graphique de l'historique trimestriel."""
    if isinstance(df, list):
        df = pd.DataFrame(df)
    
    if df.empty:
        return html.P("Historique non disponible", className="text-muted text-center")
    
    fig = go.Figure()
    
    colors = ['#00bfff', '#ffa500', '#26a69a', '#ef5350', '#9932cc']
    
    for i, (col, name) in enumerate(zip(columns, names)):
        if col in df.columns:
            df_valid = df[df[col].notna()].copy()
            if df_valid.empty:
                continue
            
            y_data = df_valid[col]
            if normalize and len(y_data) > 0 and y_data.iloc[0] != 0:
                y_data = y_data / y_data.iloc[0] * 100
            
            x_data = pd.to_datetime(df_valid['date'])
            
            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                mode='lines+markers',
                name=name,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ))
    
    if len(fig.data) == 0:
        return html.P("Données insuffisantes pour l'historique", className="text-muted text-center")
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=12)),
        template='plotly_dark',
        height=250,
        margin=dict(l=50, r=50, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        xaxis=dict(title=""),
        yaxis=dict(title="")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def calculate_indicator_contributions(row, config):
    """
    Calcule la contribution de chaque indicateur à la recommandation.
    Retourne une liste de dictionnaires avec les détails de chaque indicateur.
    """
    contributions = []
    weights = config.get('signal_weights', {})
    rsi_cfg = config.get('rsi', {})
    stoch_cfg = config.get('stochastic', {})
    
    # Direction générale (achat ou vente)
    recommendation = row.get('recommendation', 'Neutre')
    is_buy = recommendation == 'Acheter'
    is_sell = recommendation == 'Vendre'
    
    # === RSI ===
    rsi = row.get('rsi')
    rsi_weight = weights.get('rsi_exit_oversold', 2.0)
    if rsi is not None:
        if rsi < rsi_cfg.get('oversold', 30):
            rsi_interpretation = "Survente (signal achat)"
            rsi_signal = "🟢 Achat"
            rsi_contrib = rsi_weight if is_buy else 0
        elif rsi > rsi_cfg.get('overbought', 70):
            rsi_interpretation = "Surachat (signal vente)"
            rsi_signal = "🔴 Vente"
            rsi_contrib = rsi_weight if is_sell else 0
        elif rsi_cfg.get('exit_oversold_min', 30) <= rsi <= rsi_cfg.get('exit_oversold_max', 40):
            rsi_interpretation = "Sortie de survente"
            rsi_signal = "🟢 Achat"
            rsi_contrib = rsi_weight if is_buy else 0
        elif rsi_cfg.get('exit_overbought_min', 60) <= rsi <= rsi_cfg.get('exit_overbought_max', 70):
            rsi_interpretation = "Sortie de surachat"
            rsi_signal = "🔴 Vente"
            rsi_contrib = rsi_weight if is_sell else 0
        else:
            rsi_interpretation = "Zone neutre"
            rsi_signal = "⚪ Neutre"
            rsi_contrib = 0
        
        contributions.append({
            'name': INDICATOR_DETAILS['rsi']['name'],
            'interpretation_guide': INDICATOR_DETAILS['rsi']['interpretation'],
            'value': f"{rsi:.1f}",
            'signal': rsi_signal,
            'weight': rsi_weight,
            'contribution': rsi_contrib,
            'interpretation': rsi_interpretation
        })
    
    # === STOCHASTIQUE ===
    stoch_k = row.get('stochastic_k')
    stoch_d = row.get('stochastic_d')
    stoch_weight = weights.get('stoch_bullish_cross', 1.0)
    if stoch_k is not None and stoch_d is not None:
        if stoch_k < stoch_cfg.get('oversold', 20):
            if stoch_k > stoch_d:
                stoch_interpretation = "Survente + croisement haussier"
                stoch_signal = "🟢 Achat"
                stoch_contrib = stoch_weight if is_buy else 0
            else:
                stoch_interpretation = "Survente (attendre croisement)"
                stoch_signal = "🟡 Attention"
                stoch_contrib = 0
        elif stoch_k > stoch_cfg.get('overbought', 80):
            if stoch_k < stoch_d:
                stoch_interpretation = "Surachat + croisement baissier"
                stoch_signal = "🔴 Vente"
                stoch_contrib = stoch_weight if is_sell else 0
            else:
                stoch_interpretation = "Surachat (attendre croisement)"
                stoch_signal = "🟡 Attention"
                stoch_contrib = 0
        else:
            stoch_interpretation = "Zone neutre"
            stoch_signal = "⚪ Neutre"
            stoch_contrib = 0
        
        contributions.append({
            'name': INDICATOR_DETAILS['stochastic']['name'],
            'interpretation_guide': INDICATOR_DETAILS['stochastic']['interpretation'],
            'value': f"%K: {stoch_k:.1f} / %D: {stoch_d:.1f}",
            'signal': stoch_signal,
            'weight': stoch_weight,
            'contribution': stoch_contrib,
            'interpretation': stoch_interpretation
        })
    
    # === MACD ===
    macd = row.get('macd')
    macd_signal_val = row.get('macd_signal')
    macd_hist = row.get('macd_histogram')
    macd_weight = weights.get('macd_bullish', 1.0)
    macd_hist_weight = weights.get('macd_histogram_positive', 0.5)
    
    if macd is not None and macd_signal_val is not None:
        macd_contrib = 0
        if macd > macd_signal_val:
            if macd_hist > 0:
                macd_interpretation = "Croisement haussier confirmé"
                macd_signal = "🟢 Achat"
                macd_contrib = macd_weight if is_buy else 0
            else:
                macd_interpretation = "MACD > Signal mais histogramme négatif"
                macd_signal = "🟡 Attention"
        elif macd < macd_signal_val:
            if macd_hist < 0:
                macd_interpretation = "Croisement baissier confirmé"
                macd_signal = "🔴 Vente"
                macd_contrib = macd_weight if is_sell else 0
            else:
                macd_interpretation = "MACD < Signal mais histogramme positif"
                macd_signal = "🟡 Attention"
        else:
            macd_interpretation = "Neutre"
            macd_signal = "⚪ Neutre"
        
        contributions.append({
            'name': INDICATOR_DETAILS['macd']['name'],
            'interpretation_guide': INDICATOR_DETAILS['macd']['interpretation'],
            'value': f"{macd:.2f} (Signal: {macd_signal_val:.2f})",
            'signal': macd_signal,
            'weight': macd_weight,
            'contribution': macd_contrib,
            'interpretation': macd_interpretation
        })
        
        # Histogramme MACD
        if macd_hist is not None:
            if macd_hist > 0:
                hist_interpretation = "Momentum haussier"
                hist_signal = "🟢 Achat"
                hist_contrib = macd_hist_weight if is_buy else 0
            elif macd_hist < 0:
                hist_interpretation = "Momentum baissier"
                hist_signal = "🔴 Vente"
                hist_contrib = macd_hist_weight if is_sell else 0
            else:
                hist_interpretation = "Neutre"
                hist_signal = "⚪ Neutre"
                hist_contrib = 0
            
            contributions.append({
                'name': INDICATOR_DETAILS['macd_histogram']['name'],
                'interpretation_guide': INDICATOR_DETAILS['macd_histogram']['interpretation'],
                'value': f"{macd_hist:.3f}",
                'signal': hist_signal,
                'weight': macd_hist_weight,
                'contribution': hist_contrib,
                'interpretation': hist_interpretation
            })
    
    # === TENDANCE ===
    trend = row.get('trend', 'neutral')
    trend_weight = weights.get('trend_bonus', 1.0)
    trend_map = {
        'strong_bullish': ('Tendance haussière forte', '🟢 Achat', trend_weight if is_buy else 0),
        'bullish': ('Tendance haussière', '🟢 Achat', trend_weight * 0.5 if is_buy else 0),
        'neutral': ('Tendance neutre', '⚪ Neutre', 0),
        'bearish': ('Tendance baissière', '🔴 Vente', trend_weight * 0.5 if is_sell else 0),
        'strong_bearish': ('Tendance baissière forte', '🔴 Vente', trend_weight if is_sell else 0),
    }
    trend_info = trend_map.get(trend, ('Inconnu', '⚪ Neutre', 0))
    
    contributions.append({
        'name': INDICATOR_DETAILS['trend']['name'],
        'interpretation_guide': INDICATOR_DETAILS['trend']['interpretation'],
        'value': trend.replace('_', ' ').title(),
        'signal': trend_info[1],
        'weight': trend_weight,
        'contribution': trend_info[2],
        'interpretation': trend_info[0]
    })
    
    # === ADX ===
    adx = row.get('adx')
    di_plus = row.get('di_plus')
    di_minus = row.get('di_minus')
    adx_cfg = config.get('adx', {})
    
    if adx is not None:
        if adx >= adx_cfg.get('very_strong', 40):
            adx_interpretation = "Tendance très forte"
        elif adx >= adx_cfg.get('strong', 25):
            adx_interpretation = "Tendance forte"
        elif adx >= adx_cfg.get('weak', 20):
            adx_interpretation = "Tendance modérée"
        else:
            adx_interpretation = "Pas de tendance claire"
        
        if di_plus is not None and di_minus is not None:
            if di_plus > di_minus:
                adx_signal = "🟢 Haussier"
            elif di_minus > di_plus:
                adx_signal = "🔴 Baissier"
            else:
                adx_signal = "⚪ Neutre"
            adx_value = f"ADX: {adx:.1f} (DI+: {di_plus:.1f}, DI-: {di_minus:.1f})"
        else:
            adx_signal = "⚪ Neutre"
            adx_value = f"{adx:.1f}"
        
        contributions.append({
            'name': INDICATOR_DETAILS['adx']['name'],
            'interpretation_guide': INDICATOR_DETAILS['adx']['interpretation'],
            'value': adx_value,
            'signal': adx_signal,
            'weight': "—",
            'contribution': "—",
            'interpretation': adx_interpretation
        })
    
    # === DIVERGENCE RSI ===
    rsi_div = row.get('rsi_divergence', 'none')
    div_weight = weights.get('rsi_divergence', 2.0)
    if rsi_div == 'bullish':
        div_interpretation = "Divergence haussière détectée"
        div_signal = "🟢 Achat"
        div_contrib = div_weight if is_buy else 0
    elif rsi_div == 'bearish':
        div_interpretation = "Divergence baissière détectée"
        div_signal = "🔴 Vente"
        div_contrib = div_weight if is_sell else 0
    else:
        div_interpretation = "Aucune divergence"
        div_signal = "⚪ Neutre"
        div_contrib = 0
    
    contributions.append({
        'name': INDICATOR_DETAILS['divergence']['name'],
        'interpretation_guide': INDICATOR_DETAILS['divergence']['interpretation'],
        'value': rsi_div.title() if rsi_div != 'none' else 'Aucune',
        'signal': div_signal,
        'weight': div_weight,
        'contribution': div_contrib,
        'interpretation': div_interpretation
    })
    
    # === PATTERN ===
    pattern = row.get('pattern', 'Aucun')
    pattern_dir = row.get('pattern_direction', 'neutral')
    pattern_weight = weights.get('pattern_bullish', 1.5)
    
    if pattern != 'Aucun' and pattern_dir != 'neutral':
        if pattern_dir == 'bullish':
            pattern_interpretation = f"Pattern haussier: {pattern}"
            pattern_signal = "🟢 Achat"
            pattern_contrib = pattern_weight if is_buy else 0
        else:
            pattern_interpretation = f"Pattern baissier: {pattern}"
            pattern_signal = "🔴 Vente"
            pattern_contrib = pattern_weight if is_sell else 0
    else:
        pattern_interpretation = "Aucun pattern significatif"
        pattern_signal = "⚪ Neutre"
        pattern_contrib = 0
    
    contributions.append({
        'name': INDICATOR_DETAILS['pattern']['name'],
        'interpretation_guide': INDICATOR_DETAILS['pattern']['interpretation'],
        'value': pattern,
        'signal': pattern_signal,
        'weight': pattern_weight,
        'contribution': pattern_contrib,
        'interpretation': pattern_interpretation
    })
    
    return contributions


def create_technical_indicators_table(row, config):
    """Crée le tableau détaillé des indicateurs techniques."""
    contributions = calculate_indicator_contributions(row, config)
    
    rows = []
    total_contribution = 0
    
    for ind in contributions:
        contrib = ind['contribution']
        if isinstance(contrib, (int, float)):
            total_contribution += contrib
            contrib_display = f"+{contrib:.1f}" if contrib > 0 else "0"
        else:
            contrib_display = contrib
        
        rows.append(
            html.Tr([
                html.Td(ind['name'], style={'fontWeight': 'bold', 'width': '15%'}),
                html.Td(ind['interpretation_guide'], className="small", style={'width': '30%'}),
                html.Td(ind['value'], className="text-center", style={'width': '15%'}),
                html.Td(ind['interpretation'], className="text-center", style={'width': '15%'}),
                html.Td(ind['signal'], className="text-center", style={'width': '10%'}),
                html.Td(str(ind['weight']), className="text-center", style={'width': '7%'}),
                html.Td(contrib_display, className="text-center", style={'width': '8%', 'fontWeight': 'bold'}),
            ])
        )
    
    # Ligne de total
    rows.append(
        html.Tr([
            html.Td("TOTAL", colSpan=6, className="text-end", style={'fontWeight': 'bold'}),
            html.Td(f"{total_contribution:.1f}", className="text-center", 
                   style={'fontWeight': 'bold', 'backgroundColor': '#198754' if row.get('recommendation') == 'Acheter' 
                          else '#dc3545' if row.get('recommendation') == 'Vendre' else '#6c757d'}),
        ], style={'backgroundColor': '#2c3034'})
    )
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Indicateur"),
            html.Th("Comment l'interpréter"),
            html.Th("Valeur", className="text-center"),
            html.Th("Interprétation", className="text-center"),
            html.Th("Signal", className="text-center"),
            html.Th("Poids", className="text-center"),
            html.Th("Contrib.", className="text-center"),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", responsive=True)


# Mise à jour du dashboard - Génération dynamique des graphiques
@callback(
    [Output('main-charts-container', 'children'),
     Output('technical-charts-container', 'children'),
     Output('technical-summary-header', 'children'),
     Output('technical-indicators-table', 'children'),
     Output('technical-data-store', 'data')],
    [Input('asset-dropdown', 'value'),
     Input('date-picker', 'date'),
     Input('period-dropdown', 'value'),
     Input('display-options', 'value'),
     Input('config-store', 'data')]
)
def update_dashboard(selected_asset, selected_date_str, selected_period, display_options, config):
    if not selected_asset or not selected_date_str:
        return [], [], [], [], {}

    df = fetch_and_prepare_data(selected_asset, period=selected_period, config=config)
    if df.empty:
        return [dbc.Alert("Aucune donnée disponible", color="warning")], [], [], [], {}

    selected_date = pd.to_datetime(selected_date_str)
    df_graph = df[df['Date'] <= selected_date].copy()
    
    if df_graph.empty:
        return [dbc.Alert("Aucune donnée pour cette date", color="warning")], [], [], [], {}

    # Dernière ligne pour le résumé
    last_row = df_graph.iloc[-1]
    
    # === HEADER TECHNIQUE ===
    recommendation = last_row.get('recommendation', 'Neutre')
    conviction = last_row.get('conviction', 0)
    trend = last_row.get('trend', 'neutral')
    close_price = last_row.get('close', 0)
    
    # Badge de recommandation
    if recommendation == 'Acheter':
        reco_badge = dbc.Badge(f"🟢 ACHETER", color="success", className="fs-5 me-2")
    elif recommendation == 'Vendre':
        reco_badge = dbc.Badge(f"🔴 VENDRE", color="danger", className="fs-5 me-2")
    else:
        reco_badge = dbc.Badge(f"⚪ NEUTRE", color="secondary", className="fs-5 me-2")
    
    # Badge de conviction
    conviction_color = "success" if conviction >= 4 else "warning" if conviction >= 3 else "secondary"
    conviction_badge = dbc.Badge(f"Conviction: {conviction}/5", color=conviction_color, className="me-2")
    
    # Badge de tendance
    trend_display = trend.replace('_', ' ').title()
    if 'bullish' in trend:
        trend_badge = dbc.Badge(f"↗ {trend_display}", color="success", className="me-3")
    elif 'bearish' in trend:
        trend_badge = dbc.Badge(f"↘ {trend_display}", color="danger", className="me-3")
    else:
        trend_badge = dbc.Badge(f"→ {trend_display}", color="secondary", className="me-3")
    
    technical_header = [
        html.Span(f"{selected_asset}", className="fs-5 fw-bold me-3"),
        html.Span(f"${close_price:.2f}", className="me-3"),
        reco_badge,
        conviction_badge,
        trend_badge,
        html.Span(f"({last_row.get('date', '')})", className="text-muted small"),
    ]
    
    # === TABLEAU DES INDICATEURS ===
    indicators_table = create_technical_indicators_table(last_row.to_dict(), config)
    
    # === GRAPHIQUES PRINCIPAUX ===
    main_charts = []
    
    if 'price' in display_options:
        show_ma = 'moving_averages' in display_options
        fig_price = create_price_chart(df_graph, selected_date, selected_asset, show_ma, config)
        main_charts.append(dcc.Graph(figure=fig_price, style={'height': '400px'}, config={'displayModeBar': False}))
    
    if 'recommendations' in display_options:
        fig_reco = create_recommendations_chart(df_graph, selected_date)
        main_charts.append(html.Div([
            html.H6(f"📊 Recommandations — {INDICATOR_DESCRIPTIONS['recommendations']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_reco, style={'height': '150px'}, config={'displayModeBar': False})
        ]))
    
    if 'trend' in display_options:
        fig_trend = create_trend_chart(df_graph, selected_date, config)
        main_charts.append(html.Div([
            html.H6(f"📈 Tendance (ADX) — {INDICATOR_DESCRIPTIONS['trend']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_trend, style={'height': '150px'}, config={'displayModeBar': False})
        ]))

    # === GRAPHIQUES TECHNIQUES (dans le collapse) ===
    technical_charts = []
    
    if 'macd' in display_options:
        fig_macd = create_macd_chart(df_graph, selected_date)
        technical_charts.append(html.Div([
            html.H6(f"📉 MACD — {INDICATOR_DESCRIPTIONS['macd']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_macd, style={'height': '180px'}, config={'displayModeBar': False})
        ]))
    
    if 'volume' in display_options:
        fig_volume = create_volume_chart(df_graph, selected_date)
        technical_charts.append(html.Div([
            html.H6(f"📊 Volume — {INDICATOR_DESCRIPTIONS['volume']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_volume, style={'height': '130px'}, config={'displayModeBar': False})
        ]))
    
    if 'rsi' in display_options:
        fig_rsi = create_rsi_chart(df_graph, selected_date, config)
        technical_charts.append(html.Div([
            html.H6(f"📊 RSI — {INDICATOR_DESCRIPTIONS['rsi']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_rsi, style={'height': '150px'}, config={'displayModeBar': False})
        ]))
    
    if 'stochastic' in display_options:
        fig_stoch = create_stochastic_chart(df_graph, selected_date, config)
        technical_charts.append(html.Div([
            html.H6(f"📈 Stochastique — {INDICATOR_DESCRIPTIONS['stochastic']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_stoch, style={'height': '150px'}, config={'displayModeBar': False})
        ]))
    
    if 'patterns' in display_options:
        fig_patterns = create_patterns_chart(df_graph, selected_date)
        technical_charts.append(html.Div([
            html.H6(f"🕯️ Patterns — {INDICATOR_DESCRIPTIONS['patterns']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(figure=fig_patterns, style={'height': '180px'}, config={'displayModeBar': False})
        ]))

    if not technical_charts:
        technical_charts = [html.P("Aucun indicateur technique sélectionné.", className="text-muted")]

    # Store data
    store_data = last_row.to_dict()
    
    return main_charts, technical_charts, technical_header, indicators_table, store_data


# === Fonctions de création des graphiques ===

def create_price_chart(df_graph, selected_date, asset_name, show_ma, config):
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df_graph['Date'], open=df_graph['open'], high=df_graph['high'],
        low=df_graph['low'], close=df_graph['close'], name='Prix',
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ))
    
    if show_ma:
        ma_cfg = config.get('moving_averages', {})
        if 'sma_20' in df_graph.columns:
            fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['sma_20'],
                mode='lines', name=f"SMA {ma_cfg.get('sma_short', 20)}",
                line=dict(color='#00bfff', width=1.5), opacity=0.8))
        if 'sma_50' in df_graph.columns:
            fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['sma_50'],
                mode='lines', name=f"SMA {ma_cfg.get('sma_medium', 50)}",
                line=dict(color='#ffa500', width=1.5), opacity=0.8))
        if 'sma_200' in df_graph.columns:
            fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['sma_200'],
                mode='lines', name=f"SMA {ma_cfg.get('sma_long', 200)}",
                line=dict(color='#9932cc', width=2), opacity=0.9))
    
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    desc = INDICATOR_DESCRIPTIONS['price']
    fig.update_layout(
        title=dict(text=f'{asset_name} — {desc}', font=dict(size=14)),
        xaxis_rangeslider_visible=False, template='plotly_dark', showlegend=show_ma,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=50, r=50, t=50, b=20)
    )
    return fig


def create_recommendations_chart(df_graph, selected_date):
    fig = go.Figure()
    conviction_values = []
    bar_colors = []
    hover_texts = []
    
    for _, row in df_graph.iterrows():
        trend = row.get('trend', 'neutral')
        if row['recommendation'] == 'Acheter':
            conviction_values.append(row['conviction'])
            bar_colors.append('#26a69a')
            hover_texts.append(f"ACHETER | Conv: {row['conviction']}/5 | Trend: {trend}")
        elif row['recommendation'] == 'Vendre':
            conviction_values.append(-row['conviction'])
            bar_colors.append('#ef5350')
            hover_texts.append(f"VENDRE | Conv: {row['conviction']}/5 | Trend: {trend}")
        else:
            conviction_values.append(0)
            bar_colors.append('rgba(128,128,128,0.3)')
            hover_texts.append(f"Neutre | Trend: {trend}")
    
    fig.add_trace(go.Bar(x=df_graph['Date'], y=conviction_values, marker_color=bar_colors, 
                         hovertext=hover_texts, hoverinfo='text+x'))
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.add_annotation(x=0.02, y=0.85, xref="paper", yref="paper", text="↑ ACHETER", 
                       showarrow=False, font=dict(size=10, color="#26a69a"))
    fig.add_annotation(x=0.02, y=0.15, xref="paper", yref="paper", text="↓ VENDRE", 
                       showarrow=False, font=dict(size=10, color="#ef5350"))
    
    fig.update_layout(
        template='plotly_dark',
        yaxis=dict(range=[-5.5, 5.5], tickvals=[-5, 0, 5], ticktext=['Vente forte', '0', 'Achat fort']),
        showlegend=False, margin=dict(l=50, r=50, t=10, b=20)
    )
    return fig


def create_trend_chart(df_graph, selected_date, config):
    fig = go.Figure()
    trend_values = []
    trend_colors = []
    
    adx_strong = config.get('adx', {}).get('strong', 25)
    
    for _, row in df_graph.iterrows():
        adx = row.get('adx', 0)
        di_plus = row.get('di_plus', 0)
        di_minus = row.get('di_minus', 0)
        
        if pd.isna(adx):
            trend_values.append(0)
            trend_colors.append('rgba(128,128,128,0.3)')
            continue
        
        if di_plus > di_minus:
            trend_values.append(adx)
            trend_colors.append('#26a69a' if adx >= adx_strong else '#4a7c6f')
        else:
            trend_values.append(-adx)
            trend_colors.append('#ef5350' if adx >= adx_strong else '#8b5a5a')
    
    fig.add_trace(go.Bar(x=df_graph['Date'], y=trend_values, marker_color=trend_colors))
    fig.add_hline(y=adx_strong, line_dash="dot", line_color="green", opacity=0.5)
    fig.add_hline(y=-adx_strong, line_dash="dot", line_color="red", opacity=0.5)
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.update_layout(
        template='plotly_dark',
        yaxis=dict(range=[-60, 60], tickvals=[-40, 0, 40], ticktext=['Baisse', '0', 'Hausse']),
        showlegend=False, margin=dict(l=50, r=50, t=10, b=20)
    )
    return fig


def create_macd_chart(df_graph, selected_date):
    fig = go.Figure()
    
    if 'macd' not in df_graph.columns:
        return fig
    
    histogram_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df_graph['macd_histogram'].fillna(0)]
    
    fig.add_trace(go.Bar(x=df_graph['Date'], y=df_graph['macd_histogram'], marker_color=histogram_colors, opacity=0.7, name='Hist'))
    fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['macd'], mode='lines', name='MACD', line=dict(color='#00bfff', width=1.5)))
    fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['macd_signal'], mode='lines', name='Signal', line=dict(color='#ffa500', width=1.5)))
    fig.add_hline(y=0, line_dash="solid", line_color="white", opacity=0.5)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.update_layout(
        template='plotly_dark', showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
        margin=dict(l=50, r=50, t=10, b=20)
    )
    return fig


def create_volume_chart(df_graph, selected_date):
    fig = go.Figure()
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df_graph['close'], df_graph['open'])]
    fig.add_trace(go.Bar(x=df_graph['Date'], y=df_graph['volume'], marker_color=colors, opacity=0.7))
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    fig.update_layout(template='plotly_dark', showlegend=False, margin=dict(l=50, r=50, t=10, b=20))
    return fig


def create_rsi_chart(df_graph, selected_date, config):
    fig = go.Figure()
    rsi_cfg = config.get('rsi', {})
    
    fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['rsi'], mode='lines', name='RSI', line=dict(color='#ffd700', width=1.5)))
    fig.add_hrect(y0=rsi_cfg.get('overbought', 70), y1=100, fillcolor="red", opacity=0.15, line_width=0)
    fig.add_hrect(y0=0, y1=rsi_cfg.get('oversold', 30), fillcolor="green", opacity=0.15, line_width=0)
    fig.add_hline(y=rsi_cfg.get('overbought', 70), line_dash="dot", line_color="red", opacity=0.5)
    fig.add_hline(y=rsi_cfg.get('oversold', 30), line_dash="dot", line_color="green", opacity=0.5)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.update_layout(template='plotly_dark', yaxis=dict(range=[0, 100]), showlegend=False, margin=dict(l=50, r=50, t=10, b=20))
    return fig


def create_stochastic_chart(df_graph, selected_date, config):
    fig = go.Figure()
    stoch_cfg = config.get('stochastic', {})
    
    fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['stochastic_k'], mode='lines', name='%K', line=dict(color='#00bfff', width=1.5)))
    fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['stochastic_d'], mode='lines', name='%D', line=dict(color='#ff6347', width=1.5)))
    fig.add_hrect(y0=stoch_cfg.get('overbought', 80), y1=100, fillcolor="red", opacity=0.15, line_width=0)
    fig.add_hrect(y0=0, y1=stoch_cfg.get('oversold', 20), fillcolor="green", opacity=0.15, line_width=0)
    fig.add_hline(y=stoch_cfg.get('overbought', 80), line_dash="dot", line_color="red", opacity=0.5)
    fig.add_hline(y=stoch_cfg.get('oversold', 20), line_dash="dot", line_color="green", opacity=0.5)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.update_layout(
        template='plotly_dark', yaxis=dict(range=[0, 100]), showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
        margin=dict(l=50, r=50, t=10, b=20)
    )
    return fig


def create_patterns_chart(df_graph, selected_date):
    fig = go.Figure()
    df_with_patterns = df_graph[df_graph['pattern'] != 'Aucun'].copy()
    
    if not df_with_patterns.empty:
        for direction, y_val, color, symbol in [
            ('bullish', 1, '#26a69a', 'triangle-up'),
            ('bearish', -1, '#ef5350', 'triangle-down'),
            ('neutral', 0, '#ffd700', 'diamond')
        ]:
            df_dir = df_with_patterns[df_with_patterns['pattern_direction'] == direction]
            if not df_dir.empty:
                fig.add_trace(go.Scatter(
                    x=df_dir['Date'], y=[y_val] * len(df_dir), mode='markers+text',
                    marker=dict(symbol=symbol, size=14 if direction != 'neutral' else 10, color=color, line=dict(width=1, color='white')),
                    text=df_dir['pattern'], textposition='top center' if y_val >= 0 else 'bottom center',
                    textfont=dict(size=8, color=color), name=direction.capitalize()
                ))
    
    fig.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.3)
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    
    fig.update_layout(
        template='plotly_dark',
        yaxis=dict(range=[-1.8, 1.8], tickvals=[-1, 0, 1], ticktext=['Baissier', 'Neutre', 'Haussier']),
        showlegend=False, margin=dict(l=50, r=50, t=10, b=20)
    )
    return fig


# Callback de sauvegarde
@callback(
    Output('save-status', 'children'),
    Input('save-button', 'n_clicks'),
    [State('asset-dropdown', 'value'), State('date-picker', 'date'), State('config-store', 'data')],
    prevent_initial_call=True
)
def save_data_callback(n_clicks, selected_asset, selected_date_str, config):
    df = fetch_and_prepare_data(selected_asset, period="5y", config=config)
    df_today = df[df['date'] == selected_date_str].copy()

    if df_today.empty:
        return dbc.Alert(f"Aucune donnée pour {selected_asset} le {selected_date_str}.", color="warning", duration=4000)

    save_indicators_to_db(df_today)
    return dbc.Alert(f"✅ Indicateurs sauvegardés pour {selected_asset} le {selected_date_str}", color="success", duration=4000, dismissable=True)


if __name__ == '__main__':
    app.run(debug=True)