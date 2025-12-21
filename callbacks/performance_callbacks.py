# callbacks/performance_callbacks.py
"""
Callbacks pour l'analyse de performance des indicateurs (backtesting).
"""
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from indicator_performance import calculate_performance_history
from components.performance_charts import (
    create_performance_section,
    create_performance_summary_cards,
    HORIZON_NAMES
)


def register_performance_callbacks(app):
    """Enregistre les callbacks de performance."""
    
    @app.callback(
        [Output('performance-content', 'children'),
         Output('performance-store', 'data')],
        [Input('analyze-performance-btn', 'n_clicks'),
         Input('performance-horizon-filter', 'value')],
        [State('full-data-store', 'data'),
         State('config-store', 'data'),
         State('asset-dropdown', 'value'),
         State('performance-store', 'data')],
        prevent_initial_call=True
    )
    def update_performance_analysis(n_clicks, selected_horizons, data, config, asset, cached_perf):
        from dash import callback_context
        ctx = callback_context
        
        if not data:
            return html.P("Chargez d'abord des données.", className="text-muted"), {}
        
        triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
        
        # Si on a des données en cache et qu'on change juste le filtre
        if triggered == 'performance-horizon-filter' and cached_perf:
            performance_history = {k: pd.DataFrame(v) for k, v in cached_perf.items()}
        elif triggered == 'analyze-performance-btn' or not cached_perf:
            # Recalculer la performance
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            
            horizons = [1, 2, 5, 10, 20]
            performance_history = calculate_performance_history(df, config, horizons)
            
            if not performance_history:
                return html.P("Pas assez de données pour analyser la performance.", className="text-muted"), {}
        else:
            performance_history = {k: pd.DataFrame(v) for k, v in cached_perf.items()}
        
        if not selected_horizons:
            selected_horizons = [1, 2, 5, 10, 20]
        
        # Créer le contenu
        content = html.Div([
            # En-tête
            html.Div([
                html.H5(f"📊 Backtesting des Indicateurs — {asset}", className="mb-2"),
                html.P([
                    f"Basé sur {len(pd.DataFrame(data))} jours de données. ",
                    html.Strong("Score positif = prédiction correcte"),
                    ", ",
                    html.Strong("négatif = incorrecte"),
                    ". Hauteur = intensité du signal."
                ], className="text-muted small mb-3"),
            ]),
            
            # Cartes résumé
            html.H6("📈 Vue d'ensemble", className="mb-2"),
            create_performance_summary_cards(performance_history, selected_horizons),
            
            html.Hr(),
            
            # Graphiques détaillés par indicateur
            html.H6("📉 Historique par Indicateur", className="mb-3"),
            create_performance_section(performance_history, selected_horizons),
        ])
        
        # Convertir pour le cache (DataFrame -> dict)
        cache_data = {k: v.to_dict('records') for k, v in performance_history.items()}
        
        return content, cache_data
    
    @app.callback(
        Output("collapse-performance", "is_open"),
        Input("collapse-performance-btn", "n_clicks"),
        State("collapse-performance", "is_open"),
        prevent_initial_call=True
    )
    def toggle_performance_collapse(n_clicks, is_open):
        return not is_open