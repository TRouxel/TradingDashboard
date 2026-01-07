# callbacks/dashboard_callbacks.py
"""
Callbacks pour le dashboard principal et les graphiques.
"""
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import json

from data_handler import fetch_and_prepare_data, save_indicators_to_db
from config import INDICATOR_DESCRIPTIONS
from components import (
    create_price_chart, create_recommendations_chart, create_trend_chart,
    create_macd_chart, create_volume_chart, create_rsi_chart,
    create_stochastic_chart, create_patterns_chart,
    create_technical_indicators_table
)


def register_dashboard_callbacks(app):
    """Enregistre les callbacks du dashboard."""
    
    # === CALLBACK 1: Chargement initial des données ===
    # CORRECTION: Ajouter config-store comme Input pour recalculer quand la config change
    @app.callback(
        [Output('full-data-store', 'data'),
         Output('zoom-range-store', 'data', allow_duplicate=True)],
        [Input('asset-dropdown', 'value'),
         Input('period-dropdown', 'value'),
         Input('config-store', 'data')],  # <-- Ceci déclenche un recalcul quand la config change
        prevent_initial_call=True
    )
    def load_data(selected_asset, selected_period, config):
        if not selected_asset:
            return {}, None
        
        # DEBUG: Afficher la config reçue
        if config:
            dec_cfg = config.get('decision', {})
            ind_cfg = config.get('individual_weights', {})
            print(f"\n🔄 load_data appelé avec config:")
            print(f"   seuil = {dec_cfg.get('min_conviction_threshold')}")
            print(f"   min_combos = {dec_cfg.get('min_combinations_for_signal')}")
            print(f"   rsi_divergence = {ind_cfg.get('rsi_divergence')}")
        
        df = fetch_and_prepare_data(selected_asset, period=selected_period, config=config)
        if df.empty:
            return {}, None
        
        # Convertir en format JSON-serializable
        df['Date'] = df['Date'].astype(str)
        data = df.to_dict('records')
        
        return data, None
    
    # === CALLBACK 2: Mise à jour des graphiques ===
    @app.callback(
        [Output('main-charts-container', 'children'),
         Output('technical-charts-container', 'children')],
        [Input('full-data-store', 'data'),
         Input('date-picker', 'date'),
         Input('display-options', 'value'),
         Input('zoom-range-store', 'data')],
        [State('asset-dropdown', 'value'),
         State('config-store', 'data')]
    )
    def update_charts(data, selected_date_str, display_options, zoom_range, selected_asset, config):
        if not data or not selected_asset:
            return [], []
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        selected_date = pd.to_datetime(selected_date_str)
        df_graph = df[df['Date'] <= selected_date].copy()
        
        if df_graph.empty:
            return [dbc.Alert("Aucune donnée pour cette date", color="warning")], []
        
        # Appliquer le zoom si défini
        x_range = None
        if zoom_range:
            x_range = [zoom_range.get('start'), zoom_range.get('end')]
        
        # === GRAPHIQUES PRINCIPAUX ===
        main_charts = create_main_charts_with_zoom(
            df_graph, selected_date, selected_asset, display_options, config, x_range
        )
        
        # === GRAPHIQUES TECHNIQUES ===
        technical_charts = create_technical_charts_with_zoom(
            df_graph, selected_date, display_options, config, x_range
        )
        
        return main_charts, technical_charts
    
    # === CALLBACK 3: Mise à jour du header et tableau technique ===
    @app.callback(
        [Output('technical-summary-header', 'children'),
         Output('technical-indicators-table', 'children'),
         Output('technical-data-store', 'data'),
         Output('zoom-info', 'children')],
        [Input('full-data-store', 'data'),
         Input('date-picker', 'date'),
         Input('zoom-range-store', 'data')],
        [State('asset-dropdown', 'value'),
         State('config-store', 'data')]
    )
    def update_technical_summary(data, selected_date_str, zoom_range, selected_asset, config):
        if not data or not selected_asset:
            return [], [], {}, ""
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        selected_date = pd.to_datetime(selected_date_str)
        df_filtered = df[df['Date'] <= selected_date].copy()
        
        if df_filtered.empty:
            return [], [], {}, ""
        
        # Déterminer la date à afficher (fin du zoom ou date sélectionnée)
        zoom_info = ""
        if zoom_range and zoom_range.get('end'):
            zoom_end = pd.to_datetime(zoom_range['end'])
            zoom_start = pd.to_datetime(zoom_range['start']) if zoom_range.get('start') else None
            
            df_in_zoom = df_filtered[df_filtered['Date'] <= zoom_end]
            if zoom_start:
                df_in_zoom = df_in_zoom[df_in_zoom['Date'] >= zoom_start]
            
            if not df_in_zoom.empty:
                last_row = df_in_zoom.iloc[-1]
                start_str = zoom_start.strftime('%d/%m/%Y') if zoom_start else "..."
                end_str = zoom_end.strftime('%d/%m/%Y')
                zoom_info = f"🔍 Zoom actif: {start_str} → {end_str} | Données affichées au {last_row['Date'].strftime('%d/%m/%Y')}"
            else:
                last_row = df_filtered.iloc[-1]
        else:
            last_row = df_filtered.iloc[-1]
        
        # Header technique
        technical_header = create_technical_header(last_row, selected_asset)
        
        # Tableau des indicateurs
        indicators_table = create_technical_indicators_table(last_row.to_dict(), config)
        
        # Store data
        store_data = {k: (v.isoformat() if isinstance(v, pd.Timestamp) else v) 
                      for k, v in last_row.to_dict().items()}
        
        return technical_header, indicators_table, store_data, zoom_info
    
    # === CALLBACK 4: Capturer le zoom du graphique principal ===
    @app.callback(
        Output('zoom-range-store', 'data', allow_duplicate=True),
        [Input('price-chart', 'relayoutData'),
         Input('recommendations-chart', 'relayoutData'),
         Input('trend-chart', 'relayoutData'),
         Input('macd-chart', 'relayoutData'),
         Input('volume-chart', 'relayoutData'),
         Input('rsi-chart', 'relayoutData'),
         Input('stochastic-chart', 'relayoutData'),
         Input('patterns-chart', 'relayoutData'),
         Input('reset-zoom-btn', 'n_clicks')],
        [State('zoom-range-store', 'data')],
        prevent_initial_call=True
    )
    def sync_zoom(price_relay, reco_relay, trend_relay, macd_relay, 
                  volume_relay, rsi_relay, stoch_relay, patterns_relay,
                  reset_clicks, current_zoom):
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset zoom
        if triggered_id == 'reset-zoom-btn':
            return None
        
        # Trouver le relayoutData qui a déclenché le callback
        relay_data = None
        for relay in [price_relay, reco_relay, trend_relay, macd_relay, 
                      volume_relay, rsi_relay, stoch_relay, patterns_relay]:
            if relay:
                relay_data = relay
                break
        
        if not relay_data:
            raise PreventUpdate
        
        # Extraire la plage de zoom
        if 'xaxis.range[0]' in relay_data and 'xaxis.range[1]' in relay_data:
            return {
                'start': relay_data['xaxis.range[0]'],
                'end': relay_data['xaxis.range[1]']
            }
        elif 'xaxis.range' in relay_data:
            return {
                'start': relay_data['xaxis.range'][0],
                'end': relay_data['xaxis.range'][1]
            }
        elif 'xaxis.autorange' in relay_data:
            return None
        
        raise PreventUpdate
    
    # === CALLBACK 5: Sauvegarde ===
    @app.callback(
        Output('save-status', 'children'),
        Input('save-button', 'n_clicks'),
        [State('asset-dropdown', 'value'), 
         State('date-picker', 'date'), 
         State('config-store', 'data')],
        prevent_initial_call=True
    )
    def save_data_callback(n_clicks, selected_asset, selected_date_str, config):
        df = fetch_and_prepare_data(selected_asset, period="5y", config=config)
        df_today = df[df['date'] == selected_date_str].copy()

        if df_today.empty:
            return dbc.Alert(f"Aucune donnée pour {selected_asset} le {selected_date_str}.", 
                           color="warning", duration=4000)

        save_indicators_to_db(df_today)
        return dbc.Alert(f"✅ Indicateurs sauvegardés pour {selected_asset} le {selected_date_str}", 
                        color="success", duration=4000, dismissable=True)

