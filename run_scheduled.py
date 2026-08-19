"""
Punto de entrada para ejecucion PROGRAMADA (GitHub Actions u otro cron sin servidor
propio): corre UN solo ciclo y termina. El estado (posicion abierta, perdida del dia)
se guarda en state.json, que el workflow de GitHub sube de vuelta al repositorio para
que la proxima ejecucion -- en un contenedor nuevo, desde cero -- sepa donde quedo todo.
"""
from config import Config
from main import build_components, run_once, persist


def run():
    cfg = Config()
    data_feed, risk_mgr, executor = build_components(cfg)
    print(f"Ciclo unico | data_mode={cfg.data_mode} | execution_mode={cfg.execution_mode}")
    run_once(cfg, data_feed, risk_mgr, executor)
    persist(risk_mgr, executor)
    print("Estado guardado en state.json")


if __name__ == "__main__":
    run()
