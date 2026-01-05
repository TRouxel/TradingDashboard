# components/summary_table.py
"""
Tableau récapitulatif des divergences RSI pour tous les actifs.
VERSION 2.0 - Sous-sections par catégorie d'actifs
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta

from config import ASSET_CATEGORIES, get_asset_category, load_user_assets_with_categories


def create_asset_row(asset_data, is_loaded=True):
    """Crée une ligne de tableau pour un actif."""
    ticker = asset_data.get('ticker', 'N/A')
    
    if not is_loaded:
        # Ligne pour actif non chargé
        return html.Tr([
            html.Td(
                dbc.Checkbox(
                    id={'type': 'asset-checkbox', 'index': ticker},
                    value=False,
                    className="form-check-input"
                ),
                className="text-center",
                style={'width': '40px'}
            ),
            html.Td(html.Strong(ticker), style={'width': '80px'}),
            html.Td(html.Span("—", className="text-muted"), className="text-end", style={'width': '90px'}),
            html.Td(html.Span("—", className="text-muted"), className="text-center", style={'width': '60px'}),
            html.Td(dbc.Badge("—", color="secondary", className="me-1"), className="text-center", style={'width': '100px'}),
            html.Td(dbc.Badge("—", color="secondary", className="me-1"), className="text-center", style={'width': '100px'}),
            html.Td(dbc.Badge("—", color="secondary", className="me-1"), className="text-center", style={'width': '80px'}),
            html.Td(dbc.Badge("—", color="secondary"), className="text-center", style={'width': '100px'}),
        ], id={'type': 'asset-row', 'index': ticker}, className="text-muted")
    
    # Données pour actif chargé
    rsi_divergence = asset_data.get('rsi_divergence', 'none')
    last_div_date = asset_data.get('last_div_date')
    last_div_type = asset_data.get('last_div_type', 'none')
    current_price = asset_data.get('current_price', 0)
    rsi_value = asset_data.get('rsi_value')
    recommendation = asset_data.get('recommendation', 'Neutre')
    
    # Badge pour divergence actuelle
    if rsi_divergence == 'bullish':
        div_badge = dbc.Badge("🟢 Achat", color="success", className="me-1")
    elif rsi_divergence == 'bearish':
        div_badge = dbc.Badge("🔴 Vente", color="danger", className="me-1")
    else:
        div_badge = dbc.Badge("— Néant", color="secondary", className="me-1")
    
    # Calcul de l'ancienneté de la dernière divergence
    if last_div_date:
        try:
            if isinstance(last_div_date, str):
                last_date = pd.to_datetime(last_div_date)
            else:
                last_date = last_div_date
            
            days_ago = (datetime.now() - last_date.to_pydatetime().replace(tzinfo=None)).days
            
            if days_ago == 0:
                date_display = "Aujourd'hui"
                date_color = "success"
            elif days_ago == 1:
                date_display = "Hier"
                date_color = "success"
            elif days_ago <= 3:
                date_display = f"-{days_ago} jours"
                date_color = "success"
            elif days_ago <= 7:
                date_display = f"-{days_ago} jours"
                date_color = "warning"
            elif days_ago <= 21:
                date_display = f"-{days_ago} jours"
                date_color = "info"
            else:
                date_display = f"> 21 jours"
                date_color = "secondary"
            
            date_badge = dbc.Badge(date_display, color=date_color, className="me-1")
        except Exception:
            date_badge = dbc.Badge("N/A", color="secondary", className="me-1")
    else:
        date_badge = dbc.Badge("Aucune", color="secondary", className="me-1")
    
    # Badge pour le type de la dernière divergence
    if last_div_type == 'bullish':
        last_type_badge = dbc.Badge("Achat", color="success", className="me-1")
    elif last_div_type == 'bearish':
        last_type_badge = dbc.Badge("Vente", color="danger", className="me-1")
    else:
        last_type_badge = dbc.Badge("—", color="secondary", className="me-1")
    
    # Badge pour la recommandation globale
    if recommendation == 'Acheter':
        reco_badge = dbc.Badge("🟢 Acheter", color="success")
    elif recommendation == 'Vendre':
        reco_badge = dbc.Badge("🔴 Vendre", color="danger")
    else:
        reco_badge = dbc.Badge("⚪ Neutre", color="secondary")
    
    # Couleur du RSI
    if rsi_value is not None:
        if rsi_value < 30:
            rsi_color = "#26a69a"
        elif rsi_value > 70:
            rsi_color = "#ef5350"
        else:
            rsi_color = "#ffffff"
        rsi_display = f"{rsi_value:.1f}"
    else:
        rsi_color = "#6c757d"
        rsi_display = "N/A"
    
    # Prix
    if current_price is not None and current_price != 0:
        price_display = f"${current_price:.2f}"
    else:
        price_display = "N/A"
    
    return html.Tr([
        html.Td(
            dbc.Checkbox(
                id={'type': 'asset-checkbox', 'index': ticker},
                value=True,
                className="form-check-input"
            ),
            className="text-center",
            style={'width': '40px'}
        ),
        html.Td(html.Strong(ticker), style={'width': '80px'}),
        html.Td(price_display, className="text-end", style={'width': '90px'}),
        html.Td(
            html.Span(rsi_display, style={'color': rsi_color, 'fontWeight': 'bold'}),
            className="text-center",
            style={'width': '60px'}
        ),
        html.Td(div_badge, className="text-center", style={'width': '100px'}),
        html.Td(date_badge, className="text-center", style={'width': '100px'}),
        html.Td(last_type_badge, className="text-center", style={'width': '80px'}),
        html.Td(reco_badge, className="text-center", style={'width': '100px'}),
    ], id={'type': 'asset-row', 'index': ticker})


def create_category_table(category_key, assets_data, is_loaded=True):
    """Crée un tableau pour une catégorie d'actifs."""
    cat_info = ASSET_CATEGORIES.get(category_key, ASSET_CATEGORIES['custom'])
    
    rows = []
    for asset_data in assets_data:
        if is_loaded:
            rows.append(create_asset_row(asset_data, is_loaded=True))
        else:
            rows.append(create_asset_row({'ticker': asset_data}, is_loaded=False))
    
    if not rows:
        return None
    
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("", style={'width': '40px'}),
            html.Th("Actif", style={'width': '80px'}),
            html.Th("Prix", className="text-end", style={'width': '90px'}),
            html.Th("RSI", className="text-center", style={'width': '60px'}),
            html.Th("Div. RSI", className="text-center", style={'width': '100px'}),
            html.Th("Dernière Div.", className="text-center", style={'width': '100px'}),
            html.Th("Type", className="text-center", style={'width': '80px'}),
            html.Th("Reco.", className="text-center", style={'width': '100px'}),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", responsive=True, className="mb-0")
    
    return table


