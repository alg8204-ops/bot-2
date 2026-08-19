"""
Ejecucion y gestion de ordenes.
  - "paper": simula la orden localmente, no toca el exchange. SIEMPRE seguro.
  - "live": envia una orden real al exchange. Requiere API key con permiso de trading
            (NUNCA de retiro) y que el sistema ya haya sido validado en paper trading.

Incluye el cierre de posiciones por stop-loss/take-profit, que es lo que permite que el
limite de perdida diaria del RiskManager funcione de verdad (antes no existia: una vez
abierta, la posicion nunca se cerraba ni se registraba su resultado).
"""
from datetime import datetime
from typing import Optional


class Executor:
    def __init__(self, cfg, data_feed):
        self.cfg = cfg
        self.data_feed = data_feed
        self.open_position: Optional[dict] = None
        self.last_closed: Optional[dict] = None

    def execute(self, signal, size: float):
        if signal.action == "none" or size <= 0:
            return None
        if self.open_position is not None:
            # Nunca abrir una segunda posicion mientras hay una en curso.
            return None

        order = {
            "timestamp": datetime.utcnow().isoformat(),
            "side": signal.action,
            "entry": signal.entry,
            "stop": signal.stop,
            "target": signal.target,
            "size": size,
            "mode": self.cfg.execution_mode,
        }

        if self.cfg.execution_mode == "paper":
            self.open_position = order
            return order

        elif self.cfg.execution_mode == "live":
            if not self.cfg.api_key or not self.cfg.api_secret:
                raise RuntimeError(
                    "execution_mode='live' pero no hay API key/secret configurados. "
                    "Define EXCHANGE_API_KEY y EXCHANGE_API_SECRET, y confirma que entiendes "
                    "que esto colocara ordenes reales con dinero real."
                )
            exchange = self.data_feed._exchange
            side = "buy" if signal.action == "long" else "sell"
            real_order = exchange.create_order(
                symbol=self.cfg.symbol, type="market", side=side, amount=size
            )
            self.open_position = order
            return real_order

        raise ValueError(f"execution_mode desconocido: {self.cfg.execution_mode}")

    def check_and_close_position(self, current_price: float) -> Optional[float]:
        """Si el precio actual toco el stop o el target de la posicion abierta, la cierra
        y devuelve el PnL realizado (positivo o negativo). Si no toco ninguno todavia,
        devuelve None y la posicion sigue abierta tal cual."""
        pos = self.open_position
        if pos is None:
            return None

        side, entry, stop, target, size = pos["side"], pos["entry"], pos["stop"], pos["target"], pos["size"]
        hit_stop = (side == "long" and current_price <= stop) or (side == "short" and current_price >= stop)
        hit_target = (side == "long" and current_price >= target) or (side == "short" and current_price <= target)

        if not (hit_stop or hit_target):
            return None

        exit_price = stop if hit_stop else target
        pnl = (exit_price - entry) * size if side == "long" else (entry - exit_price) * size

        if self.cfg.execution_mode == "live":
            exchange = self.data_feed._exchange
            closing_side = "sell" if side == "long" else "buy"
            exchange.create_order(symbol=self.cfg.symbol, type="market", side=closing_side, amount=size)

        pos["closed_at"] = datetime.utcnow().isoformat()
        pos["exit_price"] = exit_price
        pos["pnl"] = pnl
        pos["result"] = "stop" if hit_stop else "target"

        self.last_closed = pos
        self.open_position = None
        return pnl

    def load_state(self, open_position: Optional[dict]):
        self.open_position = open_position

    def export_state(self) -> Optional[dict]:
        return self.open_position
