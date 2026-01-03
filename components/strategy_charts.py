# components/strategy_charts.py
"""
Graphiques pour les stratégies de trading.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np

# Couleurs pour chaque période de holding
HOLDING_COLORS = {
    1: '#00bfff',   # Bleu clair
    2: '#ffa500',   # Orange
    5: '#26a69a',   # Vert
    10: '#9932cc',  # Violet
    20: '#ff6347',  # Rouge tomate
}


def create_hold_and_sell_chart(strategy_results, asset_name, df_prices):
    """
    Crée le graphique pour la stratégie Hold & Sell on RSI Divergence.
    
    Affiche:
    - Courbe d'équité pour chaque période de holding
    - Courbe Buy & Hold pour comparaison
    - Points de vente (divergence baissière)
    - Points de rachat
    """
    if not strategy_results:
        return html.P("Aucune donnée de stratégie disponible.", className="text-muted")
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=("Évolution du Capital", "Prix de l'actif")
    )
    
    # Ajouter le Buy & Hold comme référence
    first_key = list(strategy_results.keys())[0]
    equity_df = strategy_results[first_key]['equity_curve']
    
    # Normaliser le prix pour la comparaison (base 100)
    if not equity_df.empty:
        initial_price = equity_df.iloc[0]['close']
        buy_hold_curve = (equity_df['close'] / initial_price) * 100
        
        fig.add_trace(go.Scatter(
            x=equity_df['Date'],
            y=buy_hold_curve,
            mode='lines',
            name='Buy & Hold',
            line=dict(color='white', width=2, dash='dash'),
            opacity=0.7
        ), row=1, col=1)
    
    # Ajouter les courbes d'équité pour chaque période
    for hold_days, data in strategy_results.items():
        equity_df = data['equity_curve']
        color = HOLDING_COLORS.get(hold_days, '#ffffff')
        
        fig.add_trace(go.Scatter(
            x=equity_df['Date'],
            y=equity_df['portfolio_value'],
            mode='lines',
            name=f'{hold_days}j (rebuy)',
            line=dict(color=color, width=2),
            hovertemplate=(
                f"<b>{hold_days} jours</b><br>"
                "Date: %{x}<br>"
                "Capital: %{y:.2f}<br>"
                "<extra></extra>"
            )
        ), row=1, col=1)
        
        # Ajouter les points de trade
        trades = data['trades']
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        buy_trades = [t for t in trades if t['type'] == 'BUY' and t['reason'] != 'Initial buy']
        
        if sell_trades:
            sell_dates = [t['date'] for t in sell_trades]
            sell_values = []
            for sd in sell_dates:
                idx = equity_df[equity_df['Date'] == sd].index
                if len(idx) > 0:
                    sell_values.append(equity_df.loc[idx[0], 'portfolio_value'])
                else:
                    sell_values.append(None)
            
            fig.add_trace(go.Scatter(
                x=sell_dates,
                y=sell_values,
                mode='markers',
                name=f'Ventes ({hold_days}j)',
                marker=dict(symbol='triangle-down', size=10, color='#ef5350'),
                showlegend=False,
                hovertemplate="VENTE<br>Date: %{x}<br><extra></extra>"
            ), row=1, col=1)
    
    # Graphique des prix en bas
    fig.add_trace(go.Scatter(
        x=equity_df['Date'],
        y=equity_df['close'],
        mode='lines',
        name='Prix',
        line=dict(color='#888888', width=1),
        showlegend=False
    ), row=2, col=1)
    
    # Marquer les divergences baissières sur le prix
    if not df_prices.empty and 'rsi_divergence' in df_prices.columns:
        bearish_div = df_prices[df_prices['rsi_divergence'] == 'bearish']
        if not bearish_div.empty:
            fig.add_trace(go.Scatter(
                x=bearish_div['Date'],
                y=bearish_div['close'],
                mode='markers',
                name='Div. Baissière',
                marker=dict(symbol='triangle-down', size=12, color='#ef5350', line=dict(width=1, color='white')),
            ), row=2, col=1)
    
    fig.update_layout(
        template='plotly_dark',
        height=500,
        title=dict(
            text=f"📈 Stratégie Hold & Sell — {asset_name}",
            font=dict(size=14)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=50, t=80, b=30),
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Capital (base 100)", row=1, col=1)
    fig.update_yaxes(title_text="Prix", row=2, col=1)
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'scrollZoom': True})


def create_buy_on_divergence_chart(strategy_results, asset_name, df_prices):
    """
    Crée le graphique pour la stratégie Buy on RSI Bullish Divergence.
    
    Affiche:
    - Courbe d'équité pour chaque période de holding
    - Points d'achat (divergence haussière)
    - Points de vente automatique
    """
    if not strategy_results:
        return html.P("Aucune donnée de stratégie disponible.", className="text-muted")
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=("Évolution du Capital (achats sur divergence haussière)", "Prix de l'actif")
    )
    
    # Référence: rester en cash (ligne à 100)
    first_key = list(strategy_results.keys())[0]
    equity_df = strategy_results[first_key]['equity_curve']
    
    fig.add_trace(go.Scatter(
        x=equity_df['Date'],
        y=[100] * len(equity_df),
        mode='lines',
        name='Cash (référence)',
        line=dict(color='white', width=1, dash='dot'),
        opacity=0.5
    ), row=1, col=1)
    
    # Ajouter les courbes d'équité pour chaque période
    for hold_days, data in strategy_results.items():
        equity_df = data['equity_curve']
        color = HOLDING_COLORS.get(hold_days, '#ffffff')
        
        fig.add_trace(go.Scatter(
            x=equity_df['Date'],
            y=equity_df['portfolio_value'],
            mode='lines',
            name=f'{hold_days}j (hold)',
            line=dict(color=color, width=2),
            hovertemplate=(
                f"<b>{hold_days} jours</b><br>"
                "Date: %{x}<br>"
                "Capital: %{y:.2f}<br>"
                "<extra></extra>"
            )
        ), row=1, col=1)
        
        # Points d'achat
        trades = data['trades']
        buy_trades = [t for t in trades if t['type'] == 'BUY']
        
        if buy_trades:
            buy_dates = [t['date'] for t in buy_trades]
            buy_values = []
            for bd in buy_dates:
                idx = equity_df[equity_df['Date'] == bd].index
                if len(idx) > 0:
                    buy_values.append(equity_df.loc[idx[0], 'portfolio_value'])
                else:
                    buy_values.append(None)
            
            fig.add_trace(go.Scatter(
                x=buy_dates,
                y=buy_values,
                mode='markers',
                name=f'Achats ({hold_days}j)',
                marker=dict(symbol='triangle-up', size=10, color='#26a69a'),
                showlegend=False,
                hovertemplate="ACHAT<br>Date: %{x}<br><extra></extra>"
            ), row=1, col=1)
    
    # Graphique des prix en bas
    fig.add_trace(go.Scatter(
        x=equity_df['Date'],
        y=equity_df['close'],
        mode='lines',
        name='Prix',
        line=dict(color='#888888', width=1),
        showlegend=False
    ), row=2, col=1)
    
    # Marquer les divergences haussières sur le prix
    if not df_prices.empty and 'rsi_divergence' in df_prices.columns:
        bullish_div = df_prices[df_prices['rsi_divergence'] == 'bullish']
        if not bullish_div.empty:
            fig.add_trace(go.Scatter(
                x=bullish_div['Date'],
                y=bullish_div['close'],
                mode='markers',
                name='Div. Haussière',
                marker=dict(symbol='triangle-up', size=12, color='#26a69a', line=dict(width=1, color='white')),
            ), row=2, col=1)
    
    fig.update_layout(
        template='plotly_dark',
        height=500,
        title=dict(
            text=f"📊 Stratégie Buy on Divergence — {asset_name}",
            font=dict(size=14)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        margin=dict(l=50, r=50, t=80, b=30),
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Capital (base 100)", row=1, col=1)
    fig.update_yaxes(title_text="Prix", row=2, col=1)
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'scrollZoom': True})


def create_strategy_stats_table(strategy_results, strategy_type='hold_and_sell'):
    """
    Crée un tableau de statistiques pour une stratégie.
    """
    if not strategy_results:
        return html.P("Aucune donnée disponible.", className="text-muted")
    
    rows = []
    
    for hold_days in sorted(strategy_results.keys()):
        data = strategy_results[hold_days]
        stats = data['stats']
        
        # Couleur selon la performance
        ret = stats['total_return']
        outperf = stats['outperformance']
        
        ret_color = '#26a69a' if ret > 0 else '#ef5350'
        outperf_color = '#26a69a' if outperf > 0 else '#ef5350' if outperf < 0 else '#6c757d'
        
        if strategy_type == 'buy_on_divergence':
            # Colonnes spécifiques pour buy on divergence
            win_rate = stats.get('win_rate', 0)
            wr_color = '#26a69a' if win_rate >= 50 else '#ef5350'
            
            row = html.Tr([
                html.Td(f"{hold_days} jours", style={'fontWeight': 'bold'}),
                html.Td(f"{ret:+.2f}%", style={'color': ret_color, 'fontWeight': 'bold'}),
                html.Td(f"{stats['buy_hold_return']:.2f}%"),
                html.Td(f"{outperf:+.2f}%", style={'color': outperf_color, 'fontWeight': 'bold'}),
                html.Td(str(stats.get('num_trades', 0))),
                html.Td(f"{win_rate:.0f}%", style={'color': wr_color}),
                html.Td(f"{stats.get('avg_win', 0):+.2f}%", style={'color': '#26a69a'}),
                html.Td(f"{stats.get('avg_loss', 0):+.2f}%", style={'color': '#ef5350'}),
            ])
        else:
            # Colonnes pour hold & sell
            row = html.Tr([
                html.Td(f"{hold_days} jours", style={'fontWeight': 'bold'}),
                html.Td(f"{ret:+.2f}%", style={'color': ret_color, 'fontWeight': 'bold'}),
                html.Td(f"{stats['buy_hold_return']:.2f}%"),
                html.Td(f"{outperf:+.2f}%", style={'color': outperf_color, 'fontWeight': 'bold'}),
                html.Td(str(stats.get('num_sells', 0))),
                html.Td(str(stats.get('num_buys', 0))),
            ])
        
        rows.append(row)
    
    if strategy_type == 'buy_on_divergence':
        header = html.Thead(html.Tr([
            html.Th("Période"),
            html.Th("Rendement"),
            html.Th("Buy&Hold"),
            html.Th("Surperf."),
            html.Th("Trades"),
            html.Th("Win Rate"),
            html.Th("Gain Moy."),
            html.Th("Perte Moy."),
        ]))
    else:
        header = html.Thead(html.Tr([
            html.Th("Période Rebuy"),
            html.Th("Rendement"),
            html.Th("Buy&Hold"),
            html.Th("Surperf."),
            html.Th("Ventes"),
            html.Th("Rachats"),
        ]))
    
    return dbc.Table([header, html.Tbody(rows)], 
                     bordered=True, color="dark", hover=True, size="sm", responsive=True)


def create_strategies_section(df, asset_name, spread_pct=0.5):
    """
    Crée la section complète des stratégies de trading.
    """
    from trading_strategies import create_strategy_comparison_data
    
    if df.empty:
        return html.P("Aucune donnée disponible pour les simulations.", className="text-muted")
    
    # Calculer les stratégies
    results = create_strategy_comparison_data(df, spread_pct)
    
    hold_sell_results = results['hold_and_sell']
    buy_div_results = results['buy_on_divergence']
    buy_hold_return = results['buy_hold_return']
    
    # Vérifier s'il y a des divergences
    num_bullish = len(df[df['rsi_divergence'] == 'bullish']) if 'rsi_divergence' in df.columns else 0
    num_bearish = len(df[df['rsi_divergence'] == 'bearish']) if 'rsi_divergence' in df.columns else 0
    
    content = html.Div([
        # En-tête avec résumé
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📊 Période d'analyse", className="text-muted mb-1"),
                        html.P(f"{len(df)} jours", className="mb-0 h5"),
                    ])
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📈 Buy & Hold", className="text-muted mb-1"),
                        html.P(f"{buy_hold_return:+.2f}%", 
                               className="mb-0 h5",
                               style={'color': '#26a69a' if buy_hold_return > 0 else '#ef5350'}),
                    ])
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🔴 Div. Baissières", className="text-muted mb-1"),
                        html.P(f"{num_bearish} signaux", className="mb-0 h5"),
                    ])
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🟢 Div. Haussières", className="text-muted mb-1"),
                        html.P(f"{num_bullish} signaux", className="mb-0 h5"),
                    ])
                ], color="dark", outline=True)
            ], width=2),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("💰 Spread utilisé", className="text-muted mb-1"),
                        html.P(f"{spread_pct}%", className="mb-0 h5"),
                    ])
                ], color="dark", outline=True)
            ], width=2),
        ], className="mb-4"),
        
        # === STRATÉGIE 1: HOLD & SELL ===
        html.Hr(),
        html.H5("📈 Stratégie 1: Hold & Sell on RSI Divergence", className="mb-2"),
        html.P([
            "Cette stratégie est adaptée aux actifs que vous souhaitez ",
            html.Strong("garder en portefeuille à long terme"),
            " (ex: ETF S&P500, actions de qualité). ",
            "Elle achète au début de la période, vend sur divergence baissière RSI, ",
            "puis rachète automatiquement après N jours."
        ], className="text-muted small mb-3"),
        
        dbc.Row([
            dbc.Col([
                create_hold_and_sell_chart(hold_sell_results, asset_name, df)
            ], width=8),
            dbc.Col([
                html.H6("📊 Statistiques", className="mb-2"),
                create_strategy_stats_table(hold_sell_results, 'hold_and_sell')
            ], width=4),
        ], className="mb-4"),
        
        # === STRATÉGIE 2: BUY ON DIVERGENCE ===
        html.Hr(),
        html.H5("📊 Stratégie 2: Buy on RSI Bullish Divergence", className="mb-2"),
        html.P([
            "Cette stratégie est adaptée aux actifs sur lesquels vous avez ",
            html.Strong("plus de doutes"),
            " (ex: actions spéculatives, crypto). ",
            "Elle n'achète ",
            html.Strong("que sur signal de divergence haussière RSI"),
            " et revend automatiquement après N jours. ",
            html.Em("Pas de vente à découvert.")
        ], className="text-muted small mb-3"),
        
        dbc.Row([
            dbc.Col([
                create_buy_on_divergence_chart(buy_div_results, asset_name, df)
            ], width=8),
            dbc.Col([
                html.H6("📊 Statistiques", className="mb-2"),
                create_strategy_stats_table(buy_div_results, 'buy_on_divergence')
            ], width=4),
        ]),
    ])
    
    return content