"""
Journal de operaciones: registra cada apertura y cierre en un CSV para revision posterior.
Corresponde al punto 8 del marco original: es indispensable para validar si el sistema
realmente funciona antes (y despues) de usar capital real.

Columnas fijas (en vez de tomarlas de las claves de cada evento) para que abrir y cerrar
queden prolijos en el mismo archivo sin romper el CSV.
"""
import csv
import os
from datetime import datetime

JOURNAL_PATH = "trade_journal.csv"

FIELDNAMES = [
    "timestamp", "event", "side", "score", "reasons",
    "entry", "stop", "target", "size", "exit_price", "pnl", "mode",
]


def _write_row(row: dict, path: str = JOURNAL_PATH):
    full_row = {k: row.get(k, "") for k in FIELDNAMES}
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(full_row)


def log_entry(signal, size, extra=None, path: str = JOURNAL_PATH):
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "open",
        "side": signal.action,
        "score": signal.score,
        "reasons": " | ".join(signal.reasons),
        "entry": signal.entry,
        "stop": signal.stop,
        "target": signal.target,
        "size": size,
    }
    if extra:
        row.update(extra)
    _write_row(row, path)


def log_close(closed_position: dict, path: str = JOURNAL_PATH):
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": f"close_{closed_position.get('result', '')}",
        "side": closed_position.get("side"),
        "entry": closed_position.get("entry"),
        "stop": closed_position.get("stop"),
        "target": closed_position.get("target"),
        "size": closed_position.get("size"),
        "exit_price": closed_position.get("exit_price"),
        "pnl": closed_position.get("pnl"),
        "mode": closed_position.get("mode"),
    }
    _write_row(row, path)
