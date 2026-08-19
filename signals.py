"""
Genera senales de entrada combinando tecnico + fundamental, siguiendo el checklist
de confluencia del marco original (documento de estrategia).
"""
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TradeSignal:
    action: str          # "long" | "short" | "none"
    score: int
    reasons: List[str] = field(default_factory=list)
    entry: Optional[float] = None
    stop: Optional[float] = None
    target: Optional[float] = None


def generate_signal(df_entry, df_trend, fundamentals, cfg) -> TradeSignal:
    last = df_entry.iloc[-1]
    trend_last = df_trend.iloc[-1]

    reasons = []
    score = 0

    # 1. Tendencia mayor (4H)
    trend_up = trend_last["close"] > trend_last["ema_trend"]
    trend_down = trend_last["close"] < trend_last["ema_trend"]
    if trend_up:
        reasons.append("Tendencia 4H alcista")
        score += 1
    elif trend_down:
        reasons.append("Tendencia 4H bajista")
        score += 1

    # 2. Precio en zona tecnica clave (cerca de EMA20)
    near_ema20 = abs(last["close"] - last["ema_fast"]) / last["close"] < 0.003
    if near_ema20:
        reasons.append("Precio cerca de EMA20")
        score += 1

    # 3. RSI saliendo de zona extrema
    rsi_bullish = cfg.rsi_oversold < last["rsi"] < cfg.rsi_oversold + 10
    rsi_bearish = cfg.rsi_overbought - 10 < last["rsi"] < cfg.rsi_overbought
    if rsi_bullish or rsi_bearish:
        reasons.append("RSI saliendo de zona extrema")
        score += 1

    # 4. Funding rate no extremo en contra
    if not fundamentals.funding_extreme:
        reasons.append("Funding rate no esta en extremo")
        score += 1
    else:
        reasons.append(f"Funding rate extremo ({fundamentals.funding_bias})")

    # 5. Fear & Greed Index (gratis, Alternative.me): evita comprar en euforia extrema
    #    y evita vender en panico extremo -- son las zonas donde mas se revierte el precio.
    fg = fundamentals.fear_greed_value
    fg_blocks_long = fg is not None and fg >= 80
    fg_blocks_short = fg is not None and fg <= 20
    if fg is None:
        reasons.append("Fear & Greed no disponible (sin conexion)")
    elif not (fg_blocks_long or fg_blocks_short):
        score += 1
        reasons.append(f"Fear & Greed neutral ({fg}, {fundamentals.fear_greed_classification})")
    else:
        reasons.append(f"Fear & Greed en extremo ({fg}, {fundamentals.fear_greed_classification})")

    # 6. Evento macro de alto impacto (placeholder si no hay calendario conectado)
    if fundamentals.high_impact_event_soon is None:
        reasons.append("Calendario macro no conectado (revisar manualmente)")
    elif not fundamentals.high_impact_event_soon:
        score += 1
        reasons.append("Sin eventos macro de alto impacto inminentes")

    action = "none"
    if score >= cfg.confluence_min_score:
        if trend_up and fundamentals.funding_bias != "long_crowded" and not fg_blocks_long:
            action = "long"
        elif trend_down and fundamentals.funding_bias != "short_crowded" and not fg_blocks_short:
            action = "short"

    sig = TradeSignal(action=action, score=score, reasons=reasons)

    if action != "none":
        entry = float(last["close"])
        vol = df_entry["close"].pct_change().rolling(14).std().iloc[-1]
        vol = vol if vol and vol > 0 else 0.003
        atr_proxy = entry * vol
        if action == "long":
            sig.entry = entry
            sig.stop = entry - 1.5 * atr_proxy
            sig.target = entry + 1.5 * cfg.min_risk_reward * atr_proxy
        else:
            sig.entry = entry
            sig.stop = entry + 1.5 * atr_proxy
            sig.target = entry - 1.5 * cfg.min_risk_reward * atr_proxy

    return sig
