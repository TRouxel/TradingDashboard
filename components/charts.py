# components/charts.py
"""
Fonctions de création des graphiques Plotly.
"""
import plotly.graph_objects as go
from dash import dcc, html
import pandas as pd

from config import INDICATOR_DESCRIPTIONS


def create_price_chart(df_graph, selected_date, asset_name, show_ma, show_bb, config):
    """Crée le graphique principal des prix en chandeliers avec Bollinger optionnel."""
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df_graph['Date'], open=df_graph['open'], high=df_graph['high'],
        low=df_graph['low'], close=df_graph['close'], name='Prix',
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ))
    
    # Bandes de Bollinger (affichées en premier pour être en arrière-plan)
    if show_bb and 'bb_upper' in df_graph.columns and 'bb_lower' in df_graph.columns:
        # Bande supérieure
        fig.add_trace(go.Scatter(
            x=df_graph['Date'], y=df_graph['bb_upper'],
            mode='lines', name='BB Haute',
            line=dict(color='rgba(255, 165, 0, 0.6)', width=1),
            hovertemplate='BB Haute: %{y:.2f}<extra></extra>'
        ))
        # Bande inférieure avec remplissage vers la bande supérieure
        fig.add_trace(go.Scatter(
            x=df_graph['Date'], y=df_graph['bb_lower'],
            mode='lines', name='BB Basse',
            line=dict(color='rgba(255, 165, 0, 0.6)', width=1),
            fill='tonexty',
            fillcolor='rgba(255, 165, 0, 0.1)',
            hovertemplate='BB Basse: %{y:.2f}<extra></extra>'
        ))
        # Bande médiane (SMA 20)
        if 'bb_middle' in df_graph.columns:
            fig.add_trace(go.Scatter(
                x=df_graph['Date'], y=df_graph['bb_middle'],
                mode='lines', name='BB Milieu (SMA20)',
                line=dict(color='rgba(255, 165, 0, 0.8)', width=1, dash='dot'),
                hovertemplate='BB Milieu: %{y:.2f}<extra></extra>'
            ))
    
    # Moyennes mobiles
    if show_ma:
        ma_cfg = config.get('moving_averages', {})
        if 'sma_20' in df_graph.columns and not show_bb:  # Ne pas afficher SMA20 si BB est actif (BB middle = SMA20)
            fig.add_trace(go.Scatter(x=df_graph['Date'], y=df_graph['sma_20'],
                mode='lines', name=f"SMA {ma_cfg.get('sma_short', 20)}",
                line=dict(color='#00bfff', width=1.5), opacity=0.8))
        elif 'sma_20' in df_graph.columns and show_bb:
            pass  # SMA20 déjà affichée via BB middle
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
    if show_bb:
        desc += " + Bollinger"
    if show_ma:
        desc += " + MAs"
        
    fig.update_layout(
        title=dict(text=f'{asset_name} — {desc}', font=dict(size=14)),
        xaxis_rangeslider_visible=False, template='plotly_dark', showlegend=(show_ma or show_bb),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
        margin=dict(l=50, r=50, t=50, b=20)
    )
    return fig


def create_recommendations_chart(df_graph, selected_date):
    """Crée le graphique des recommandations achat/vente."""
    fig = go.Figure()
    conviction_values = []
    bar_colors = []
    hover_texts = []
    
    for _, row in df_graph.iterrows():
        trend = row.get('trend', 'neutral')
        bb_signal = row.get('bb_signal', 'neutral')
        if row['recommendation'] == 'Acheter':
            conviction_values.append(row['conviction'])
            bar_colors.append('#26a69a')
            hover_texts.append(f"ACHETER | Conv: {row['conviction']}/5 | Trend: {trend} | BB: {bb_signal}")
        elif row['recommendation'] == 'Vendre':
            conviction_values.append(-row['conviction'])
            bar_colors.append('#ef5350')
            hover_texts.append(f"VENDRE | Conv: {row['conviction']}/5 | Trend: {trend} | BB: {bb_signal}")
        else:
            conviction_values.append(0)
            bar_colors.append('rgba(128,128,128,0.3)')
            hover_texts.append(f"Neutre | Trend: {trend} | BB: {bb_signal}")
    
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
    """Crée le graphique de tendance ADX."""
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
    """Crée le graphique MACD."""
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
    """Crée le graphique de volume."""
    fig = go.Figure()
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df_graph['close'], df_graph['open'])]
    fig.add_trace(go.Bar(x=df_graph['Date'], y=df_graph['volume'], marker_color=colors, opacity=0.7))
    fig.add_vline(x=selected_date, line_width=2, line_dash="dash", line_color="cyan")
    fig.update_layout(template='plotly_dark', showlegend=False, margin=dict(l=50, r=50, t=10, b=20))
    return fig


def create_rsi_chart(df_graph, selected_date, config):
    """Crée le graphique RSI."""
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
    """Crée le graphique Stochastique."""
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
    """Crée le graphique des patterns de chandeliers."""
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