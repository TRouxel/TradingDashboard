# constants.py
"""
Constantes et descriptions utilisées dans l'application.
"""

# === DESCRIPTIONS DES INDICATEURS POUR LE TABLEAU ===
INDICATOR_DETAILS = {
    'rsi': {
        'name': 'RSI (Relative Strength Index)',
        'interpretation': 'Mesure la vitesse et l\'amplitude des mouvements de prix. <30 = survente (achat potentiel), >70 = surachat (vente potentielle).',
        'weight_key': 'rsi_exit_oversold'
    },
    'stochastic': {
        'name': 'Stochastique (%K/%D)',
        'interpretation': 'Compare le prix de clôture à sa plage de prix. Croisement %K > %D en zone basse = signal achat.',
        'weight_key': 'stoch_bullish_cross'
    },
    'macd': {
        'name': 'MACD',
        'interpretation': 'Différence entre 2 moyennes mobiles. Croisement au-dessus du signal = momentum haussier.',
        'weight_key': 'macd_bullish'
    },
    'macd_histogram': {
        'name': 'Histogramme MACD',
        'interpretation': 'Visualise la force du momentum. Barres vertes croissantes = momentum haussier qui s\'accélère.',
        'weight_key': 'macd_histogram_positive'
    },
    'trend': {
        'name': 'Tendance (MAs + ADX)',
        'interpretation': 'Alignement des moyennes mobiles et force via ADX. Prix > SMA20 > SMA50 > SMA200 = tendance haussière forte.',
        'weight_key': 'trend_bonus'
    },
    'divergence': {
        'name': 'Divergence RSI',
        'interpretation': 'Prix fait nouveau bas mais RSI fait un bas plus haut = divergence haussière (retournement potentiel).',
        'weight_key': 'rsi_divergence'
    },
    'pattern': {
        'name': 'Pattern Chandelier',
        'interpretation': 'Figures de chandeliers japonais. Ex: Engulfing haussier, Doji, Hammer signalent des retournements.',
        'weight_key': 'pattern_bullish'
    },
    'adx': {
        'name': 'ADX (Force de Tendance)',
        'interpretation': 'Mesure la force de la tendance (pas la direction). >25 = tendance forte, >40 = très forte.',
        'weight_key': None
    },
}