def create_technical_header(last_row, selected_asset):
    """Crée le header avec les badges de recommandation et le prix avec bonne devise."""
    from config import get_asset_currency, get_currency_symbol
    
    recommendation = last_row.get('recommendation', 'Neutre')
    conviction = last_row.get('conviction', 0)
    trend = last_row.get('trend', 'neutral')
    close_price = last_row.get('close', 0)
    bb_signal = last_row.get('bb_signal', 'neutral')
    
    # Récupérer la devise et son symbole
    currency = get_asset_currency(selected_asset)
    currency_symbol = get_currency_symbol(currency)
    
    # Formater le prix selon la devise
    if currency in ['JPY', 'KRW']:
        price_display = f"{currency_symbol}{close_price:,.0f}"
    elif close_price < 0.01:
        price_display = f"{currency_symbol}{close_price:.6f}"
    elif close_price < 1:
        price_display = f"{currency_symbol}{close_price:.4f}"
    elif close_price > 10000:
        price_display = f"{currency_symbol}{close_price:,.0f}"
    else:
        price_display = f"{currency_symbol}{close_price:.2f}"
    
    date_val = last_row.get('date', last_row.get('Date', ''))
    if isinstance(date_val, pd.Timestamp):
        date_str = date_val.strftime('%Y-%m-%d')
    else:
        date_str = str(date_val)[:10] if date_val else ''
    
    if recommendation == 'Acheter':
        reco_badge = dbc.Badge(f"🟢 ACHETER", color="success", className="fs-5 me-2")
    elif recommendation == 'Vendre':
        reco_badge = dbc.Badge(f"🔴 VENDRE", color="danger", className="fs-5 me-2")
    else:
        reco_badge = dbc.Badge(f"⚪ NEUTRE", color="secondary", className="fs-5 me-2")
    
    conviction_color = "success" if conviction >= 4 else "warning" if conviction >= 3 else "secondary"
    conviction_badge = dbc.Badge(f"Conviction: {conviction}/5", color=conviction_color, className="me-2")
    
    trend_display = trend.replace('_', ' ').title() if isinstance(trend, str) else 'Neutral'
    if 'bullish' in str(trend):
        trend_badge = dbc.Badge(f"↗ {trend_display}", color="success", className="me-2")
    elif 'bearish' in str(trend):
        trend_badge = dbc.Badge(f"↘ {trend_display}", color="danger", className="me-2")
    else:
        trend_badge = dbc.Badge(f"→ {trend_display}", color="secondary", className="me-2")
    
    # Badge Bollinger
    if bb_signal in ['lower_touch', 'lower_zone']:
        bb_badge = dbc.Badge(f"BB: Support", color="success", className="me-3")
    elif bb_signal in ['upper_touch', 'upper_zone']:
        bb_badge = dbc.Badge(f"BB: Résistance", color="danger", className="me-3")
    elif bb_signal == 'squeeze':
        bb_badge = dbc.Badge(f"BB: Squeeze ⚡", color="warning", className="me-3")
    else:
        bb_badge = dbc.Badge(f"BB: Neutre", color="secondary", className="me-3")
    
    return [
        html.Span(f"{selected_asset}", className="fs-5 fw-bold me-3"),
        html.Span(price_display, className="me-3"),
        reco_badge,
        conviction_badge,
        trend_badge,
        bb_badge,
        html.Span(f"({date_str})", className="text-muted small"),
    ]

