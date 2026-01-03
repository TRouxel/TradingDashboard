# components/__init__.py
from .charts import (
    create_price_chart,
    create_recommendations_chart,
    create_trend_chart,
    create_macd_chart,
    create_volume_chart,
    create_rsi_chart,
    create_stochastic_chart,
    create_patterns_chart,
    create_quarterly_chart
)
from .tables import (
    create_technical_indicators_table,
    create_ratio_table,
    create_fundamental_details
)
from .indicators import calculate_indicator_contributions
from .performance_charts import (
    create_indicator_performance_chart,
    create_accuracy_badges,
    create_performance_section,
    create_performance_summary_cards,
    create_combination_ranking_table,
    create_global_performance_summary,
    HORIZON_COLORS,
    HORIZON_NAMES
)
from .strategy_charts import (
    create_hold_and_sell_chart,
    create_buy_on_divergence_chart,
    create_strategy_stats_table,
    create_strategies_section,
    HOLDING_COLORS
)
from .summary_table import (
    create_assets_summary_table,
    create_summary_section
)