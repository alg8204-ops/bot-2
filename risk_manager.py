"""
Gestion de riesgo: tamano de posicion, limite de perdida diaria, kill switch.
Esta es la parte mas importante del sistema: un bug aqui es el que mas dinero puede costar
precisamente porque el bot opera sin supervision constante.
"""
from dataclasses import dataclass, field
from datetime import date


@dataclass
class RiskManager:
    cfg: object
    _daily_pnl: float = 0.0
    _daily_date: date = field(default_factory=date.today)
    _trading_halted: bool = False

    def reset_if_new_day(self):
        today = date.today()
        if today != self._daily_date:
            self._daily_date = today
            self._daily_pnl = 0.0
            self._trading_halted = False

    def register_trade_result(self, pnl: float):
        self.reset_if_new_day()
        self._daily_pnl += pnl
        max_loss = -abs(self.cfg.capital_total * self.cfg.max_daily_loss_pct / 100)
        if self._daily_pnl <= max_loss:
            self._trading_halted = True

    def can_trade(self) -> bool:
        self.reset_if_new_day()
        return not self._trading_halted

    def load_state(self, state: dict):
        """Recupera el estado guardado (ej. al iniciar un contenedor nuevo en GitHub Actions)."""
        self._daily_pnl = state.get("daily_pnl", 0.0)
        d = state.get("daily_date")
        self._daily_date = date.fromisoformat(d) if d else date.today()
        self._trading_halted = state.get("trading_halted", False)
        self.reset_if_new_day()  # si el estado guardado es de otro dia, arranca en limpio

    def export_state(self) -> dict:
        return {
            "daily_pnl": self._daily_pnl,
            "daily_date": self._daily_date.isoformat(),
            "trading_halted": self._trading_halted,
        }

    def position_size(self, entry_price: float, stop_price: float) -> float:
        """Tamano de posicion en unidades del activo (ej. BTC), nunca un monto fijo arbitrario."""
        risk_amount = self.cfg.capital_total * self.cfg.risk_per_trade_pct / 100
        distance = abs(entry_price - stop_price)
        if distance <= 0:
            return 0.0
        size = risk_amount / distance
        max_notional = self.cfg.capital_total * self.cfg.max_leverage
        max_size = max_notional / entry_price
        return min(size, max_size)

    def risk_reward_ok(self, entry: float, stop: float, target: float) -> bool:
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk <= 0:
            return False
        return (reward / risk) >= self.cfg.min_risk_reward