def create_main_charts_with_zoom(df_graph, selected_date, selected_asset, display_options, config, x_range=None):
    """Crée les graphiques principaux avec zoom synchronisé."""
    main_charts = []
    
    if 'price' in display_options:
        show_ma = 'moving_averages' in display_options
        show_bb = 'bollinger' in display_options
        fig_price = create_price_chart(df_graph, selected_date, selected_asset, show_ma, show_bb, config)
        if x_range:
            fig_price.update_xaxes(range=x_range)
        main_charts.append(
            dcc.Graph(
                id='price-chart',
                figure=fig_price, 
                style={'height': '400px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        )
    
    if 'recommendations' in display_options:
        fig_reco = create_recommendations_chart(df_graph, selected_date)
        if x_range:
            fig_reco.update_xaxes(range=x_range)
        main_charts.append(html.Div([
            html.H6(f"📊 Recommandations — {INDICATOR_DESCRIPTIONS['recommendations']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='recommendations-chart',
                figure=fig_reco, 
                style={'height': '150px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    if 'trend' in display_options:
        fig_trend = create_trend_chart(df_graph, selected_date, config)
        if x_range:
            fig_trend.update_xaxes(range=x_range)
        main_charts.append(html.Div([
            html.H6(f"📈 Tendance (ADX) — {INDICATOR_DESCRIPTIONS['trend']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='trend-chart',
                figure=fig_trend, 
                style={'height': '150px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    # Graphiques vides pour les IDs manquants
    if 'price' not in display_options:
        main_charts.append(html.Div(id='price-chart', style={'display': 'none'}))
    if 'recommendations' not in display_options:
        main_charts.append(html.Div([
            dcc.Graph(id='recommendations-chart', figure={}, style={'display': 'none'})
        ], style={'display': 'none'}))
    if 'trend' not in display_options:
        main_charts.append(html.Div([
            dcc.Graph(id='trend-chart', figure={}, style={'display': 'none'})
        ], style={'display': 'none'}))
    
    return main_charts


def create_technical_charts_with_zoom(df_graph, selected_date, display_options, config, x_range=None):
    """Crée les graphiques techniques détaillés avec zoom synchronisé."""
    technical_charts = []
    
    if 'macd' in display_options:
        fig_macd = create_macd_chart(df_graph, selected_date)
        if x_range:
            fig_macd.update_xaxes(range=x_range)
        technical_charts.append(html.Div([
            html.H6(f"📉 MACD — {INDICATOR_DESCRIPTIONS['macd']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='macd-chart',
                figure=fig_macd, 
                style={'height': '180px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    if 'volume' in display_options:
        fig_volume = create_volume_chart(df_graph, selected_date)
        if x_range:
            fig_volume.update_xaxes(range=x_range)
        technical_charts.append(html.Div([
            html.H6(f"📊 Volume — {INDICATOR_DESCRIPTIONS['volume']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='volume-chart',
                figure=fig_volume, 
                style={'height': '130px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    if 'rsi' in display_options:
        fig_rsi = create_rsi_chart(df_graph, selected_date, config)
        if x_range:
            fig_rsi.update_xaxes(range=x_range)
        technical_charts.append(html.Div([
            html.H6(f"📊 RSI — {INDICATOR_DESCRIPTIONS['rsi']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='rsi-chart',
                figure=fig_rsi, 
                style={'height': '150px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    if 'stochastic' in display_options:
        fig_stoch = create_stochastic_chart(df_graph, selected_date, config)
        if x_range:
            fig_stoch.update_xaxes(range=x_range)
        technical_charts.append(html.Div([
            html.H6(f"📈 Stochastique — {INDICATOR_DESCRIPTIONS['stochastic']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='stochastic-chart',
                figure=fig_stoch, 
                style={'height': '150px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    if 'patterns' in display_options:
        fig_patterns = create_patterns_chart(df_graph, selected_date)
        if x_range:
            fig_patterns.update_xaxes(range=x_range)
        technical_charts.append(html.Div([
            html.H6(f"🕯️ Patterns — {INDICATOR_DESCRIPTIONS['patterns']}", 
                   className="text-muted mt-3 mb-1", style={'fontSize': '12px'}),
            dcc.Graph(
                id='patterns-chart',
                figure=fig_patterns, 
                style={'height': '180px'}, 
                config={'displayModeBar': True, 'scrollZoom': True}
            )
        ]))
    
    # Graphiques vides pour les IDs manquants
    if 'macd' not in display_options:
        technical_charts.append(dcc.Graph(id='macd-chart', figure={}, style={'display': 'none'}))
    if 'volume' not in display_options:
        technical_charts.append(dcc.Graph(id='volume-chart', figure={}, style={'display': 'none'}))
    if 'rsi' not in display_options:
        technical_charts.append(dcc.Graph(id='rsi-chart', figure={}, style={'display': 'none'}))
    if 'stochastic' not in display_options:
        technical_charts.append(dcc.Graph(id='stochastic-chart', figure={}, style={'display': 'none'}))
    if 'patterns' not in display_options:
        technical_charts.append(dcc.Graph(id='patterns-chart', figure={}, style={'display': 'none'}))
    
    if not any(opt in display_options for opt in ['macd', 'volume', 'rsi', 'stochastic', 'patterns']):
        technical_charts.insert(0, html.P("Aucun indicateur technique sélectionné.", className="text-muted"))
    
    return technical_charts