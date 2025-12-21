# components/tables.py
"""
Fonctions de création des tableaux HTML.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from constants import FUNDAMENTAL_DESCRIPTIONS
from .indicators import calculate_indicator_contributions
from .charts import create_quarterly_chart


def create_technical_indicators_table(row, config):
    """Crée le tableau détaillé des indicateurs techniques."""
    contributions = calculate_indicator_contributions(row, config)
    
    rows = []
    total_buy = 0
    total_sell = 0
    
    for ind in contributions:
        buy_c = ind.get('buy_contrib', 0)
        sell_c = ind.get('sell_contrib', 0)
        total_buy += buy_c
        total_sell += sell_c
        
        # Afficher la contribution dominante
        if buy_c > 0 and sell_c == 0:
            contrib_display = html.Span(f"+{buy_c:.1f}", style={'color': '#26a69a'})
        elif sell_c > 0 and buy_c == 0:
            contrib_display = html.Span(f"-{sell_c:.1f}", style={'color': '#ef5350'})
        elif buy_c > 0 and sell_c > 0:
            contrib_display = html.Span(f"+{buy_c:.1f}/-{sell_c:.1f}", style={'color': '#ffc107'})
        else:
            contrib_display = html.Span("0", style={'color': '#6c757d'})
        
        rows.append(
            html.Tr([
                html.Td(ind['name'], style={'fontWeight': 'bold', 'width': '12%'}),
                html.Td(ind['interpretation_guide'], className="small text-muted", style={'width': '22%'}),
                html.Td(ind['value'], className="text-center", style={'width': '15%'}),
                html.Td(ind['interpretation'], className="text-center small", style={'width': '20%'}),
                html.Td(ind['signal'], className="text-center", style={'width': '10%'}),
                html.Td(str(ind['weight']), className="text-center", style={'width': '6%'}),
                html.Td(contrib_display, className="text-center", style={'width': '10%', 'fontWeight': 'bold'}),
            ])
        )
    
    # Ligne de totaux
    recommendation = row.get('recommendation', 'Neutre')
    if recommendation == 'Acheter':
        result_color = '#198754'
        result_text = f"ACHAT: {total_buy:.1f}"
    elif recommendation == 'Vendre':
        result_color = '#dc3545'
        result_text = f"VENTE: {total_sell:.1f}"
    else:
        result_color = '#6c757d'
        result_text = f"NEUTRE"
    
    rows.append(
        html.Tr([
            html.Td("TOTAUX", colSpan=5, className="text-end", style={'fontWeight': 'bold'}),
            html.Td(
                html.Div([
                    html.Span(f"🟢 {total_buy:.1f}", style={'color': '#26a69a', 'marginRight': '10px'}),
                    html.Span(f"🔴 {total_sell:.1f}", style={'color': '#ef5350'}),
                ]),
                className="text-center"
            ),
            html.Td(result_text, className="text-center", 
                   style={'fontWeight': 'bold', 'backgroundColor': result_color, 'color': 'white'}),
        ], style={'backgroundColor': '#2c3034'})
    )
    
    # Explication du calcul
    decision_cfg = config.get('decision', {})
    seuil = decision_cfg.get('min_conviction_threshold', 2.5) * 0.8
    diff = decision_cfg.get('conviction_difference', 0.5)
    
    explanation = html.Tr([
        html.Td(
            html.Small([
                f"Règle: Score ≥ {seuil:.1f} ET différence ≥ {diff} → ",
                html.Span("Achat", style={'color': '#26a69a'}),
                " si vert > rouge, ",
                html.Span("Vente", style={'color': '#ef5350'}),
                " si rouge > vert"
            ], className="text-muted"),
            colSpan=7,
            className="text-center",
            style={'borderTop': '1px solid #444'}
        )
    ])
    rows.append(explanation)
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Indicateur"),
            html.Th("Guide"),
            html.Th("Valeur", className="text-center"),
            html.Th("Interprétation", className="text-center"),
            html.Th("Signal", className="text-center"),
            html.Th("Poids", className="text-center"),
            html.Th("Contrib.", className="text-center"),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", responsive=True)


def create_ratio_table(title, ratios):
    """
    Crée un tableau pour afficher les ratios fondamentaux avec descriptions détaillées.
    """
    rows = []
    for ratio in ratios:
        name = ratio[0]
        value = ratio[1]
        desc_key = ratio[2]
        ideal = ratio[3]
        suffix = ratio[4] if len(ratio) > 4 else ''
        
        description = FUNDAMENTAL_DESCRIPTIONS.get(desc_key, "Description non disponible.")
        
        if isinstance(value, (int, float)) and value is not None:
            display_value = f"{value:.2f}{suffix}"
        elif isinstance(value, str):
            display_value = value
        else:
            display_value = "N/A"
        
        rows.append(
            html.Tr([
                html.Td(name, style={'fontWeight': 'bold', 'width': '12%', 'verticalAlign': 'top'}),
                html.Td(display_value, className="text-end", style={'width': '8%', 'verticalAlign': 'top'}),
                html.Td(description, className="text-muted small", style={'width': '65%', 'lineHeight': '1.4'}),
                html.Td(ideal, className="text-info small text-end", style={'width': '15%', 'verticalAlign': 'top'}),
            ])
        )
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Indicateur"),
            html.Th("Valeur", className="text-end"),
            html.Th("Explication détaillée"),
            html.Th("Zone Idéale", className="text-end"),
        ]), style={'backgroundColor': '#1a1d20'}),
        html.Tbody(rows)
    ], bordered=True, color="dark", hover=True, size="sm", className="mb-0")


def create_fundamental_details(current_data, quarterly_history):
    """Crée la section détaillée avec les 5 catégories et l'historique."""
    from fundamental_analyzer import format_large_number
    
    tabs = dbc.Tabs([
        # === TAB 1: VALORISATION ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Valorisation", [
                    ("P/E Ratio", current_data.get('pe_ratio'), "pe_ratio", "< 20-25"),
                    ("P/E Forward", current_data.get('forward_pe'), "forward_pe", "< 20"),
                    ("PEG Ratio", current_data.get('peg_ratio'), "peg_ratio", "< 1.5"),
                    ("P/B Ratio", current_data.get('pb_ratio'), "pb_ratio", "< 3"),
                    ("P/S Ratio", current_data.get('ps_ratio'), "ps_ratio", "< 2-3"),
                    ("EV/EBITDA", current_data.get('ev_ebitda'), "ev_ebitda", "< 12-15"),
                    ("EV/Revenue", current_data.get('ev_revenue'), "ev_revenue", "< 3"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['pe_ratio', 'pb_ratio', 'ps_ratio'], 
                                      ['P/E', 'P/B', 'P/S'], "Ratios de Valorisation")
            ], className="p-2")
        ], label="💵 Valorisation", tab_id="tab-valuation"),
        
        # === TAB 2: RENTABILITÉ ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Rentabilité", [
                    ("ROE", current_data.get('roe'), "roe", "> 15%", "%"),
                    ("ROA", current_data.get('roa'), "roa", "> 5%", "%"),
                    ("Marge Brute", current_data.get('gross_margin'), "gross_margin", "> 40%", "%"),
                    ("Marge Opérationnelle", current_data.get('operating_margin'), "operating_margin", "> 15%", "%"),
                    ("Marge Nette", current_data.get('net_margin'), "net_margin", "> 10%", "%"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['roe', 'net_margin', 'gross_margin'], 
                                      ['ROE', 'Marge Nette', 'Marge Brute'], "Ratios de Rentabilité (%)")
            ], className="p-2")
        ], label="💰 Rentabilité", tab_id="tab-profitability"),
        
        # === TAB 3: SANTÉ FINANCIÈRE ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Santé Financière", [
                    ("Dette/Equity", current_data.get('debt_equity'), "debt_equity", "< 0.5-1"),
                    ("Current Ratio", current_data.get('current_ratio'), "current_ratio", "> 1.5"),
                    ("Quick Ratio", current_data.get('quick_ratio'), "quick_ratio", "> 1"),
                    ("Dette Totale", format_large_number(current_data.get('total_debt')), "total_debt", "—"),
                    ("Cash Disponible", format_large_number(current_data.get('total_cash')), "total_cash", "—"),
                    ("Free Cash Flow", format_large_number(current_data.get('free_cash_flow')), "free_cash_flow", "Positif"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['debt_equity', 'current_ratio', 'quick_ratio'], 
                                      ['Dette/Equity', 'Current Ratio', 'Quick Ratio'], "Ratios de Santé Financière")
            ], className="p-2")
        ], label="🏦 Santé Financière", tab_id="tab-health"),
        
        # === TAB 4: CROISSANCE ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Croissance", [
                    ("Croissance CA (YoY)", current_data.get('revenue_growth'), "revenue_growth", "> 5-10%", "%"),
                    ("Croissance Bénéfices", current_data.get('earnings_growth'), "earnings_growth", "> 10%", "%"),
                    ("EPS (TTM)", current_data.get('eps_trailing'), "eps_trailing", "—"),
                    ("EPS (Forward)", current_data.get('eps_forward'), "eps_forward", "—"),
                ]),
                html.Hr(),
                html.H6("📈 Historique Trimestriel - Revenus et Bénéfices", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['revenue', 'net_income'], 
                                      ['Revenus', 'Bénéfice Net'], "Revenus et Bénéfices (normalisé)", normalize=True),
                html.Br(),
                html.H6("📈 Croissance Year-over-Year", className="mt-3"),
                create_quarterly_chart(quarterly_history, ['revenue_yoy', 'net_income_yoy'], 
                                      ['Croiss. CA YoY', 'Croiss. Bénéf. YoY'], "Croissance YoY (%)")
            ], className="p-2")
        ], label="📈 Croissance", tab_id="tab-growth"),
        
        # === TAB 5: DIVIDENDES ===
        dbc.Tab([
            html.Div([
                create_ratio_table("Dividendes", [
                    ("Dividend Yield", current_data.get('dividend_yield'), "dividend_yield", "2-5%", "%"),
                    ("Dividende Annuel", current_data.get('dividend_rate'), "dividend_rate", "—", "$"),
                    ("Payout Ratio", current_data.get('payout_ratio'), "payout_ratio", "< 60%", "%"),
                    ("Yield Moyen 5 ans", current_data.get('five_year_avg_dividend_yield'), "five_year_avg_dividend_yield", "—", "%"),
                ]),
            ], className="p-2")
        ], label="💸 Dividendes", tab_id="tab-dividends"),
        
    ], id="fundamental-tabs", active_tab="tab-valuation")
    
    return tabs