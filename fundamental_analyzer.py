# fundamental_analyzer.py
"""
Module d'analyse fondamentale avec historique trimestriel.
Récupère et calcule les ratios fondamentaux à partir des données yfinance.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


# === SEUILS IDÉAUX PAR CATÉGORIE ===
FUNDAMENTAL_THRESHOLDS = {
    'valuation': {
        'pe_ratio': {'good': 20, 'max': 25, 'direction': 'lower'},
        'peg_ratio': {'good': 1.0, 'max': 1.5, 'direction': 'lower'},
        'pb_ratio': {'good': 2, 'max': 3, 'direction': 'lower'},
        'ps_ratio': {'good': 2, 'max': 3, 'direction': 'lower'},
        'ev_ebitda': {'good': 10, 'max': 15, 'direction': 'lower'},
    },
    'profitability': {
        'roe': {'good': 15, 'min': 10, 'direction': 'higher'},
        'roa': {'good': 5, 'min': 3, 'direction': 'higher'},
        'roic': {'good': 10, 'min': 7, 'direction': 'higher'},
        'net_margin': {'good': 10, 'min': 5, 'direction': 'higher'},
        'gross_margin': {'good': 40, 'min': 20, 'direction': 'higher'},
    },
    'financial_health': {
        'debt_equity': {'good': 0.5, 'max': 1.0, 'direction': 'lower'},
        'current_ratio': {'good': 1.5, 'min': 1.0, 'direction': 'higher'},
        'quick_ratio': {'good': 1.0, 'min': 0.8, 'direction': 'higher'},
        'interest_coverage': {'good': 5, 'min': 3, 'direction': 'higher'},
    },
    'growth': {
        'revenue_growth': {'good': 10, 'min': 5, 'direction': 'higher'},
        'eps_growth': {'good': 10, 'min': 5, 'direction': 'higher'},
        'fcf_growth': {'good': 5, 'min': 0, 'direction': 'higher'},
    },
    'dividends': {
        'dividend_yield': {'good': 2, 'max': 5, 'direction': 'range'},
        'payout_ratio': {'good': 40, 'max': 60, 'direction': 'lower'},
    }
}


def get_fundamental_data(ticker_symbol):
    """
    Récupère les données fondamentales actuelles et historiques depuis yfinance.
    
    Returns:
        dict: Données fondamentales actuelles
        pd.DataFrame: Historique trimestriel des ratios calculés
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Données actuelles depuis .info
        current_data = extract_current_fundamentals(info)
        
        # Historique trimestriel
        quarterly_history = calculate_quarterly_history(ticker)
        
        return current_data, quarterly_history
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données fondamentales pour {ticker_symbol}: {e}")
        return {}, pd.DataFrame()


