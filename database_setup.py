# database_setup.py
import sqlite3

def setup_database():
    """Crée la base de données SQLite et les tables si elles n'existent pas."""
    conn = sqlite3.connect('my_assets.db')
    cursor = conn.cursor()

    # Table pour les actifs (actions, cryptos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL UNIQUE,
            name TEXT
        )
    ''')

    # Table pour les données historiques et les indicateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_data (
            asset_id INTEGER,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            stochastic_k REAL,
            stochastic_d REAL,
            rsi REAL,
            pattern TEXT,
            recommendation TEXT,
            conviction INTEGER,
            FOREIGN KEY (asset_id) REFERENCES assets (id),
            PRIMARY KEY (asset_id, date)
        )
    ''')

    print("Base de données et tables créées avec succès.")
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()    