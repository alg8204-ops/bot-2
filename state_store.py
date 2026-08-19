"""
Persistencia de estado en un archivo JSON simple.

Necesario para poder correr el bot en plataformas donde cada ejecucion arranca "desde
cero" (por ejemplo GitHub Actions, un contenedor nuevo cada vez): sin esto, el bot
olvidaria si tiene una posicion abierta o cuanto lleva perdido en el dia cada vez que
se ejecuta. Con un servidor siempre encendido (VPS) tambien ayuda: si el proceso se
reinicia, retoma donde estaba en vez de perder el estado.
"""
import json
import os
from datetime import date

DEFAULT_STATE = {
    "daily_pnl": 0.0,
    "daily_date": None,   # se completa con la fecha de hoy si no existe
    "trading_halted": False,
    "open_position": None,
}


def load_state(path: str) -> dict:
    if not os.path.isfile(path):
        state = dict(DEFAULT_STATE)
        state["daily_date"] = date.today().isoformat()
        return state
    try:
        with open(path) as f:
            state = json.load(f)
    except Exception:
        state = {}
    for k, v in DEFAULT_STATE.items():
        state.setdefault(k, v)
    if not state.get("daily_date"):
        state["daily_date"] = date.today().isoformat()
    return state


def save_state(path: str, state: dict) -> None:
    """Escritura atomica: si el proceso se corta a mitad, el archivo previo queda intacto."""
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp_path, path)
