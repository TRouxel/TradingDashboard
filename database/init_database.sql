-- database/init_database.sql
-- Script d'initialisation de la base de données locale
-- À exécuter une seule fois pour créer la structure

-- Création de la base de données (à exécuter en tant que superuser)
-- CREATE DATABASE trading_dashboard;

-- Connexion à la base trading_dashboard avant d'exécuter le reste

-- ============================================================
-- TABLE: asset_categories
-- Catégories/Classes d'actifs avec leurs horaires de clôture
-- ============================================================
CREATE TABLE IF NOT EXISTS asset_categories (
    id SERIAL PRIMARY KEY,
    category_key VARCHAR(50) UNIQUE NOT NULL,  -- Ex: 'crypto_eur', 'forex_eur', 'blue_chip_us'
    name VARCHAR(100) NOT NULL,                 -- Ex: 'Crypto EUR', 'Forex vs EUR'
    description TEXT,
    icon VARCHAR(10),                           -- Emoji pour l'affichage
    color VARCHAR(20),                          -- Couleur hex pour l'UI
    
    -- Horaires de clôture (heure française / Europe/Paris)
    market_close_time TIME,                     -- Heure de clôture du marché
    market_close_timezone VARCHAR(50) DEFAULT 'Europe/Paris',
    trading_days VARCHAR(20) DEFAULT 'Mon-Fri', -- Jours de trading (Mon-Fri, Mon-Sun, etc.)
    
    -- Notes sur les horaires
    close_time_notes TEXT,                      -- Explications supplémentaires
    
    -- Configuration des indicateurs (JSON pour flexibilité)
    weight_modifiers JSONB DEFAULT '{}',
    combination_modifiers JSONB DEFAULT '{}',
    decision_modifiers JSONB DEFAULT '{}',
    rsi_thresholds JSONB DEFAULT '{"oversold": 30, "overbought": 70}',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: assets
-- Liste de tous les actifs suivis
-- ============================================================
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(30) UNIQUE NOT NULL,         -- Symbole Yahoo Finance (ex: 'BTC-EUR', 'AAPL')
    name VARCHAR(255),                          -- Nom complet (ex: 'Bitcoin', 'Apple Inc.')
    
    -- Référence à la catégorie
    category_id INTEGER REFERENCES asset_categories(id) ON DELETE SET NULL,
    
    -- Devise
    currency VARCHAR(10) NOT NULL DEFAULT 'USD', -- EUR, USD, GBP, etc.
    currency_symbol VARCHAR(5) DEFAULT '$',      -- €, $, £, etc.
    
    -- Métadonnées Yahoo Finance
    quote_type VARCHAR(50),                      -- EQUITY, CRYPTOCURRENCY, CURRENCY, ETF, INDEX, FUTURE
    exchange VARCHAR(50),                        -- Bourse (NASDAQ, NYSE, etc.)
    sector VARCHAR(100),                         -- Secteur (pour les actions)
    industry VARCHAR(100),                       -- Industrie (pour les actions)
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,              -- Actif dans le suivi
    display_order INTEGER DEFAULT 0,             -- Ordre d'affichage
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_data_fetch TIMESTAMP                    -- Dernière récupération de données
);

-- ============================================================
-- TABLE: historical_data
-- Données historiques OHLCV + indicateurs calculés
-- ============================================================
CREATE TABLE IF NOT EXISTS historical_data (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    -- OHLCV
    open DECIMAL(20, 8),
    high DECIMAL(20, 8),
    low DECIMAL(20, 8),
    close DECIMAL(20, 8),
    volume BIGINT,
    
    -- Indicateurs techniques
    rsi DECIMAL(10, 4),
    stochastic_k DECIMAL(10, 4),
    stochastic_d DECIMAL(10, 4),
    macd DECIMAL(15, 6),
    macd_signal DECIMAL(15, 6),
    macd_histogram DECIMAL(15, 6),
    
    -- Moyennes mobiles
    sma_20 DECIMAL(20, 8),
    sma_50 DECIMAL(20, 8),
    sma_200 DECIMAL(20, 8),
    ema_12 DECIMAL(20, 8),
    ema_26 DECIMAL(20, 8),
    
    -- Bollinger Bands
    bb_upper DECIMAL(20, 8),
    bb_middle DECIMAL(20, 8),
    bb_lower DECIMAL(20, 8),
    bb_percent DECIMAL(10, 6),
    bb_signal VARCHAR(20),
    
    -- ADX/DI
    adx DECIMAL(10, 4),
    di_plus DECIMAL(10, 4),
    di_minus DECIMAL(10, 4),
    
    -- Tendance et signaux
    trend VARCHAR(30),
    rsi_divergence VARCHAR(20),
    pattern VARCHAR(100),
    pattern_direction VARCHAR(20),
    
    -- Recommandation calculée
    recommendation VARCHAR(20),
    conviction INTEGER,
    active_combinations TEXT[],  -- Array des combinaisons actives
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contrainte d'unicité
    UNIQUE(asset_id, date)
);

-- ============================================================
-- TABLE: user_preferences
-- Préférences utilisateur (config sauvegardée)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEX pour les performances
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_assets_ticker ON assets(ticker);
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category_id);
CREATE INDEX IF NOT EXISTS idx_assets_active ON assets(is_active);
CREATE INDEX IF NOT EXISTS idx_historical_asset_date ON historical_data(asset_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_historical_date ON historical_data(date DESC);
CREATE INDEX IF NOT EXISTS idx_historical_divergence ON historical_data(rsi_divergence) WHERE rsi_divergence IS NOT NULL;

-- ============================================================
-- FONCTION: Mise à jour automatique du timestamp updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
DROP TRIGGER IF EXISTS update_asset_categories_updated_at ON asset_categories;
CREATE TRIGGER update_asset_categories_updated_at
    BEFORE UPDATE ON asset_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_assets_updated_at ON assets;
CREATE TRIGGER update_assets_updated_at
    BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();