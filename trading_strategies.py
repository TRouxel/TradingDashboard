# trading_strategies.py
"""
Module de simulation de stratégies de trading basées sur la divergence RSI.
VERSION 1.0

Deux stratégies:
1. Hold & Sell on RSI Divergence: Achète au début, vend sur divergence baissière, rachète N jours après
2. Buy on RSI Divergence: N'achète que sur divergence haussière, revend N jours après
"""
import pandas as pd
import numpy as np
from datetime import timedelta


def simulate_hold_and_sell_strategy(df, holding_periods=[1, 2, 5, 10, 20], spread_pct=0.5):
    """
    Stratégie 1: Hold & Sell on RSI Divergence
    
    - Achète au début de la période (peu importe les indicateurs)
    - Vend quand la divergence RSI baissière apparaît
    - Rachète N jours plus tard
    - Le spread (coût de transaction) est appliqué à chaque achat/vente
    
    Args:
        df: DataFrame avec les données et indicateurs (doit contenir 'rsi_divergence', 'close', 'Date')
        holding_periods: Liste des périodes de rachat après vente (en jours)
        spread_pct: Écart achat/vente en % du prix (coût de transaction)
    
    Returns:
        dict: Résultats pour chaque période de holding
            - 'equity_curve': Courbe de capital pour chaque période
            - 'trades': Liste des trades effectués
            - 'stats': Statistiques de performance
    """
    if df.empty or 'rsi_divergence' not in df.columns:
        return {}
    
    df = df.copy()
    df = df.sort_values('Date').reset_index(drop=True)
    
    # S'assurer que 'close' existe
    if 'close' not in df.columns and 'Close' in df.columns:
        df['close'] = df['Close']
    
    results = {}
    
    for hold_days in holding_periods:
        equity_curve = []
        trades = []
        
        # Capital initial normalisé à 100
        capital = 100.0
        position = 0  # Nombre d'unités détenues
        in_position = False
        waiting_to_rebuy = False
        rebuy_date = None
        entry_price = None
        
        # Prix d'achat initial (premier jour)
        initial_price = df.iloc[0]['close']
        spread_amount = initial_price * (spread_pct / 100)
        
        # Acheter au début
        entry_price = initial_price + spread_amount / 2  # Prix d'achat légèrement plus haut
        position = capital / entry_price
        in_position = True
        capital = 0
        
        trades.append({
            'date': df.iloc[0]['Date'],
            'type': 'BUY',
            'price': entry_price,
            'units': position,
            'reason': 'Initial buy'
        })
        
        for idx in range(len(df)):
            row = df.iloc[idx]
            current_date = row['Date']
            current_price = row['close']
            rsi_div = row.get('rsi_divergence', 'none')
            
            # Calculer la valeur actuelle du portefeuille
            if in_position:
                portfolio_value = position * current_price
            else:
                portfolio_value = capital
            
            # Vérifier si on doit racheter
            if waiting_to_rebuy and rebuy_date is not None:
                if current_date >= rebuy_date:
                    # Racheter
                    buy_price = current_price + (current_price * spread_pct / 100) / 2
                    position = capital / buy_price
                    in_position = True
                    capital = 0
                    waiting_to_rebuy = False
                    rebuy_date = None
                    
                    trades.append({
                        'date': current_date,
                        'type': 'BUY',
                        'price': buy_price,
                        'units': position,
                        'reason': f'Rebuy after {hold_days} days'
                    })
            
            # Vérifier si divergence baissière (signal de vente)
            if in_position and rsi_div == 'bearish':
                # Vendre
                sell_price = current_price - (current_price * spread_pct / 100) / 2
                capital = position * sell_price
                
                trades.append({
                    'date': current_date,
                    'type': 'SELL',
                    'price': sell_price,
                    'units': position,
                    'reason': 'RSI bearish divergence'
                })
                
                position = 0
                in_position = False
                waiting_to_rebuy = True
                
                # Calculer la date de rachat
                rebuy_date = current_date + timedelta(days=hold_days)
            
            # Enregistrer la valeur du portefeuille
            if in_position:
                portfolio_value = position * current_price
            else:
                portfolio_value = capital
            
            equity_curve.append({
                'Date': current_date,
                'portfolio_value': portfolio_value,
                'in_position': in_position,
                'close': current_price
            })
        
        # Calculer le buy & hold pour comparaison
        buy_hold_return = (df.iloc[-1]['close'] / df.iloc[0]['close'] - 1) * 100
        
        # Statistiques
        equity_df = pd.DataFrame(equity_curve)
        final_value = equity_df.iloc[-1]['portfolio_value']
        total_return = (final_value / 100 - 1) * 100
        
        # Nombre de trades
        num_sells = len([t for t in trades if t['type'] == 'SELL'])
        num_buys = len([t for t in trades if t['type'] == 'BUY'])
        
        results[hold_days] = {
            'equity_curve': equity_df,
            'trades': trades,
            'stats': {
                'total_return': total_return,
                'buy_hold_return': buy_hold_return,
                'outperformance': total_return - buy_hold_return,
                'num_sells': num_sells,
                'num_buys': num_buys,
                'final_value': final_value
            }
        }
    
    return results


