# data_handler.py
import yfinance as yf
import pandas as pd
from indicator_calculator import calculate_all_indicators
from config import get_default_config

MIN_PERIOD_FOR_INDICATORS = "2y"


def get_asset_id(ticker):
    """Récupère l'ID d'un actif depuis PostgreSQL. S'il n'existe pas, il le crée."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM assets WHERE ticker = %s", (ticker,))
        data = cursor.fetchone()
        
        if data is None:
            # L'actif n'existe pas, on le crée
            try:
                info = yf.Ticker(ticker).info
                name = info.get('longName', ticker)
                asset_type = info.get('quoteType', 'EQUITY')
            except Exception:
                name = ticker
                asset_type = 'UNKNOWN'
            
            cursor.execute(
                "INSERT INTO assets (ticker, name, asset_type) VALUES (%s, %s, %s) RETURNING id",
                (ticker, name, asset_type)
            )
            asset_id = cursor.fetchone()[0]
            conn.commit()
        else:
            asset_id = data[0]
        
        cursor.close()
        conn.close()
        return asset_id
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'asset_id pour {ticker}: {e}")
        # Retourner un ID fictif basé sur le hash du ticker
        return hash(ticker) % 1000000


def period_to_days(period_str):
    """Convertit une chaîne de période en nombre approximatif de jours."""
    mapping = {
        '1mo': 30,
        '3mo': 90,
        '6mo': 180,
        '1y': 365,
        '2y': 730,
        '5y': 1825,
        '10y': 3650,
        'max': 10000
    }
    return mapping.get(period_str, 365)


def get_minimum_period(requested_period):
    """Retourne la période minimale à télécharger pour avoir des indicateurs stables."""
    requested_days = period_to_days(requested_period)
    min_days_needed = requested_days + 300
    
    if min_days_needed <= 730:
        return "2y"
    elif min_days_needed <= 1825:
        return "5y"
    else:
        return "10y"


def fetch_and_prepare_data(ticker, period="2y", return_full=False, config=None):
    """
    Récupère les données depuis Yahoo Finance, calcule les indicateurs, et retourne un DataFrame.
    
    Args:
        ticker: Le symbole de l'actif
        period: La période d'affichage souhaitée
        return_full: Si True, retourne toutes les données
        config: Configuration des paramètres (optionnel)
    """
    if config is None:
        config = get_default_config()
        print("⚠️ fetch_and_prepare_data: config=None, utilisation des défauts")
    else:
        ind_cfg = config.get('individual_weights', {})
        dec_cfg = config.get('decision', {})
        print(f"\n{'='*60}")
        print(f"📊 fetch_and_prepare_data pour {ticker}")
        print(f"   >>> CONFIG REÇUE <<<")
        print(f"   rsi_divergence = {ind_cfg.get('rsi_divergence')}")
        print(f"   min_conviction_threshold = {dec_cfg.get('min_conviction_threshold')}")
        print(f"   min_combinations_for_signal = {dec_cfg.get('min_combinations_for_signal')}")
        print(f"{'='*60}\n")
    
    print(f"📊 Téléchargement des données pour {ticker}...")
    
    asset_id = get_asset_id(ticker)
    download_period = get_minimum_period(period)
    
    try:
        df = yf.download(ticker, period=download_period, auto_adjust=True, progress=False)
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de {ticker}: {e}")
        return pd.DataFrame()
    
    if df.empty:
        print(f"⚠️ Aucune donnée reçue pour {ticker}")
        return pd.DataFrame()
    
    print(f"✅ {len(df)} lignes téléchargées pour {ticker}")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    
    df.columns = df.columns.str.lower()
    
    df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    }, inplace=True)

    # Calculer les indicateurs avec la config
    df_with_indicators = calculate_all_indicators(df.copy(), config=config)
    
    df_with_indicators.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)
    
    df_with_indicators['asset_id'] = asset_id
    df_with_indicators.reset_index(inplace=True)
    df_with_indicators['date'] = df_with_indicators['Date'].dt.strftime('%Y-%m-%d')
    
    if not return_full:
        end_date = df_with_indicators['Date'].max()
        requested_days = period_to_days(period)
        start_date = end_date - pd.Timedelta(days=requested_days)
        df_filtered = df_with_indicators[df_with_indicators['Date'] >= start_date].copy()
        return df_filtered
    
    return df_with_indicators


def save_indicators_to_db(df_today):
    """Sauvegarde les indicateurs calculés pour un jour donné dans la base de données PostgreSQL."""
    try:
        from db_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        columns_to_save = [
            'asset_id', 'date', 'open', 'high', 'low', 'close', 'volume',
            'stochastic_k', 'stochastic_d', 'rsi', 'pattern', 'recommendation', 'conviction'
        ]
        
        for col in columns_to_save:
            if col not in df_today.columns:
                df_today[col] = None
                
        df_to_save = df_today[columns_to_save].copy()
        df_to_save = df_to_save.where(pd.notna(df_to_save), None)

        for _, row in df_to_save.iterrows():
            cursor.execute('''
                INSERT INTO historical_data 
                (asset_id, date, open, high, low, close, volume, stochastic_k, stochastic_d, rsi, pattern, recommendation, conviction)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (asset_id, date) 
                DO UPDATE SET 
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume,
                    stochastic_k = EXCLUDED.stochastic_k,
                    stochastic_d = EXCLUDED.stochastic_d,
                    rsi = EXCLUDED.rsi,
                    pattern = EXCLUDED.pattern,
                    recommendation = EXCLUDED.recommendation,
                    conviction = EXCLUDED.conviction
            ''', tuple(row))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Données sauvegardées pour {len(df_to_save)} lignes.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")