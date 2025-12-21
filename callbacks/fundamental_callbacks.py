# callbacks/fundamental_callbacks.py
"""
Callbacks pour l'analyse fondamentale.
"""
from dash import html, Input, Output
import dash_bootstrap_components as dbc

from fundamental_analyzer import (
    get_fundamental_data, calculate_fundamental_score, format_large_number
)
from components import create_fundamental_details


def register_fundamental_callbacks(app):
    """Enregistre les callbacks d'analyse fondamentale."""
    
    @app.callback(
        [Output('fundamental-summary-header', 'children'),
         Output('fundamental-details-container', 'children'),
         Output('fundamental-store', 'data')],
        [Input('asset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_fundamental_analysis(selected_asset):
        if not selected_asset:
            return [], [], {}
        
        # Récupérer les données fondamentales
        current_data, quarterly_history = get_fundamental_data(selected_asset)
        
        if not current_data:
            header = [
                dbc.Badge("N/A", color="secondary", className="me-2"),
                html.Span("Données non disponibles (crypto, ETF, etc.)", className="text-muted small")
            ]
            return header, html.P("Analyse fondamentale non disponible pour cet actif.", className="text-muted"), {}
        
        # Calculer le score
        score, score_details = calculate_fundamental_score(current_data)
        
        # === HEADER AVEC SCORE ===
        if score:
            if score >= 4:
                badge_color = "success"
                score_text = "Excellent"
            elif score >= 3:
                badge_color = "primary"
                score_text = "Bon"
            elif score >= 2:
                badge_color = "warning"
                score_text = "Moyen"
            else:
                badge_color = "danger"
                score_text = "Faible"
            
            header = [
                dbc.Badge(f"Score: {score}/5", color=badge_color, className="me-2 fs-6"),
                dbc.Badge(score_text, color=badge_color, className="me-3"),
                html.Span(f"Secteur: {current_data.get('sector', 'N/A')}", className="text-muted small me-3"),
                html.Span(f"Cap: {format_large_number(current_data.get('market_cap'))}", className="text-muted small"),
            ]
        else:
            header = [dbc.Badge("Score N/A", color="secondary", className="me-2")]
        
        # === DÉTAILS FONDAMENTAUX ===
        details = create_fundamental_details(current_data, quarterly_history)
        
        # Stocker les données
        store_data = {
            'current': current_data,
            'history': quarterly_history.to_dict('records') if not quarterly_history.empty else []
        }
        
        return header, details, store_data