# === DESCRIPTIONS DÉTAILLÉES DES RATIOS FONDAMENTAUX ===
FUNDAMENTAL_DESCRIPTIONS = {
    # Valorisation
    'pe_ratio': "Le P/E (Price-to-Earnings) compare le prix de l'action au bénéfice par action. Un P/E de 15 signifie que vous payez 15€ pour chaque 1€ de bénéfice annuel. Un P/E bas peut indiquer une action sous-évaluée, mais peut aussi refléter des problèmes. À comparer avec le secteur.",
    'forward_pe': "P/E calculé avec les bénéfices PRÉVUS des 12 prochains mois (estimations analystes). Plus pertinent que le P/E trailing car il anticipe la croissance future. Un forward P/E < trailing P/E suggère une croissance attendue.",
    'peg_ratio': "PEG = P/E divisé par le taux de croissance des bénéfices. Permet de comparer des entreprises à croissance différente. PEG < 1 = potentiellement sous-évalué compte tenu de la croissance. PEG > 2 = potentiellement surévalué.",
    'pb_ratio': "P/B (Price-to-Book) compare le prix de marché à la valeur comptable (actifs - dettes). P/B < 1 signifie que l'action cote sous sa valeur comptable. Utile pour les secteurs à actifs tangibles (banques, industrie).",
    'ps_ratio': "P/S (Price-to-Sales) compare la capitalisation au chiffre d'affaires. Utile pour les entreprises non rentables ou en forte croissance. Moins manipulable que le bénéfice. P/S < 1 est généralement attractif.",
    'ev_ebitda': "EV/EBITDA compare la valeur d'entreprise (market cap + dette - cash) à l'EBITDA. Mesure combien d'années d'EBITDA il faudrait pour \"racheter\" l'entreprise. Indépendant de la structure financière.",
    'ev_revenue': "EV/Revenue compare la valeur d'entreprise au CA. Utile pour comparer des entreprises du même secteur avec des marges différentes. Particulièrement utilisé pour les entreprises tech en croissance.",
    
    # Rentabilité
    'roe': "ROE (Return on Equity) = Bénéfice net / Capitaux propres. Mesure combien l'entreprise génère de profit pour chaque euro investi par les actionnaires. ROE > 15% est généralement bon. Attention : un ROE très élevé peut venir d'un endettement excessif.",
    'roa': "ROA (Return on Assets) = Bénéfice net / Total des actifs. Mesure l'efficacité de l'utilisation de TOUS les actifs (pas seulement les capitaux propres). Plus pertinent pour comparer des entreprises avec des niveaux d'endettement différents.",
    'gross_margin': "Marge brute = (CA - Coûts directs) / CA. Représente le pourcentage du CA restant après les coûts de production/achat. Une marge brute élevée indique un pouvoir de pricing ou des coûts maîtrisés.",
    'operating_margin': "Marge opérationnelle = Résultat opérationnel / CA. Inclut tous les coûts d'exploitation (salaires, marketing, R&D...). Mesure la rentabilité du cœur de métier avant intérêts et impôts.",
    'net_margin': "Marge nette = Bénéfice net / CA. Le pourcentage du CA qui se transforme réellement en profit après TOUTES les charges (opérationnelles, financières, fiscales). C'est le \"bottom line\".",
    
    # Santé financière
    'debt_equity': "Dette/Equity = Dette totale / Capitaux propres. Mesure le levier financier. Ratio > 1 signifie plus de dette que de fonds propres. Un ratio élevé augmente le risque mais peut booster le ROE.",
    'current_ratio': "Current Ratio = Actifs court terme / Passifs court terme. Mesure la capacité à payer les dettes à moins d'un an. Ratio > 1 = l'entreprise peut couvrir ses obligations. Ratio > 2 peut indiquer une gestion inefficace du cash.",
    'quick_ratio': "Quick Ratio = (Actifs CT - Stocks) / Passifs CT. Plus conservateur que le Current Ratio car exclut les stocks (moins liquides). Ratio > 1 indique une bonne liquidité immédiate.",
    'interest_coverage': "Couverture des intérêts = EBIT / Charges d'intérêts. Mesure combien de fois l'entreprise peut payer ses intérêts avec son résultat opérationnel. Ratio < 2 est préoccupant.",
    'total_debt': "Montant total de la dette financière (court et long terme). À comparer avec les capitaux propres et la capacité de remboursement (cash flow).",
    'total_cash': "Trésorerie et équivalents de trésorerie. Argent immédiatement disponible. Important pour la flexibilité financière et les opportunités d'investissement.",
    'free_cash_flow': "FCF = Cash flow opérationnel - Investissements (CapEx). C'est l'argent réellement disponible après avoir maintenu/développé l'activité. Peut servir aux dividendes, rachats d'actions, acquisitions ou désendettement.",
    
    # Croissance
    'revenue_growth': "Croissance du chiffre d'affaires par rapport à la même période l'an dernier. Indicateur clé de la dynamique commerciale. Une croissance > 10% est généralement considérée comme forte.",
    'earnings_growth': "Croissance du bénéfice net par rapport à l'an dernier. Peut être volatile. Une croissance des bénéfices supérieure à celle du CA indique une amélioration des marges.",
    'eps_trailing': "EPS (Earnings Per Share) sur les 12 derniers mois. Bénéfice net divisé par le nombre d'actions. Base du calcul du P/E. Suivre son évolution est crucial.",
    'eps_forward': "EPS prévisionnel pour les 12 prochains mois (consensus analystes). Si EPS forward > EPS trailing, les analystes anticipent une croissance des bénéfices.",
    
    # Dividendes
    'dividend_yield': "Rendement du dividende = Dividende annuel / Prix de l'action. Représente le revenu passif en pourcentage. Un yield > 5% peut être attractif mais aussi signaler un prix déprimé ou un dividende non soutenable.",
    'dividend_rate': "Montant en dollars/euros du dividende versé par action sur une année. À multiplier par le nombre d'actions détenues pour connaître le revenu total.",
    'payout_ratio': "Payout = Dividendes versés / Bénéfice net. Pourcentage des bénéfices distribués. Ratio > 80% peut être risqué (peu de marge de sécurité). Ratio < 40% laisse de la place pour la croissance du dividende.",
    'five_year_avg_dividend_yield': "Moyenne du rendement du dividende sur 5 ans. Permet de voir si le yield actuel est historiquement haut (opportunité ?) ou bas.",
}