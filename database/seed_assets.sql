-- database/seed_assets.sql
-- Insertion des actifs par défaut

-- D'abord, récupérer les IDs des catégories
-- Puis insérer les actifs

-- ============================================================
-- INSERTION DES ACTIFS PAR DÉFAUT
-- ============================================================

-- INDICES MAJEURS
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT '^GSPC', 'S&P 500', id, 'USD', '$', 'INDEX', 1 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- ETF INDICES (UCITS EUR)
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'IWDA.AS', 'iShares MSCI World', id, 'EUR', '€', 'ETF', 10 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'EUNL.DE', 'iShares MSCI World UCITS', id, 'EUR', '€', 'ETF', 11 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'CW8.PA', 'Amundi MSCI World', id, 'EUR', '€', 'ETF', 12 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'EWLD.PA', 'Lyxor MSCI World', id, 'EUR', '€', 'ETF', 13 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'MWRD.DE', 'Amundi MSCI World II', id, 'EUR', '€', 'ETF', 14 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'SXR8.DE', 'iShares S&P 500 UCITS', id, 'EUR', '€', 'ETF', 15 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'VUAA.DE', 'Vanguard S&P 500 UCITS', id, 'EUR', '€', 'ETF', 16 FROM asset_categories WHERE category_key = 'indices'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- BLUE CHIPS US
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'AAPL', 'Apple', id, 'USD', '$', 'EQUITY', 'Technology', 100 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'MSFT', 'Microsoft', id, 'USD', '$', 'EQUITY', 'Technology', 101 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'GOOGL', 'Alphabet (Google)', id, 'USD', '$', 'EQUITY', 'Technology', 102 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'JNJ', 'Johnson & Johnson', id, 'USD', '$', 'EQUITY', 'Healthcare', 103 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'KO', 'Coca-Cola', id, 'USD', '$', 'EQUITY', 'Consumer Defensive', 104 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'PG', 'Procter & Gamble', id, 'USD', '$', 'EQUITY', 'Consumer Defensive', 105 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'PEP', 'PepsiCo', id, 'USD', '$', 'EQUITY', 'Consumer Defensive', 106 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'MCD', 'McDonald''s', id, 'USD', '$', 'EQUITY', 'Consumer Cyclical', 107 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'WMT', 'Walmart', id, 'USD', '$', 'EQUITY', 'Consumer Defensive', 108 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'JPM', 'JPMorgan Chase', id, 'USD', '$', 'EQUITY', 'Financial Services', 109 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'V', 'Visa', id, 'USD', '$', 'EQUITY', 'Financial Services', 110 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'MA', 'Mastercard', id, 'USD', '$', 'EQUITY', 'Financial Services', 111 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'UNH', 'UnitedHealth', id, 'USD', '$', 'EQUITY', 'Healthcare', 112 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'HD', 'Home Depot', id, 'USD', '$', 'EQUITY', 'Consumer Cyclical', 113 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'DIS', 'Disney', id, 'USD', '$', 'EQUITY', 'Communication Services', 114 FROM asset_categories WHERE category_key = 'blue_chip_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- TECH VOLATILE US
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'TSLA', 'Tesla', id, 'USD', '$', 'EQUITY', 'Consumer Cyclical', 200 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'NVDA', 'NVIDIA', id, 'USD', '$', 'EQUITY', 'Technology', 201 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'AMD', 'AMD', id, 'USD', '$', 'EQUITY', 'Technology', 202 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'AMZN', 'Amazon', id, 'USD', '$', 'EQUITY', 'Consumer Cyclical', 203 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'META', 'Meta (Facebook)', id, 'USD', '$', 'EQUITY', 'Communication Services', 204 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'NFLX', 'Netflix', id, 'USD', '$', 'EQUITY', 'Communication Services', 205 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'PLTR', 'Palantir', id, 'USD', '$', 'EQUITY', 'Technology', 206 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'COIN', 'Coinbase', id, 'USD', '$', 'EQUITY', 'Financial Services', 207 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'SQ', 'Block (Square)', id, 'USD', '$', 'EQUITY', 'Technology', 208 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'SHOP', 'Shopify', id, 'USD', '$', 'EQUITY', 'Technology', 209 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'ROKU', 'Roku', id, 'USD', '$', 'EQUITY', 'Communication Services', 210 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'SNOW', 'Snowflake', id, 'USD', '$', 'EQUITY', 'Technology', 211 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'CRWD', 'CrowdStrike', id, 'USD', '$', 'EQUITY', 'Technology', 212 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'DDOG', 'Datadog', id, 'USD', '$', 'EQUITY', 'Technology', 213 FROM asset_categories WHERE category_key = 'tech_volatile_us'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- BLUE CHIPS EUR
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'AI.PA', 'Air Liquide', id, 'EUR', '€', 'EQUITY', 'Basic Materials', 300 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'MC.PA', 'LVMH', id, 'EUR', '€', 'EQUITY', 'Consumer Cyclical', 301 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'OR.PA', 'L''Oréal', id, 'EUR', '€', 'EQUITY', 'Consumer Defensive', 302 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'SAN.PA', 'Sanofi', id, 'EUR', '€', 'EQUITY', 'Healthcare', 303 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'AIR.PA', 'Airbus', id, 'EUR', '€', 'EQUITY', 'Industrials', 304 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'SAP.DE', 'SAP', id, 'EUR', '€', 'EQUITY', 'Technology', 305 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, sector, display_order)
SELECT 'ASML.AS', 'ASML', id, 'EUR', '€', 'EQUITY', 'Technology', 306 FROM asset_categories WHERE category_key = 'blue_chip_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- FOREX EUR
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'USDEUR=X', 'Dollar US', id, 'EUR', '€', 'CURRENCY', 400 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'AUDEUR=X', 'Dollar Australien', id, 'EUR', '€', 'CURRENCY', 401 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'GBPEUR=X', 'Livre Sterling', id, 'EUR', '€', 'CURRENCY', 402 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'CHFEUR=X', 'Franc Suisse', id, 'EUR', '€', 'CURRENCY', 403 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'JPYEUR=X', 'Yen Japonais', id, 'EUR', '€', 'CURRENCY', 404 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'CADEUR=X', 'Dollar Canadien', id, 'EUR', '€', 'CURRENCY', 405 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'NZDEUR=X', 'Dollar Néo-Zélandais', id, 'EUR', '€', 'CURRENCY', 406 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'SEKEUR=X', 'Couronne Suédoise', id, 'EUR', '€', 'CURRENCY', 407 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'NOKEUR=X', 'Couronne Norvégienne', id, 'EUR', '€', 'CURRENCY', 408 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'SGDEUR=X', 'Dollar Singapourien', id, 'EUR', '€', 'CURRENCY', 409 FROM asset_categories WHERE category_key = 'forex_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- MÉTAUX PRÉCIEUX EUR
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT '4GLD.DE', 'Xetra-Gold', id, 'EUR', '€', 'ETF', 500 FROM asset_categories WHERE category_key = 'precious_metals_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'VZLE.DE', 'WisdomTree Physical Silver EUR', id, 'EUR', '€', 'ETF', 501 FROM asset_categories WHERE category_key = 'precious_metals_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

