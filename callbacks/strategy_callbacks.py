# callbacks/strategy_callbacks.py
"""
Callbacks pour les stratégies de trading.
"""
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from trading_strategies import create_strategy_comparison_data
from components.strategy_charts import create_strategies_section


def register_strategy_callbacks(app):
    """Enregistre les callbacks des stratégies de trading."""
    
    @app.callback(
        Output('strategy-content', 'children'),
        [Input('analyze-strategy-btn', 'n_clicks')],
        [State('full-data-store', 'data'),
         State('config-store', 'data'),
         State('asset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_strategy_analysis(n_clicks, data, config, asset):
        if not data or not asset:
            return html.P("Chargez d'abord des données.", className="text-muted")
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Récupérer le spread depuis la config
        decision_cfg = config.get('decision', {})
        spread_pct = decision_cfg.get('conviction_difference', 0.5)
        
        # Créer la section des stratégies
        content = create_strategies_section(df, asset, spread_pct)
        
        return content
    
    @app.callback(
        Output("collapse-strategy", "is_open"),
        Input("collapse-strategy-btn", "n_clicks"),
        State("collapse-strategy", "is_open"),
        prevent_initial_call=True
    )
    def toggle_strategy_collapse(n_clicks, is_open):
        return not is_open