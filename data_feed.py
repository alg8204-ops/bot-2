"""
Obtencion de datos de mercado. Dos modos:
  - "mock": genera datos sinteticos (random walk) para probar el sistema sin conexion.
  - "live": usa ccxt para obtener datos REALES de mercado (endpoints publicos, sin API key
            para lectura; solo la ejecucion de ordenes reales requiere API key).
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class DataFeed:
    def __init__(self, cfg):
        self.cfg = cfg
        self._exchange = None
        self._mock_last_price = 60000.0  # continua entre llamadas para simular un mercado coherente
        if cfg.data_mode == "live":
            import ccxt  # se importa solo si hace falta, para no exigir la libreria en modo mock
            self._exchange = getattr(ccxt, cfg.exchange_id)()

    def fetch_ohlcv(self, timeframe: str, limit: int = 300) -> pd.DataFrame:
        if self.cfg.data_mode == "mock":
            return self._mock_ohlcv(limit)
        ohlcv = self._exchange.fetch_ohlcv(self.cfg.symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def fetch_funding_rate(self) -> float:
        if self.cfg.data_mode == "mock":
            return float(np.random.uniform(-0.0006, 0.0006))
        try:
            fr = self._exchange.fetch_funding_rate(self.cfg.symbol)
            return float(fr.get("fundingRate", 0.0) or 0.0)
        except Exception:
            return 0.0  # no todos los exchanges/mercados spot tienen funding rate

    def fetch_open_interest(self) -> float:
        if self.cfg.data_mode == "mock":
            return float(np.random.uniform(1e9, 2e9))
        try:
            oi = self._exchange.fetch_open_interest(self.cfg.symbol)
            return float(oi.get("openInterestAmount", 0.0) or 0.0)
        except Exception:
            return 0.0

    def _mock_ohlcv(self, limit: int) -> pd.DataFrame:
        rng = np.random.default_rng()
        now = datetime.utcnow()
        prices = [self._mock_last_price]
        for _ in range(limit - 1):
            prices.append(prices[-1] * (1 + rng.normal(0, 0.002)))
        self._mock_last_price = prices[-1]
        rows = []
        for i, close in enumerate(prices):
            o = close * (1 + rng.normal(0, 0.0005))
            h = max(o, close) * (1 + abs(rng.normal(0, 0.0008)))
            l = min(o, close) * (1 - abs(rng.normal(0, 0.0008)))
            v = abs(rng.normal(500, 150))
            ts = now - timedelta(minutes=(limit - i))
            rows.append([ts, o, h, l, close, v])
        return pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
