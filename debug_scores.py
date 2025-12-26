# debug_scores.py
"""
Diagnostic des scores - comprendre pourquoi tous les scores sont non-zéro
"""
import pandas as pd
from data_handler import fetch_and_prepare_data
from config import get_default_config
from indicator_performance import (
    calculate_performance_history_with_combinations,
    _normalize_column_names
)

def run_diagnostic():
    print("="*80)
    print("DIAGNOSTIC DES SCORES")
    print("="*80)
    
    config = get_default_config()
    df = fetch_and_prepare_data("AAPL", period="1y", config=config)
    df['Date'] = pd.to_datetime(df['Date'])
    
    horizons = [1, 2, 5, 10, 20]
    all_perf = calculate_performance_history_with_combinations(df, config, horizons)
    
    # Prendre une combinaison avec peu de signaux pour analyser
    combo_key = "🟢 RSI Sortie Survente + Stoch"
    
    if combo_key not in all_perf:
        print(f"❌ Combinaison '{combo_key}' non trouvée")
        print(f"Clés disponibles: {list(all_perf.keys())}")
        return
    
    perf_df = all_perf[combo_key]
    
    print(f"\nAnalyse de: {combo_key}")
    print(f"Nombre total de lignes: {len(perf_df)}")
    print(f"\nColonnes: {list(perf_df.columns)}")
    
    print(f"\n--- Distribution des signaux ---")
    print(perf_df['signal'].value_counts())
    
    print(f"\n--- Distribution des intensités ---")
    print(f"Intensités uniques: {perf_df['intensity'].unique()}")
    print(f"Intensités > 0: {(perf_df['intensity'] > 0).sum()}")
    print(f"Intensités == 0: {(perf_df['intensity'] == 0).sum()}")
    
    print(f"\n--- Scores pour horizon 1 jour ---")
    if 'score_1d' in perf_df.columns:
        print(f"Scores uniques (premiers 20): {perf_df['score_1d'].unique()[:20]}")
        print(f"Scores == 0: {(perf_df['score_1d'] == 0).sum()}")
        print(f"Scores != 0: {(perf_df['score_1d'] != 0).sum()}")
        print(f"Scores NaN: {perf_df['score_1d'].isna().sum()}")
    
    print(f"\n--- Échantillon des données (lignes avec signal != neutral) ---")
    signals_df = perf_df[perf_df['signal'] != 'neutral']
    print(f"Nombre de signaux non-neutres: {len(signals_df)}")
    if len(signals_df) > 0:
        print(signals_df[['Date', 'signal', 'intensity', 'score_1d', 'score_5d']].head(10))
    
    print(f"\n--- Échantillon des données (lignes avec signal == neutral) ---")
    neutral_df = perf_df[perf_df['signal'] == 'neutral']
    print(f"Nombre de signaux neutres: {len(neutral_df)}")
    if len(neutral_df) > 0:
        print(neutral_df[['Date', 'signal', 'intensity', 'score_1d', 'score_5d']].head(10))
    
    print("\n" + "="*80)

if __name__ == "__main__":
    run_diagnostic()