def extract_current_fundamentals(info):
    """
    Extrait les ratios fondamentaux actuels depuis ticker.info
    """
    def safe_get(key, default=None):
        val = info.get(key, default)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return val
    
    current = {
        # === VALORISATION ===
        'pe_ratio': safe_get('trailingPE'),
        'forward_pe': safe_get('forwardPE'),
        'peg_ratio': safe_get('pegRatio'),
        'pb_ratio': safe_get('priceToBook'),
        'ps_ratio': safe_get('priceToSalesTrailing12Months'),
        'ev_ebitda': safe_get('enterpriseToEbitda'),
        'ev_revenue': safe_get('enterpriseToRevenue'),
        
        # === RENTABILITÉ ===
        'roe': safe_get('returnOnEquity', 0) * 100 if safe_get('returnOnEquity') else None,
        'roa': safe_get('returnOnAssets', 0) * 100 if safe_get('returnOnAssets') else None,
        'gross_margin': safe_get('grossMargins', 0) * 100 if safe_get('grossMargins') else None,
        'operating_margin': safe_get('operatingMargins', 0) * 100 if safe_get('operatingMargins') else None,
        'net_margin': safe_get('profitMargins', 0) * 100 if safe_get('profitMargins') else None,
        
        # === SANTÉ FINANCIÈRE ===
        'debt_equity': safe_get('debtToEquity', 0) / 100 if safe_get('debtToEquity') else None,
        'current_ratio': safe_get('currentRatio'),
        'quick_ratio': safe_get('quickRatio'),
        'total_debt': safe_get('totalDebt'),
        'total_cash': safe_get('totalCash'),
        'free_cash_flow': safe_get('freeCashflow'),
        
        # === CROISSANCE ===
        'revenue_growth': safe_get('revenueGrowth', 0) * 100 if safe_get('revenueGrowth') else None,
        'earnings_growth': safe_get('earningsGrowth', 0) * 100 if safe_get('earningsGrowth') else None,
        'eps_trailing': safe_get('trailingEps'),
        'eps_forward': safe_get('forwardEps'),
        
        # === DIVIDENDES ===
        'dividend_yield': safe_get('dividendYield', 0) * 100 if safe_get('dividendYield') else None,
        'dividend_rate': safe_get('dividendRate'),
        'payout_ratio': safe_get('payoutRatio', 0) * 100 if safe_get('payoutRatio') else None,
        'five_year_avg_dividend_yield': safe_get('fiveYearAvgDividendYield'),
        
        # === INFOS GÉNÉRALES ===
        'market_cap': safe_get('marketCap'),
        'enterprise_value': safe_get('enterpriseValue'),
        'shares_outstanding': safe_get('sharesOutstanding'),
        'sector': safe_get('sector', 'N/A'),
        'industry': safe_get('industry', 'N/A'),
    }
    
    return current