def create_assets_summary_table(summary_data, assets_list=None):
    """
    Crée le tableau récapitulatif des actifs avec sections par catégorie.
    
    Args:
        summary_data: Liste de dictionnaires avec les données de chaque actif
        assets_list: Liste des actifs à afficher (pour affichage initial sans données)
    """
    # Charger les catégories des actifs
    assets_with_cats = load_user_assets_with_categories()
    
    # Organiser les données par catégorie
    categories_data = {}
    
    if summary_data:
        # On a des données chargées
        for asset_data in summary_data:
            ticker = asset_data.get('ticker', '')
            category = assets_with_cats.get(ticker, get_asset_category(ticker))
            
            if category not in categories_data:
                categories_data[category] = []
            categories_data[category].append(asset_data)
    elif assets_list:
        # Affichage initial sans données
        for ticker in assets_list:
            category = assets_with_cats.get(ticker, get_asset_category(ticker))
            
            if category not in categories_data:
                categories_data[category] = []
            categories_data[category].append(ticker)
    else:
        return html.Div([
            html.P("Aucun actif configuré.", className="text-muted text-center")
        ])
    
    # Créer les sections collapsibles par catégorie
    accordion_items = []
    
    # Trier les catégories par nombre d'actifs (décroissant) puis par nom
    sorted_categories = sorted(
        categories_data.keys(),
        key=lambda c: (-len(categories_data[c]), c)
    )
    
    for category_key in sorted_categories:
        cat_info = ASSET_CATEGORIES.get(category_key, ASSET_CATEGORIES['custom'])
        cat_assets = categories_data[category_key]
        
        # Compter les divergences dans cette catégorie
        if summary_data:
            num_bullish = sum(1 for a in cat_assets if a.get('rsi_divergence') == 'bullish')
            num_bearish = sum(1 for a in cat_assets if a.get('rsi_divergence') == 'bearish')
            is_loaded = True
        else:
            num_bullish = 0
            num_bearish = 0
            is_loaded = False
        
        # Créer le titre de l'accordéon avec badges
        title_content = html.Div([
            html.Span(cat_info['icon'], className="me-2", style={'fontSize': '1.2em'}),
            html.Span(cat_info['name'], className="fw-bold me-2"),
            dbc.Badge(f"{len(cat_assets)} actifs", color="info", className="me-2"),
        ], className="d-flex align-items-center")
        
        # Ajouter les badges de divergence si chargé
        if is_loaded:
            badges = []
            if num_bullish > 0:
                badges.append(dbc.Badge(f"🟢 {num_bullish}", color="success", className="me-1"))
            if num_bearish > 0:
                badges.append(dbc.Badge(f"🔴 {num_bearish}", color="danger", className="me-1"))
            
            title_content = html.Div([
                html.Span(cat_info['icon'], className="me-2", style={'fontSize': '1.2em'}),
                html.Span(cat_info['name'], className="fw-bold me-2"),
                dbc.Badge(f"{len(cat_assets)} actifs", color="info", className="me-2"),
                *badges
            ], className="d-flex align-items-center")
        
        # Créer le tableau pour cette catégorie
        table = create_category_table(category_key, cat_assets, is_loaded=is_loaded)
        
        if table:
            accordion_items.append(
                dbc.AccordionItem(
                    table,
                    title=title_content,
                    item_id=f"cat-{category_key}",
                )
            )
    
    # Checkbox "Tout sélectionner" en dehors de l'accordéon
    select_all_row = html.Div([
        dbc.Checkbox(
            id='select-all-assets',
            value=False,
            className="form-check-input me-2"
        ),
        html.Label("Tout sélectionner", className="form-check-label text-muted small"),
    ], className="mb-2 d-flex align-items-center")
    
    # Créer l'accordéon
    accordion = dbc.Accordion(
        accordion_items,
        id="summary-categories-accordion",
        start_collapsed=False,
        always_open=True,
        flush=True,
    )
    
    return html.Div([
        select_all_row,
        accordion
    ])


def create_summary_section():
    """Crée la section complète du tableau récapitulatif."""
    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    html.H5("📋 Récapitulatif des Actifs — Divergences RSI", className="mb-0"),
                ], width="auto"),
                dbc.Col([
                    dbc.Button(
                        "🔄 Rafraîchir sélection",
                        id="refresh-summary-btn",
                        color="primary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "🔄 Tout rafraîchir",
                        id="refresh-all-summary-btn",
                        color="info",
                        size="sm",
                        outline=True
                    ),
                ], className="text-end"),
            ], align="center"),
        ]),
        dbc.CardBody([
            dcc.Loading(
                html.Div(
                    id='assets-summary-table',
                ),
                type="circle"
            )
        ], className="p-2"),
    ], className="mb-3", color="dark", outline=True)