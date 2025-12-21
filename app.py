# app.py
"""
Point d'entrée principal de l'application Dash.
"""
import dash
import dash_bootstrap_components as dbc

# === INITIALISATION DE LA BASE DE DONNÉES ===
try:
    from db_manager import init_database, check_database_connection
    db_ok, db_msg = check_database_connection()
    if db_ok:
        print("✅ Connexion à PostgreSQL établie")
        init_database()
    else:
        print(f"⚠️ Impossible de se connecter à PostgreSQL: {db_msg}")
except Exception as e:
    print(f"⚠️ Erreur d'initialisation DB: {e}")

from layouts import create_main_layout
from callbacks import register_all_callbacks


# --- Initialisation de l'application Dash ---
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CYBORG], 
    suppress_callback_exceptions=True
)
server = app.server

# --- Layout ---
app.layout = create_main_layout()

# --- Callbacks ---
register_all_callbacks(app)


if __name__ == '__main__':
    app.run(debug=True)