def calculate_quarterly_history(ticker):
    """
    Calcule l'historique trimestriel des ratios fondamentaux.
    Utilise les financials trimestriels + prix historiques.
    """
    try:
        # Récupérer les états financiers trimestriels
        quarterly_financials = ticker.quarterly_financials
        quarterly_balance = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow
        
        if quarterly_financials.empty:
            return pd.DataFrame()
        
        # Récupérer les prix historiques
        hist = ticker.history(period="5y")
        if hist.empty:
            return pd.DataFrame()
        
        # Récupérer les infos statiques
        info = ticker.info
        shares_outstanding = info.get('sharesOutstanding', None)
        
        records = []
        
        # Parcourir chaque trimestre disponible
        for quarter_date in quarterly_financials.columns:
            record = {'date': quarter_date, 'quarter': quarter_date.strftime('%Y-Q%q') if hasattr(quarter_date, 'strftime') else str(quarter_date)}
            
            try:
                # === Données du compte de résultat ===
                net_income = get_financial_value(quarterly_financials, quarter_date, 
                    ['Net Income', 'Net Income Common Stockholders', 'NetIncome'])
                total_revenue = get_financial_value(quarterly_financials, quarter_date, 
                    ['Total Revenue', 'TotalRevenue', 'Revenue'])
                gross_profit = get_financial_value(quarterly_financials, quarter_date, 
                    ['Gross Profit', 'GrossProfit'])
                operating_income = get_financial_value(quarterly_financials, quarter_date, 
                    ['Operating Income', 'OperatingIncome', 'EBIT'])
                ebitda = get_financial_value(quarterly_financials, quarter_date, 
                    ['EBITDA', 'Ebitda'])
                
                # === Données du bilan ===
                if not quarterly_balance.empty and quarter_date in quarterly_balance.columns:
                    total_equity = get_financial_value(quarterly_balance, quarter_date, 
                        ['Stockholders Equity', 'Total Stockholder Equity', 'StockholdersEquity', 'Total Equity'])
                    total_assets = get_financial_value(quarterly_balance, quarter_date, 
                        ['Total Assets', 'TotalAssets'])
                    total_debt = get_financial_value(quarterly_balance, quarter_date, 
                        ['Total Debt', 'TotalDebt', 'Long Term Debt', 'LongTermDebt'])
                    current_assets = get_financial_value(quarterly_balance, quarter_date, 
                        ['Current Assets', 'CurrentAssets', 'Total Current Assets'])
                    current_liabilities = get_financial_value(quarterly_balance, quarter_date, 
                        ['Current Liabilities', 'CurrentLiabilities', 'Total Current Liabilities'])
                    inventory = get_financial_value(quarterly_balance, quarter_date, 
                        ['Inventory', 'Inventories'])
                else:
                    total_equity = total_assets = total_debt = None
                    current_assets = current_liabilities = inventory = None
                
                # === Données du cash flow ===
                if not quarterly_cashflow.empty and quarter_date in quarterly_cashflow.columns:
                    free_cash_flow = get_financial_value(quarterly_cashflow, quarter_date, 
                        ['Free Cash Flow', 'FreeCashFlow'])
                    if free_cash_flow is None:
                        operating_cf = get_financial_value(quarterly_cashflow, quarter_date, 
                            ['Operating Cash Flow', 'Cash Flow From Operating Activities'])
                        capex = get_financial_value(quarterly_cashflow, quarter_date, 
                            ['Capital Expenditure', 'Capital Expenditures', 'CapEx'])
                        if operating_cf is not None and capex is not None:
                            free_cash_flow = operating_cf + capex  # capex est généralement négatif
                else:
                    free_cash_flow = None
                
                # === Prix à la date du trimestre ===
                quarter_price = get_price_at_date(hist, quarter_date)
                
                # === Calcul des ratios ===
                
                # Marges
                if total_revenue and total_revenue != 0:
                    record['gross_margin'] = (gross_profit / total_revenue * 100) if gross_profit else None
                    record['operating_margin'] = (operating_income / total_revenue * 100) if operating_income else None
                    record['net_margin'] = (net_income / total_revenue * 100) if net_income else None
                
                # ROE & ROA
                if total_equity and total_equity != 0 and net_income:
                    record['roe'] = (net_income / total_equity * 100) * 4  # Annualisé
                if total_assets and total_assets != 0 and net_income:
                    record['roa'] = (net_income / total_assets * 100) * 4  # Annualisé
                
                # Ratios d'endettement
                if total_equity and total_equity != 0 and total_debt:
                    record['debt_equity'] = total_debt / total_equity
                
                # Ratios de liquidité
                if current_liabilities and current_liabilities != 0:
                    if current_assets:
                        record['current_ratio'] = current_assets / current_liabilities
                    if current_assets and inventory:
                        record['quick_ratio'] = (current_assets - inventory) / current_liabilities
                
                # EPS et P/E
                if shares_outstanding and net_income:
                    eps = (net_income * 4) / shares_outstanding  # Annualisé
                    record['eps'] = eps
                    if quarter_price and eps and eps != 0:
                        record['pe_ratio'] = quarter_price / eps
                
                # P/B
                if shares_outstanding and total_equity and quarter_price:
                    book_per_share = total_equity / shares_outstanding
                    if book_per_share and book_per_share != 0:
                        record['pb_ratio'] = quarter_price / book_per_share
                
                # P/S
                if shares_outstanding and total_revenue and quarter_price:
                    sales_per_share = (total_revenue * 4) / shares_outstanding  # Annualisé
                    if sales_per_share and sales_per_share != 0:
                        record['ps_ratio'] = quarter_price / sales_per_share
                
                # Free Cash Flow
                record['free_cash_flow'] = free_cash_flow
                
                # Prix et Market Cap
                record['price'] = quarter_price
                if quarter_price and shares_outstanding:
                    record['market_cap'] = quarter_price * shares_outstanding
                
                # Revenus et bénéfices (pour tracking)
                record['revenue'] = total_revenue
                record['net_income'] = net_income
                
            except Exception as e:
                print(f"Erreur pour le trimestre {quarter_date}: {e}")
                continue
            
            records.append(record)
        
        df = pd.DataFrame(records)
        
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculer les croissances YoY
            df = calculate_growth_rates(df)
        
        return df
        
    except Exception as e:
        print(f"Erreur lors du calcul de l'historique trimestriel: {e}")
        return pd.DataFrame()


