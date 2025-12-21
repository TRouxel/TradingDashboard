# callbacks/asset_callbacks.py
"""
Callbacks pour la gestion des actifs.
"""
from dash import Input, Output, State, ctx
import dash_bootstrap_components as dbc
import yfinance as yf

from config import load_user_assets, save_user_assets


def register_asset_callbacks(app):
    """Enregistre les callbacks de gestion des actifs."""
    
    @app.callback(
        [Output('asset-dropdown', 'options'),
         Output('asset-dropdown', 'value'),
         Output('remove-asset-dropdown', 'options'),
         Output('current-assets-list', 'children')],
        [Input('assets-store', 'data')]
    )
    def update_asset_dropdowns(assets):
        if not assets:
            assets = load_user_assets()
        
        options = [{'label': a, 'value': a} for a in assets]
        remove_options = [{'label': a, 'value': a} for a in assets]
        
        badges = [dbc.Badge(a, color="info", className="me-1 mb-1") for a in assets]
        
        return options, assets[0] if assets else None, remove_options, badges

    @app.callback(
        [Output('assets-store', 'data'),
         Output('asset-management-status', 'children'),
         Output('new-asset-input', 'value')],
        [Input('add-asset-btn', 'n_clicks'),
         Input('remove-asset-btn', 'n_clicks')],
        [State('new-asset-input', 'value'),
         State('remove-asset-dropdown', 'value'),
         State('assets-store', 'data')],
        prevent_initial_call=True
    )
    def manage_assets(add_clicks, remove_clicks, new_asset, asset_to_remove, current_assets):
        triggered = ctx.triggered_id
        
        if triggered == 'add-asset-btn' and new_asset:
            new_asset = new_asset.upper().strip()
            try:
                ticker = yf.Ticker(new_asset)
                hist = ticker.history(period='5d')
                if hist.empty:
                    return current_assets, dbc.Alert(f"❌ '{new_asset}' non trouvé sur Yahoo Finance", color="danger", duration=4000), ""
            except Exception:
                return current_assets, dbc.Alert(f"❌ Erreur lors de la vérification de '{new_asset}'", color="danger", duration=4000), ""
            
            if new_asset in current_assets:
                return current_assets, dbc.Alert(f"⚠️ '{new_asset}' existe déjà", color="warning", duration=3000), ""
            
            current_assets.append(new_asset)
            save_user_assets(current_assets)
            return current_assets, dbc.Alert(f"✅ '{new_asset}' ajouté avec succès", color="success", duration=3000), ""
        
        elif triggered == 'remove-asset-btn' and asset_to_remove:
            if len(current_assets) <= 1:
                return current_assets, dbc.Alert("⚠️ Impossible de supprimer le dernier actif", color="warning", duration=3000), ""
            
            current_assets.remove(asset_to_remove)
            save_user_assets(current_assets)
            return current_assets, dbc.Alert(f"🗑️ '{asset_to_remove}' supprimé", color="info", duration=3000), ""
        
        return current_assets, "", ""