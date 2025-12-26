# debug_combinations.py
"""
Script de diagnostic pour comprendre pourquoi les combinaisons sont vides.
À exécuter séparément : python debug_combinations.py
"""
import pandas as pd
import sys

# Importer les modules de l'application
from data_handler import fetch_and_prepare_data
from config import get_default_config
from indicator_performance import (
    calculate_performance_history,
    calculate_performance_history_with_combinations,
    analyze_signal_combinations,
    _normalize_column_names,
    COMBINATION_DEFINITIONS,
    _safe_get,
    _safe_get_numeric
)

def run_diagnostic(ticker="AAPL", period="1y"):
    """Diagnostic complet des combinaisons."""
    
    print("="*80)
    print(f"DIAGNOSTIC DES COMBINAISONS - {ticker}")
    print("="*80)
    
    # 1. Charger les données
    print("\n[1] Chargement des données...")
    config = get_default_config()
    df = fetch_and_prepare_data(ticker, period=period, config=config)
    
    if df.empty:
        print("❌ ERREUR: DataFrame vide!")
        return
    
    print(f"✓ {len(df)} lignes chargées")
    print(f"✓ Colonnes: {list(df.columns)[:20]}...")
    
    # 2. Vérifier les colonnes nécessaires
    print("\n[2] Vérification des colonnes nécessaires...")
    required_cols = ['rsi', 'stochastic_k', 'stochastic_d', 'macd', 'macd_signal', 
                     'macd_histogram', 'trend', 'bb_signal', 'pattern_direction',
                     'rsi_divergence', 'adx', 'di_plus', 'di_minus', 'sma_20', 'sma_50']
    
    for col in required_cols:
        if col in df.columns:
            non_null = df[col].notna().sum()
            print(f"  ✓ {col}: {non_null}/{len(df)} valeurs non-nulles")
        else:
            # Vérifier avec majuscule
            col_upper = col[0].upper() + col[1:] if col else col
            if col_upper in df.columns:
                print(f"  ⚠ {col} trouvé comme {col_upper}")
            else:
                print(f"  ❌ {col}: MANQUANT!")
    
    # 3. Normaliser et préparer comme dans le vrai code
    print("\n[3] Normalisation des colonnes...")
    df['Date'] = pd.to_datetime(df['Date'])
    df_norm = _normalize_column_names(df.copy())
    print(f"✓ Colonnes après normalisation: {list(df_norm.columns)[:20]}...")
    
    # 4. Tester chaque combinaison manuellement
    print("\n[4] Test de chaque combinaison...")
    print("-"*80)
    
    for combo_def in COMBINATION_DEFINITIONS:
        combo_name = combo_def['name']
        combo_type = combo_def['type']
        check_func = combo_def['check']
        
        signal_count = 0
        errors = []
        
        for idx in range(len(df_norm)):
            row = df_norm.iloc[idx]
            row_dict = row.to_dict()
            row_prev_dict = df_norm.iloc[idx - 1].to_dict() if idx > 0 else None
            
            try:
                result = check_func(row_dict, row_prev_dict, config)
                if result:
                    signal_count += 1
            except Exception as e:
                if str(e) not in [str(err) for err in errors]:
                    errors.append(e)
        
        emoji = "🟢" if combo_type == 'buy' else "🔴"
        status = f"{signal_count} signaux" if signal_count > 0 else "❌ VIDE"
        error_info = f" | Erreurs: {errors[:2]}" if errors else ""
        print(f"{emoji} {combo_name}: {status}{error_info}")
    
    # 5. Tester analyze_signal_combinations
    print("\n[5] Test de analyze_signal_combinations()...")
    horizons = [1, 2, 5, 10, 20]
    
    try:
        combo_results = analyze_signal_combinations(df_norm, config, horizons)
        print(f"✓ Résultat: {len(combo_results)} combinaisons retournées")
        
        for name, data in combo_results.items():
            perf_df = data['df']
            combo_type = data['type']
            signal_count = data.get('signal_count', 'N/A')
            
            # Compter les signaux non-neutres dans le DataFrame
            non_neutral = len(perf_df[perf_df['signal'] != 'neutral'])
            
            # Compter les scores non-zéro
            score_cols = [f'score_{h}d' for h in horizons if f'score_{h}d' in perf_df.columns]
            non_zero_scores = 0
            for col in score_cols:
                non_zero_scores += (perf_df[col] != 0).sum()
            
            print(f"  {name}: signal_count={signal_count}, non_neutral={non_neutral}, non_zero_scores={non_zero_scores}")
            
    except Exception as e:
        print(f"❌ ERREUR dans analyze_signal_combinations: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Tester calculate_performance_history_with_combinations
    print("\n[6] Test de calculate_performance_history_with_combinations()...")
    
    try:
        all_perf = calculate_performance_history_with_combinations(df_norm, config, horizons)
        print(f"✓ Résultat: {len(all_perf)} entrées")
        
        # Séparer par type
        individual = [k for k in all_perf.keys() if k.startswith('📊')]
        buy_combos = [k for k in all_perf.keys() if k.startswith('🟢')]
        sell_combos = [k for k in all_perf.keys() if k.startswith('🔴')]
        
        print(f"  Indicateurs individuels: {len(individual)}")
        print(f"  Combinaisons achat: {len(buy_combos)}")
        print(f"  Combinaisons vente: {len(sell_combos)}")
        
        # Détails sur les combinaisons
        print("\n  Détail des combinaisons:")
        for key in buy_combos + sell_combos:
            perf_df = all_perf[key]
            non_neutral = len(perf_df[perf_df['signal'] != 'neutral'])
            
            score_1d = perf_df['score_1d'] if 'score_1d' in perf_df.columns else None
            if score_1d is not None:
                non_zero = (score_1d != 0).sum()
            else:
                non_zero = 0
            
            print(f"    {key}: {non_neutral} signaux non-neutres, {non_zero} scores non-zéro")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. Vérifier un exemple concret
    print("\n[7] Exemple concret - dernières lignes avec RSI < 45 et Stoch haussier...")
    
    df_check = df_norm.copy()
    df_check['rsi_num'] = pd.to_numeric(df_check.get('rsi', 50), errors='coerce').fillna(50)
    df_check['stoch_k_num'] = pd.to_numeric(df_check.get('stochastic_k', 50), errors='coerce').fillna(50)
    df_check['stoch_d_num'] = pd.to_numeric(df_check.get('stochastic_d', 50), errors='coerce').fillna(50)
    
    condition = (df_check['rsi_num'] < 45) & (df_check['stoch_k_num'] > df_check['stoch_d_num'])
    matching = df_check[condition]
    
    print(f"  Jours avec RSI < 45 ET Stoch K > D: {len(matching)}")
    if len(matching) > 0:
        print(f"  Exemples:")
        for idx in matching.tail(3).index:
            row = df_check.loc[idx]
            print(f"    Date={row.get('Date', row.get('date', 'N/A'))}, RSI={row['rsi_num']:.1f}, K={row['stoch_k_num']:.1f}, D={row['stoch_d_num']:.1f}")
    
    print("\n" + "="*80)
    print("FIN DU DIAGNOSTIC")
    print("="*80)


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    run_diagnostic(ticker)