def get_financial_value(df, date, possible_names):
    """
    Récupère une valeur financière en essayant plusieurs noms possibles.
    """
    if df.empty or date not in df.columns:
        return None
    
    for name in possible_names:
        if name in df.index:
            val = df.loc[name, date]
            if pd.notna(val):
                return val
    return None


def get_price_at_date(hist, target_date):
    """
    Récupère le prix de clôture à une date donnée (ou la plus proche).
    """
    try:
        target = pd.Timestamp(target_date).tz_localize(None)
        hist_copy = hist.copy()
        hist_copy.index = hist_copy.index.tz_localize(None)
        
        # Chercher la date exacte ou les 5 jours suivants
        for delta in range(0, 10):
            check_date = target + pd.Timedelta(days=delta)
            if check_date in hist_copy.index:
                return hist_copy.loc[check_date, 'Close']
        
        # Sinon, prendre la date la plus proche
        idx = hist_copy.index.get_indexer([target], method='nearest')[0]
        if idx >= 0 and idx < len(hist_copy):
            return hist_copy.iloc[idx]['Close']
        
        return None
    except Exception:
        return None


def calculate_growth_rates(df):
    """
    Calcule les taux de croissance YoY pour les métriques clés.
    """
    if len(df) < 4:  # Besoin d'au moins 4 trimestres pour YoY
        return df
    
    for col in ['revenue', 'net_income', 'eps', 'free_cash_flow']:
        if col in df.columns:
            df[f'{col}_yoy'] = df[col].pct_change(periods=4) * 100
    
    return df


