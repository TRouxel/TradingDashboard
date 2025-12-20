# db_manager.py
"""
Gestionnaire de base de données PostgreSQL.
Gère la connexion et l'initialisation des tables.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (en local)
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """Crée et retourne une connexion à la base de données."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL non définie. Vérifiez votre fichier .env ou les variables d'environnement.")
    
    # Render utilise parfois 'postgres://' au lieu de 'postgresql://'
    db_url = DATABASE_URL
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return psycopg2.connect(db_url)


def init_database():
    """Initialise les tables de la base de données si elles n'existent pas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Table des actifs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(255),
                asset_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table des données historiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_data (
                id SERIAL PRIMARY KEY,
                asset_id INTEGER REFERENCES assets(id),
                date DATE NOT NULL,
                open DECIMAL(20, 6),
                high DECIMAL(20, 6),
                low DECIMAL(20, 6),
                close DECIMAL(20, 6),
                volume BIGINT,
                stochastic_k DECIMAL(10, 4),
                stochastic_d DECIMAL(10, 4),
                rsi DECIMAL(10, 4),
                pattern VARCHAR(100),
                recommendation VARCHAR(20),
                conviction INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(asset_id, date)
            )
        ''')
        
        # Table des actifs utilisateur (pour la liste personnalisée)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_assets (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(20) UNIQUE NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table de configuration utilisateur (optionnel, pour sauvegarder les configs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_config (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("✅ Base de données initialisée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def check_database_connection():
    """Vérifie que la connexion à la base de données fonctionne."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, "Connexion OK"
    except Exception as e:
        return False, str(e)


# Initialiser la base de données au chargement du module
if DATABASE_URL:
    try:
        init_database()
    except Exception as e:
        print(f"⚠️ Impossible d'initialiser la base de données: {e}")
else:
    print("⚠️ DATABASE_URL non définie - mode sans base de données")