def simulate_buy_on_divergence_strategy(df, holding_periods=[1, 2, 5, 10, 20], spread_pct=0.5):
    """
    Stratégie 2: Buy on RSI Bullish Divergence
    
    - N'achète que quand une divergence RSI haussière apparaît
    - Revend automatiquement N jours plus tard
    - Pas de vente à découvert (short)
    - Le spread (coût de transaction) est appliqué à chaque achat/vente
    
    Args:
        df: DataFrame avec les données et indicateurs
        holding_periods: Liste des périodes de détention après achat (en jours)
        spread_pct: Écart achat/vente en % du prix
    
    Returns:
        dict: Résultats pour chaque période de holding
    """
    if df.empty or 'rsi_divergence' not in df.columns:
        return {}
    
    df = df.copy()
    df = df.sort_values('Date').reset_index(drop=True)
    
    if 'close' not in df.columns and 'Close' in df.columns:
        df['close'] = df['Close']
    
    results = {}
    
    for hold_days in holding_periods:
        equity_curve = []
        trades = []
        
        # Capital initial normalisé à 100
        capital = 100.0
        position = 0
        in_position = False
        sell_date = None
        entry_price = None
        
        for idx in range(len(df)):
            row = df.iloc[idx]
            current_date = row['Date']
            current_price = row['close']
            rsi_div = row.get('rsi_divergence', 'none')
            
            # Vérifier si on doit vendre
            if in_position and sell_date is not None:
                if current_date >= sell_date:
                    # Vendre
                    sell_price = current_price - (current_price * spread_pct / 100) / 2
                    capital = position * sell_price
                    
                    # Calculer le profit/perte
                    pnl = (sell_price / entry_price - 1) * 100
                    
                    trades.append({
                        'date': current_date,
                        'type': 'SELL',
                        'price': sell_price,
                        'units': position,
                        'pnl_pct': pnl,
                        'reason': f'Auto-sell after {hold_days} days'
                    })
                    
                    position = 0
                    in_position = False
                    sell_date = None
                    entry_price = None
            
            # Vérifier si divergence haussière (signal d'achat)
            if not in_position and rsi_div == 'bullish':
                # Acheter
                buy_price = current_price + (current_price * spread_pct / 100) / 2
                position = capital / buy_price
                entry_price = buy_price
                in_position = True
                capital = 0
                
                # Calculer la date de vente
                sell_date = current_date + timedelta(days=hold_days)
                
                trades.append({
                    'date': current_date,
                    'type': 'BUY',
                    'price': buy_price,
                    'units': position,
                    'reason': 'RSI bullish divergence'
                })
            
            # Calculer la valeur du portefeuille
            if in_position:
                portfolio_value = position * current_price
            else:
                portfolio_value = capital
            
            equity_curve.append({
                'Date': current_date,
                'portfolio_value': portfolio_value,
                'in_position': in_position,
                'close': current_price
            })
        
        # Si encore en position à la fin, vendre
        if in_position:
            final_price = df.iloc[-1]['close']
            sell_price = final_price - (final_price * spread_pct / 100) / 2
            capital = position * sell_price
            pnl = (sell_price / entry_price - 1) * 100
            
            trades.append({
                'date': df.iloc[-1]['Date'],
                'type': 'SELL',
                'price': sell_price,
                'units': position,
                'pnl_pct': pnl,
                'reason': 'End of period'
            })
        
        # Statistiques
        equity_df = pd.DataFrame(equity_curve)
        final_value = equity_df.iloc[-1]['portfolio_value']
        total_return = (final_value / 100 - 1) * 100
        
        # Buy & hold pour comparaison
        buy_hold_return = (df.iloc[-1]['close'] / df.iloc[0]['close'] - 1) * 100
        
        # Calculer les stats des trades
        winning_trades = [t for t in trades if t['type'] == 'SELL' and t.get('pnl_pct', 0) > 0]
        losing_trades = [t for t in trades if t['type'] == 'SELL' and t.get('pnl_pct', 0) <= 0]
        all_sell_trades = [t for t in trades if t['type'] == 'SELL']
        
        win_rate = len(winning_trades) / len(all_sell_trades) * 100 if all_sell_trades else 0
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        results[hold_days] = {
            'equity_curve': equity_df,
            'trades': trades,
            'stats': {
                'total_return': total_return,
                'buy_hold_return': buy_hold_return,
                'outperformance': total_return - buy_hold_return,
                'num_trades': len(all_sell_trades),
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'final_value': final_value
            }
        }
    
    return results