def calculate_fundamental_score(current_data):
    """
    Calcule un score fondamental global de 1 à 5 basé sur les ratios.
    """
    scores = []
    details = {}
    
    # === VALORISATION (25%) ===
    valuation_scores = []
    
    pe = current_data.get('pe_ratio')
    if pe and pe > 0:
        if pe < 15:
            valuation_scores.append(5)
        elif pe < 20:
            valuation_scores.append(4)
        elif pe < 25:
            valuation_scores.append(3)
        elif pe < 35:
            valuation_scores.append(2)
        else:
            valuation_scores.append(1)
    
    peg = current_data.get('peg_ratio')
    if peg and peg > 0:
        if peg < 1:
            valuation_scores.append(5)
        elif peg < 1.5:
            valuation_scores.append(4)
        elif peg < 2:
            valuation_scores.append(3)
        else:
            valuation_scores.append(2)
    
    if valuation_scores:
        details['valuation'] = np.mean(valuation_scores)
        scores.append(('valuation', details['valuation'], 0.25))
    
    # === RENTABILITÉ (25%) ===
    profitability_scores = []
    
    roe = current_data.get('roe')
    if roe is not None:
        if roe > 20:
            profitability_scores.append(5)
        elif roe > 15:
            profitability_scores.append(4)
        elif roe > 10:
            profitability_scores.append(3)
        elif roe > 5:
            profitability_scores.append(2)
        else:
            profitability_scores.append(1)
    
    net_margin = current_data.get('net_margin')
    if net_margin is not None:
        if net_margin > 20:
            profitability_scores.append(5)
        elif net_margin > 15:
            profitability_scores.append(4)
        elif net_margin > 10:
            profitability_scores.append(3)
        elif net_margin > 5:
            profitability_scores.append(2)
        else:
            profitability_scores.append(1)
    
    if profitability_scores:
        details['profitability'] = np.mean(profitability_scores)
        scores.append(('profitability', details['profitability'], 0.25))
    
    # === SANTÉ FINANCIÈRE (25%) ===
    health_scores = []
    
    debt_equity = current_data.get('debt_equity')
    if debt_equity is not None:
        if debt_equity < 0.3:
            health_scores.append(5)
        elif debt_equity < 0.5:
            health_scores.append(4)
        elif debt_equity < 1:
            health_scores.append(3)
        elif debt_equity < 2:
            health_scores.append(2)
        else:
            health_scores.append(1)
    
    current_ratio = current_data.get('current_ratio')
    if current_ratio is not None:
        if current_ratio > 2:
            health_scores.append(5)
        elif current_ratio > 1.5:
            health_scores.append(4)
        elif current_ratio > 1:
            health_scores.append(3)
        else:
            health_scores.append(2)
    
    if health_scores:
        details['financial_health'] = np.mean(health_scores)
        scores.append(('financial_health', details['financial_health'], 0.25))
    
    # === CROISSANCE (25%) ===
    growth_scores = []
    
    revenue_growth = current_data.get('revenue_growth')
    if revenue_growth is not None:
        if revenue_growth > 20:
            growth_scores.append(5)
        elif revenue_growth > 10:
            growth_scores.append(4)
        elif revenue_growth > 5:
            growth_scores.append(3)
        elif revenue_growth > 0:
            growth_scores.append(2)
        else:
            growth_scores.append(1)
    
    earnings_growth = current_data.get('earnings_growth')
    if earnings_growth is not None:
        if earnings_growth > 20:
            growth_scores.append(5)
        elif earnings_growth > 10:
            growth_scores.append(4)
        elif earnings_growth > 5:
            growth_scores.append(3)
        elif earnings_growth > 0:
            growth_scores.append(2)
        else:
            growth_scores.append(1)
    
    if growth_scores:
        details['growth'] = np.mean(growth_scores)
        scores.append(('growth', details['growth'], 0.25))
    
    # === SCORE GLOBAL ===
    if not scores:
        return None, details
    
    total_weight = sum(s[2] for s in scores)
    weighted_sum = sum(s[1] * s[2] for s in scores)
    global_score = weighted_sum / total_weight if total_weight > 0 else 0
    
    return round(global_score, 1), details


def format_large_number(num):
    """Formate les grands nombres (M, B, T)."""
    if num is None:
        return "N/A"
    if abs(num) >= 1e12:
        return f"{num/1e12:.1f}T"
    elif abs(num) >= 1e9:
        return f"{num/1e9:.1f}B"
    elif abs(num) >= 1e6:
        return f"{num/1e6:.1f}M"
    elif abs(num) >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.2f}"


def format_ratio(val, suffix='', decimals=2):
    """Formate un ratio avec gestion des None."""
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}{suffix}"


def get_ratio_color(value, thresholds, ratio_type='lower'):
    """
    Retourne une couleur selon la qualité du ratio.
    ratio_type: 'lower' (plus petit = mieux), 'higher' (plus grand = mieux), 'range'
    """
    if value is None:
        return '#6c757d'  # Gris
    
    if ratio_type == 'lower':
        good = thresholds.get('good', 15)
        max_val = thresholds.get('max', 25)
        if value <= good:
            return '#28a745'  # Vert
        elif value <= max_val:
            return '#ffc107'  # Jaune
        else:
            return '#dc3545'  # Rouge
    
    elif ratio_type == 'higher':
        good = thresholds.get('good', 15)
        min_val = thresholds.get('min', 10)
        if value >= good:
            return '#28a745'
        elif value >= min_val:
            return '#ffc107'
        else:
            return '#dc3545'
    
    else:  # range
        good = thresholds.get('good', 2)
        max_val = thresholds.get('max', 5)
        if good <= value <= max_val:
            return '#28a745'
        elif value < good:
            return '#ffc107'
        else:
            return '#dc3545'
    
    return '#6c757d'