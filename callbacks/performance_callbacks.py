# callbacks/performance_callbacks.py
"""
Callbacks pour l'analyse de performance des indicateurs (backtesting).
VERSION 2.0 - Affichage des rendements réels + Performance cumulée
"""
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from indicator_performance import (
    calculate_performance_history,
    calculate_performance_history_with_combinations,
    analyze_signal_combinations,
    get_combination_summary,
    calculate_accuracy_stats
)
from components.performance_charts import (
    create_performance_section,
    create_performance_summary_cards,
    create_combination_ranking_table,
    create_global_performance_summary,
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
            # Recalculer la performance avec les combinaisons
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date'])
            
            horizons = [1, 2, 5, 10, 20]
            performance_history = calculate_performance_history_with_combinations(df, config, horizons)
            
            if not performance_history:
                return html.P("Pas assez de données pour analyser la performance.", className="text-muted"), {}
        else:
            performance_history = {k: pd.DataFrame(v) for k, v in cached_perf.items()}
        
        if not selected_horizons:
            selected_horizons = [1, 2, 5, 10, 20]
        
        # Récupérer le prix initial pour le calcul de performance
        df = pd.DataFrame(data)
        initial_price = df['close'].iloc[0] if 'close' in df.columns else None
        
        # Séparer indicateurs individuels et combinaisons
        individual_perf = {k: v for k, v in performance_history.items() if k.startswith('📊')}
        buy_combos = {k: v for k, v in performance_history.items() if k.startswith('🟢')}
        sell_combos = {k: v for k, v in performance_history.items() if k.startswith('🔴')}
        
        # Créer le classement des combinaisons
        all_combos = {**buy_combos, **sell_combos}
        combo_summary = get_combination_summary(all_combos, selected_horizons)
        
        # Créer le contenu
        content = html.Div([
            # En-tête
            html.Div([
                html.H5(f"📊 Backtesting des Indicateurs — {asset}", className="mb-2"),
                html.P([
                    f"Basé sur {len(pd.DataFrame(data))} jours de données. ",
                    html.Strong("Les barres représentent le gain/perte réel en %"),
                    " si on avait suivi le signal. ",
                    html.Strong("Perf. Σ = somme des rendements"),
                    " (performance cumulée)."
                ], className="text-muted small mb-3"),
            ]),
            
            # === RÉSUMÉ GLOBAL ===
            html.H5("🏅 Résumé Global", className="mb-3"),
            create_global_performance_summary(performance_history, selected_horizons, initial_price),
            
            html.Hr(className="my-4"),
            
            # === SECTION 1: CLASSEMENT DES COMBINAISONS ===
            html.H5("🏆 Classement des Combinaisons de Signaux", className="mb-3"),
            html.P([
                "Classement basé sur la précision (% de signaux corrects). ",
                "La colonne 'Perf. Σ' montre la performance cumulée en suivant chaque combinaison."
            ], className="text-muted small mb-3"),
            create_combination_ranking_table(combo_summary, selected_horizons),
            
            html.Hr(className="my-4"),
            
            # === SECTION 2: INDICATEURS INDIVIDUELS ===
            html.H5("📈 Performance des Indicateurs Individuels", className="mb-3"),
            create_performance_summary_cards(individual_perf, selected_horizons),
            
            html.Hr(),
            
            # === SECTION 3: DÉTAILS PAR INDICATEUR ===
            dbc.Accordion([
                dbc.AccordionItem([
                    html.P([
                        "Chaque barre représente le ",
                        html.Strong("rendement réel en %"),
                        " qu'on aurait obtenu en suivant le signal. ",
                        "Barre vers le haut = gain, vers le bas = perte."
                    ], className="text-muted small mb-3"),
                    create_performance_section(individual_perf, selected_horizons),
                ], title="📊 Détails des Indicateurs Individuels"),
                
                dbc.AccordionItem([
                    create_performance_section(buy_combos, selected_horizons),
                ], title="🟢 Détails des Combinaisons d'Achat"),
                
                dbc.AccordionItem([
                    create_performance_section(sell_combos, selected_horizons),
                ], title="🔴 Détails des Combinaisons de Vente"),
            ], start_collapsed=True, always_open=True),
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