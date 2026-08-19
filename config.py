"""
Configuracion central del sistema de trading.
Ajusta estos parametros segun tu capital, tolerancia al riesgo y exchange.
"""
import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # --- Exchange y mercado ---
    exchange_id: str = "binance"          # cualquier exchange soportado por ccxt
    symbol: str = "BTC/USDT"
    timeframe_entry: str = "15m"          # timing de entrada
    timeframe_trend: str = "4h"           # tendencia macro

    # --- Modo de operacion ---
    # Controlable por variable de entorno para poder cambiar de fase sin tocar codigo.
    # Se usa "or" (no el default de field()) para que una variable vacia tambien caiga
    # de forma segura al modo mock/paper, en vez de romperse.
    # data_mode: "mock" (datos sinteticos, sin red) | "live" (datos reales via ccxt, no requiere API key)
    data_mode: str = field(default_factory=lambda: os.getenv("DATA_MODE") or "mock")
    # execution_mode: "paper" (simulado, SIEMPRE seguro) | "live" (ordenes reales, requiere API key de trading)
    execution_mode: str = field(default_factory=lambda: os.getenv("EXECUTION_MODE") or "paper")

    # --- Credenciales (nunca hardcodear; se leen de variables de entorno) ---
    api_key: str = field(default_factory=lambda: os.getenv("EXCHANGE_API_KEY", ""))
    api_secret: str = field(default_factory=lambda: os.getenv("EXCHANGE_API_SECRET", ""))

    # --- Indicadores tecnicos ---
    ema_fast: int = 20
    ema_slow: int = 50
    ema_trend: int = 200
    rsi_period: int = 14
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std: float = 2.0

    # --- Gestion de riesgo ---
    capital_total: float = 1000.0          # capital asignado a este sistema (USDT)
    risk_per_trade_pct: float = 1.0        # % del capital arriesgado por operacion
    max_daily_loss_pct: float = 4.0        # % de perdida diaria maxima -> el bot se detiene
    min_risk_reward: float = 1.5           # ratio riesgo/beneficio minimo para tomar una entrada
    max_leverage: float = 2.0              # apalancamiento maximo permitido (1.0 = sin apalancamiento)

    # --- Fundamental ---
    funding_rate_extreme: float = 0.0005   # ~0.05% se considera funding "extremo"

    # --- Operativa ---
    loop_interval_seconds: int = 60        # cada cuanto revisa el mercado
    confluence_min_score: int = 4          # puntos minimos del checklist (sobre 5) para operar

    # --- Alertas opcionales (para saber que hace el bot sin estar presente) ---
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))