-- CRYPTO EUR
INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'BTC-EUR', 'Bitcoin', id, 'EUR', '€', 'CRYPTOCURRENCY', 600 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'ETH-EUR', 'Ethereum', id, 'EUR', '€', 'CRYPTOCURRENCY', 601 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'SOL-EUR', 'Solana', id, 'EUR', '€', 'CRYPTOCURRENCY', 602 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'XRP-EUR', 'Ripple (XRP)', id, 'EUR', '€', 'CRYPTOCURRENCY', 603 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'ADA-EUR', 'Cardano', id, 'EUR', '€', 'CRYPTOCURRENCY', 604 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'DOGE-EUR', 'Dogecoin', id, 'EUR', '€', 'CRYPTOCURRENCY', 605 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'DOT-EUR', 'Polkadot', id, 'EUR', '€', 'CRYPTOCURRENCY', 606 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'LINK-EUR', 'Chainlink', id, 'EUR', '€', 'CRYPTOCURRENCY', 607 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'AVAX-EUR', 'Avalanche', id, 'EUR', '€', 'CRYPTOCURRENCY', 608 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'MATIC-EUR', 'Polygon', id, 'EUR', '€', 'CRYPTOCURRENCY', 609 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'UNI-EUR', 'Uniswap', id, 'EUR', '€', 'CRYPTOCURRENCY', 610 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'LTC-EUR', 'Litecoin', id, 'EUR', '€', 'CRYPTOCURRENCY', 611 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'ATOM-EUR', 'Cosmos', id, 'EUR', '€', 'CRYPTOCURRENCY', 612 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'NEAR-EUR', 'Near Protocol', id, 'EUR', '€', 'CRYPTOCURRENCY', 613 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'AAVE-EUR', 'Aave', id, 'EUR', '€', 'CRYPTOCURRENCY', 614 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;

INSERT INTO assets (ticker, name, category_id, currency, currency_symbol, quote_type, display_order)
SELECT 'SHIB-EUR', 'Shiba Inu', id, 'EUR', '€', 'CRYPTOCURRENCY', 615 FROM asset_categories WHERE category_key = 'crypto_eur'
ON CONFLICT (ticker) DO UPDATE SET name = EXCLUDED.name, category_id = EXCLUDED.category_id;