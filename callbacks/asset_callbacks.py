# callbacks/asset_callbacks.py
"""
Callbacks pour la gestion des actifs avec catégories.
VERSION 2.0 - Ajout du bouton de réinitialisation aux actifs par défaut
"""
from dash import Input, Output, State, ctx, html, no_update
import dash_bootstrap_components as dbc
import yfinance as yf

from config import (
    load_user_assets, load_user_assets_with_categories, 
    save_user_assets_with_categories, detect_asset_category,
    update_asset_category, ASSET_CATEGORIES, DEFAULT_ASSETS,
    reset_to_default_assets
)


def register_asset_callbacks(app):
    """Enregistre les callbacks de gestion des actifs."""
    
    # CALLBACK 1: Initialisation des options du dropdown (déclenché par assets-store uniquement)
    @app.callback(
        [Output('asset-dropdown', 'options'),
         Output('remove-asset-dropdown', 'options'),
         Output('current-assets-list', 'children'),
         Output('category-dropdown', 'options')],
        [Input('assets-store', 'data')]
    )
    def update_asset_options(assets):
        """Met à jour les options des dropdowns quand la liste d'assets change."""
        if not assets:
            assets = load_user_assets()
        
        # Charger avec catégories
        assets_with_cats = load_user_assets_with_categories()
        
        # Options pour le dropdown des assets avec icône de catégorie
        options = []
        for ticker in assets:
            cat = assets_with_cats.get(ticker, 'custom')
            cat_info = ASSET_CATEGORIES.get(cat, ASSET_CATEGORIES['custom'])
            icon = cat_info.get('icon', '⚙️')
            options.append({'label': f"{icon} {ticker}", 'value': ticker})
        
        remove_options = [{'label': a, 'value': a} for a in assets]
        
        # Badges avec couleurs de catégorie
        badges = []
        for ticker in assets:
            cat = assets_with_cats.get(ticker, 'custom')
            cat_info = ASSET_CATEGORIES.get(cat, ASSET_CATEGORIES['custom'])
            badges.append(
                dbc.Badge(
                    f"{cat_info['icon']} {ticker}",
                    style={'backgroundColor': cat_info['color']},
                    className="me-1 mb-1"
                )
            )
        
        # Options pour le dropdown des catégories
        category_options = [
            {'label': f"{v['icon']} {v['name']}", 'value': k}
            for k, v in ASSET_CATEGORIES.items()
        ]
        
        return options, remove_options, badges, category_options
    
    # CALLBACK 2: Initialiser la valeur du dropdown seulement au premier chargement
    @app.callback(
        Output('asset-dropdown', 'value'),
        [Input('assets-store', 'data')],
        [State('asset-dropdown', 'value')],
        prevent_initial_call=False
    )
    def initialize_asset_value(assets, current_value):
        """Initialise la valeur du dropdown uniquement si aucune valeur n'est sélectionnée."""
        if not assets:
            assets = load_user_assets()
        
        # Si une valeur est déjà sélectionnée et qu'elle existe dans la liste, la garder
        if current_value and current_value in assets:
            return no_update
        
        # Sinon, sélectionner le premier asset
        return assets[0] if assets else None
    
    # CALLBACK 3: Mettre à jour la catégorie affichée quand l'asset sélectionné change
    @app.callback(
        Output('category-dropdown', 'value'),
        [Input('asset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_category_for_selected_asset(selected_asset):
        """Met à jour le dropdown de catégorie quand on change d'asset."""
        if not selected_asset:
            return 'custom'
        
        assets_with_cats = load_user_assets_with_categories()
        return assets_with_cats.get(selected_asset, 'custom')

    # CALLBACK 4: Gestion des actifs (ajout, suppression, mise à jour catégorie, réinitialisation)
    @app.callback(
        [Output('assets-store', 'data'),
         Output('asset-management-status', 'children'),
         Output('new-asset-input', 'value')],
        [Input('add-asset-btn', 'n_clicks'),
         Input('remove-asset-btn', 'n_clicks'),
         Input('update-category-btn', 'n_clicks'),
         Input('reset-assets-btn', 'n_clicks')],
        [State('new-asset-input', 'value'),
         State('remove-asset-dropdown', 'value'),
         State('asset-dropdown', 'value'),
         State('category-dropdown', 'value'),
         State('assets-store', 'data')],
        prevent_initial_call=True
    )
    def manage_assets(add_clicks, remove_clicks, update_cat_clicks, reset_clicks,
                      new_asset, asset_to_remove, selected_asset, new_category, current_assets):
        triggered = ctx.triggered_id
        
        # Réinitialiser aux actifs par défaut
        if triggered == 'reset-assets-btn':
            success = reset_to_default_assets()
            if success:
                return DEFAULT_ASSETS.copy(), dbc.Alert([
                    f"🔄 Liste réinitialisée aux {len(DEFAULT_ASSETS)} actifs par défaut"
                ], color="success", duration=4000), ""
            else:
                return current_assets, dbc.Alert(
                    "❌ Erreur lors de la réinitialisation", 
                    color="danger", 
                    duration=4000
                ), ""
        
        # Ajouter un nouvel asset
        if triggered == 'add-asset-btn' and new_asset:
            new_asset = new_asset.upper().strip()
            try:
                ticker = yf.Ticker(new_asset)
                info = ticker.info
                hist = ticker.history(period='5d')
                if hist.empty:
                    return current_assets, dbc.Alert(
                        f"❌ '{new_asset}' non trouvé sur Yahoo Finance", 
                        color="danger", 
                        duration=4000
                    ), ""
                
                # Détecter la catégorie
                detected_category = detect_asset_category(new_asset, info)
                cat_info = ASSET_CATEGORIES.get(detected_category, ASSET_CATEGORIES['custom'])
                
            except Exception as e:
                return current_assets, dbc.Alert(
                    f"❌ Erreur lors de la vérification de '{new_asset}': {str(e)}", 
                    color="danger", 
                    duration=4000
                ), ""
            
            if new_asset in current_assets:
                return current_assets, dbc.Alert(
                    f"⚠️ '{new_asset}' existe déjà", 
                    color="warning", 
                    duration=3000
                ), ""
            
            # Charger avec catégories et ajouter
            assets_with_cats = load_user_assets_with_categories()
            assets_with_cats[new_asset] = detected_category
            save_user_assets_with_categories(assets_with_cats)
            
            current_assets.append(new_asset)
            
            return current_assets, dbc.Alert([
                f"✅ '{new_asset}' ajouté | ",
                html.Span(f"{cat_info['icon']} {cat_info['name']}", style={'fontWeight': 'bold'}),
                html.Small(" (catégorie détectée automatiquement)", className="text-muted")
            ], color="success", duration=5000), ""
        
        # Supprimer un asset
        elif triggered == 'remove-asset-btn' and asset_to_remove:
            if len(current_assets) <= 1:
                return current_assets, dbc.Alert(
                    "⚠️ Impossible de supprimer le dernier actif", 
                    color="warning", 
                    duration=3000
                ), ""
            
            assets_with_cats = load_user_assets_with_categories()
            if asset_to_remove in assets_with_cats:
                del assets_with_cats[asset_to_remove]
                save_user_assets_with_categories(assets_with_cats)
            
            current_assets.remove(asset_to_remove)
            return current_assets, dbc.Alert(
                f"🗑️ '{asset_to_remove}' supprimé", 
                color="info", 
                duration=3000
            ), ""
        
        # Mettre à jour la catégorie
        elif triggered == 'update-category-btn' and selected_asset and new_category:
            update_asset_category(selected_asset, new_category)
            cat_info = ASSET_CATEGORIES.get(new_category, ASSET_CATEGORIES['custom'])
            return current_assets, dbc.Alert([
                f"✅ Catégorie de '{selected_asset}' mise à jour: ",
                html.Span(f"{cat_info['icon']} {cat_info['name']}", style={'fontWeight': 'bold'})
            ], color="success", duration=4000), ""
        
        return current_assets, "", ""