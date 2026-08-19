"""
Orquestacion principal: obtener datos -> gestionar posicion abierta (si hay) o evaluar
una entrada nueva -> ejecutar -> guardar estado.

Por defecto corre en data_mode="mock" y execution_mode="paper": no se conecta a ningun
exchange real ni coloca ninguna orden real. Cambiar esto es una decision consciente que
debes tomar tu, editando .env — no es el comportamiento por defecto.

Este archivo sirve para DOS formas de correr el bot:
  1. Bucle continuo en un servidor propio (VPS): funcion main(), pensada para systemd.
  2. Un solo ciclo por ejecucion (ej. GitHub Actions, sin servidor propio): ver run_scheduled.py,
     que reutiliza build_components/run_once/persist de este mismo archivo.
En ambos casos el estado (posicion abierta, perdida del dia) se guarda en state.json para
no perderlo entre ejecuciones.
"""
import time
import traceback

from config import Config
from data_feed import DataFeed
from indicators import add_all_indicators
from fundamental import build_fundamental_snapshot
from signals import generate_signal
from risk_manager import RiskManager
from executor import Executor
from journal import log_entry, log_close
from alerts import send_telegram_alert
from state_store import load_state, save_state

STATE_PATH = "state.json"


def build_components(cfg):
    data_feed = DataFeed(cfg)
    risk_mgr = RiskManager(cfg=cfg)
    executor = Executor(cfg, data_feed)

    state = load_state(STATE_PATH)
    risk_mgr.load_state(state)
    executor.load_state(state.get("open_position"))
    return data_feed, risk_mgr, executor


def persist(risk_mgr, executor):
    state = risk_mgr.export_state()
    state["open_position"] = executor.export_state()
    save_state(STATE_PATH, state)


def run_once(cfg, data_feed, risk_mgr, executor):
    df_entry = data_feed.fetch_ohlcv(cfg.timeframe_entry, limit=250)
    df_entry = add_all_indicators(df_entry, cfg)
    current_price = float(df_entry["close"].iloc[-1])

    # Si hay una posicion abierta, este ciclo SOLO se ocupa de gestionarla
    # (nunca se abre una posicion nueva mientras otra sigue en curso).
    if executor.open_position is not None:
        pnl = executor.check_and_close_position(current_price)
        if pnl is not None:
            risk_mgr.register_trade_result(pnl)
            closed = executor.last_closed
            log_close(closed)
            msg = (
                f"Cerrada {closed['side']} {cfg.symbol} por {closed['result']} | "
                f"PnL={pnl:.2f} [{cfg.execution_mode}]"
            )
            print(msg)
            send_telegram_alert(cfg, msg)
        else:
            print(f"Posicion {executor.open_position['side']} en curso. Precio actual={current_price:.2f}")
        return None

    if not risk_mgr.can_trade():
        print("Limite de perdida diaria alcanzado. Bot en pausa hasta manana.")
        return None

    df_trend = data_feed.fetch_ohlcv(cfg.timeframe_trend, limit=250)
    df_trend = add_all_indicators(df_trend, cfg)

    funding_rate = data_feed.fetch_funding_rate()
    open_interest = data_feed.fetch_open_interest()
    fundamentals = build_fundamental_snapshot(cfg, funding_rate, open_interest)

    signal = generate_signal(df_entry, df_trend, fundamentals, cfg)

    if signal.action == "none":
        print(f"[{cfg.symbol}] Sin operacion. Score={signal.score}. Razones: {signal.reasons}")
        return None

    if not risk_mgr.risk_reward_ok(signal.entry, signal.stop, signal.target):
        print("Senal descartada: ratio riesgo/beneficio insuficiente.")
        return None

    size = risk_mgr.position_size(signal.entry, signal.stop)
    order = executor.execute(signal, size)
    if order is None:
        return None
    log_entry(signal, size, extra={"mode": cfg.execution_mode})

    msg = (
        f"{signal.action.upper()} {cfg.symbol} | entry={signal.entry:.2f} "
        f"stop={signal.stop:.2f} target={signal.target:.2f} size={size:.6f} "
        f"[{cfg.execution_mode}]"
    )
    print(msg)
    send_telegram_alert(cfg, msg)
    return order


def main():
    cfg = Config()
    data_feed, risk_mgr, executor = build_components(cfg)

    print(f"Iniciando bot | data_mode={cfg.data_mode} | execution_mode={cfg.execution_mode}")
    if cfg.execution_mode == "live":
        print("*** MODO LIVE: se colocaran ordenes reales. Ctrl+C para cancelar ahora. ***")
        time.sleep(10)

    while True:
        try:
            run_once(cfg, data_feed, risk_mgr, executor)
            persist(risk_mgr, executor)
        except Exception as e:
            err = f"Error en el bucle principal: {e}"
            print(err)
            print(traceback.format_exc())
            send_telegram_alert(cfg, f"Alerta bot: {err}")
        time.sleep(cfg.loop_interval_seconds)


if __name__ == "__main__":
    main()