def create_strategy_comparison_data(df, spread_pct=0.5, holding_periods=[1, 2, 5, 10, 20]):
    """
    Crée les données de comparaison pour les deux stratégies.
    
    Returns:
        dict: {
            'hold_and_sell': résultats stratégie 1,
            'buy_on_divergence': résultats stratégie 2,
            'buy_hold': rendement buy & hold
        }
    """
    hold_sell_results = simulate_hold_and_sell_strategy(df, holding_periods, spread_pct)
    buy_div_results = simulate_buy_on_divergence_strategy(df, holding_periods, spread_pct)
    
    # Buy & hold simple
    if not df.empty and 'close' in df.columns:
        buy_hold_return = (df.iloc[-1]['close'] / df.iloc[0]['close'] - 1) * 100
    else:
        buy_hold_return = 0
    
    return {
        'hold_and_sell': hold_sell_results,
        'buy_on_divergence': buy_div_results,
        'buy_hold_return': buy_hold_return
    }


def calculate_strategy_summary(strategy_results, strategy_type='hold_and_sell'):
    """
    Calcule un résumé des performances d'une stratégie.
    
    Args:
        strategy_results: Résultats d'une stratégie (dict par période)
        strategy_type: 'hold_and_sell' ou 'buy_on_divergence'
    
    Returns:
        pd.DataFrame: Tableau récapitulatif
    """
    summary = []
    
    for hold_days, data in strategy_results.items():
        stats = data['stats']
        
        row = {
            'holding_days': hold_days,
            'total_return': stats['total_return'],
            'buy_hold_return': stats['buy_hold_return'],
            'outperformance': stats['outperformance'],
            'final_value': stats['final_value']
        }
        
        if strategy_type == 'buy_on_divergence':
            row['num_trades'] = stats.get('num_trades', 0)
            row['win_rate'] = stats.get('win_rate', 0)
            row['avg_win'] = stats.get('avg_win', 0)
            row['avg_loss'] = stats.get('avg_loss', 0)
        else:
            row['num_sells'] = stats.get('num_sells', 0)
            row['num_buys'] = stats.get('num_buys', 0)
        
        summary.append(row)
    
    return pd.DataFrame(summary)