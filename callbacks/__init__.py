# callbacks/__init__.py
from .config_callbacks import register_config_callbacks
from .asset_callbacks import register_asset_callbacks
from .dashboard_callbacks import register_dashboard_callbacks
from .fundamental_callbacks import register_fundamental_callbacks
from .performance_callbacks import register_performance_callbacks
from .strategy_callbacks import register_strategy_callbacks


def register_all_callbacks(app):
    """Enregistre tous les callbacks de l'application."""
    register_config_callbacks(app)
    register_asset_callbacks(app)
    register_dashboard_callbacks(app)
    register_fundamental_callbacks(app)
    register_performance_callbacks(app)
    register_strategy_callbacks(app)