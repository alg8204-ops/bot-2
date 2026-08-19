"""
Senales fundamentales.

100% gratis, sin API key:
  - funding_rate / open_interest: directo del exchange via ccxt (data_feed.py)
  - fear_greed: Alternative.me Crypto Fear & Greed Index (https://alternative.me/crypto/fear-and-greed-index/)

Sin equivalente gratuito real:
  - exchange_netflow / whale tracking: requiere wallets etiquetadas, que es el valor
    que venden Glassnode/CryptoQuant de pago. Queda como TODO explicito en vez de simularse.
  - high_impact_event_soon (calendario FOMC/CPI/NFP): no hay una API gratuita fiable de
    calendario economico. Alternativa gratis realista: las fechas de FOMC se publican con
    meses de antelacion en federalreserve.gov, puedes cargarlas a mano (ver IMPLEMENTACION.md).
"""
import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

_fng_cache = {"data": None, "fetched_at": None}
_FNG_CACHE_SECONDS = 3600  # el indice se actualiza ~1 vez al dia, no hace falta pedirlo mas seguido


@dataclass
class FundamentalSnapshot:
    funding_rate: float
    open_interest: float
    funding_extreme: bool
    funding_bias: str  # "long_crowded", "short_crowded", "neutral"

    fear_greed_value: Optional[int] = None            # 0-100, gratis via Alternative.me
    fear_greed_classification: Optional[str] = None   # ej. "Extreme Fear", "Greed"

    # Sin equivalente gratuito real (ver docstring del modulo).
    exchange_netflow: Optional[float] = None
    high_impact_event_soon: Optional[bool] = None


def fetch_fear_greed_index() -> Optional[dict]:
    """Devuelve {'value': int, 'classification': str} o None si no hay conexion.
    Cachea 1 hora para no golpear la API gratuita mas de lo necesario."""
    now = datetime.utcnow()
    cached, fetched_at = _fng_cache["data"], _fng_cache["fetched_at"]
    if cached is not None and fetched_at is not None:
        if (now - fetched_at).total_seconds() < _FNG_CACHE_SECONDS:
            return cached
    try:
        req = urllib.request.Request(
            "https://api.alternative.me/fng/?limit=1",
            headers={"User-Agent": "btc-bot/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read())
        entry = payload["data"][0]
        result = {"value": int(entry["value"]), "classification": entry["value_classification"]}
        _fng_cache["data"], _fng_cache["fetched_at"] = result, now
        return result
    except Exception:
        return cached  # si falla, usa el ultimo valor conocido (o None si nunca hubo exito)


def build_fundamental_snapshot(cfg, funding_rate: float, open_interest: float) -> FundamentalSnapshot:
    extreme = abs(funding_rate) >= cfg.funding_rate_extreme
    if funding_rate >= cfg.funding_rate_extreme:
        bias = "long_crowded"     # exceso de largos apalancados -> riesgo de long squeeze
    elif funding_rate <= -cfg.funding_rate_extreme:
        bias = "short_crowded"
    else:
        bias = "neutral"

    fng = fetch_fear_greed_index()

    return FundamentalSnapshot(
        funding_rate=funding_rate,
        open_interest=open_interest,
        funding_extreme=extreme,
        funding_bias=bias,
        fear_greed_value=fng["value"] if fng else None,
        fear_greed_classification=fng["classification"] if fng else None,
    )
