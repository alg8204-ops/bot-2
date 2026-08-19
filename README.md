# Bot de Trading Intradía BTC — Guía de uso

Implementa el marco de análisis técnico + fundamental del documento anterior, probado de
extremo a extremo (apertura y cierre de posición, límite de pérdida diaria, persistencia
de estado entre ejecuciones — ver detalle de pruebas en `GUIA_GITHUB_ACTIONS.md`).

## ¿Cuál guía seguir?
- **No querés usar tarjeta de crédito en ningún lado** → `GUIA_GITHUB_ACTIONS.md`
  (recomendado; 100% gratis, sin tarjeta nunca, corre solo cada 15 min).
- Preferís un servidor propio siempre encendido y no te molesta cargar una tarjeta
  (aunque no te cobren) → `GUIA_PRIMERA_VEZ.md` (Google Cloud) o `IMPLEMENTACION.md`
  (referencia rápida para cualquier VPS).
- Solo querés probarlo ya, en tu propia computadora → seguí leyendo acá abajo.

## Estado por defecto: 100% seguro
```
DATA_MODE=mock        # datos sintéticos, sin conexión a ningún exchange
EXECUTION_MODE=paper  # simula operaciones, nunca coloca órdenes reales
```
Puedes ejecutarlo ahora mismo sin cuenta de exchange ni riesgo alguno, solo para ver la lógica en acción.

## Instalación local
```bash
pip install -r requirements.txt
python main.py
```

## Paso 1 — Datos reales, sin arriesgar dinero
Definí la variable de entorno (o el secret de GitHub, o la línea en `.env` según qué
guía estés siguiendo):
```
DATA_MODE=live
```
`EXECUTION_MODE` sigue en `paper`. Así validas las señales contra el mercado real
durante semanas antes de arriesgar nada (ver punto 8 del marco original: backtesting +
demo antes de capital real).

## Paso 2 — Operar con dinero real (opcional, bajo tu responsabilidad)
1. Confirma que el sistema fue rentable de forma consistente en paper trading con datos reales.
2. Crea una API key en tu exchange con permiso **solo de trading** — nunca actives retiro de fondos.
3. Definí `EXCHANGE_API_KEY` y `EXCHANGE_API_SECRET` (nunca hardcodees claves en el código).
4. Cambiá `EXECUTION_MODE=live`.

## "Autónomo" no significa "sin supervisión"
Ningún bot debería correr indefinidamente sin que nadie lo revise:
- Configura alertas por Telegram (`alerts.py`) para enterarte de operaciones y errores sin estar frente a la pantalla — necesitas `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` como variables de entorno.
- Revisa `trade_journal.csv` con regularidad; ahí queda cada señal y operación.
- Un bug, un cambio brusco de mercado o una caída del exchange pueden causar pérdidas grandes si nadie se entera durante días. El `try/except` en `main.py` evita que el bot "haga cosas raras" al fallar, pero no reemplaza revisar el sistema periódicamente.
- Empieza siempre con capital que puedas permitirte perder por completo.

## Estructura del proyecto
| Archivo | Función |
|---|---|
| `config.py` | Todos los parámetros ajustables (riesgo, indicadores, modo) |
| `data_feed.py` | Obtiene velas OHLCV, funding rate y open interest |
| `indicators.py` | EMA, RSI, MACD, Bollinger, VWAP |
| `fundamental.py` | Funding rate/OI + Fear & Greed Index (gratis) + placeholders on-chain/macro |
| `signals.py` | Checklist de confluencia técnico + fundamental |
| `risk_manager.py` | Tamaño de posición, ratio riesgo/beneficio, límite de pérdida diaria |
| `executor.py` | Abre y **cierra** la posición por stop/target, calcula el PnL real |
| `journal.py` | Registra cada apertura y cierre en `trade_journal.csv` |
| `alerts.py` | Notificaciones opcionales por Telegram |
| `state_store.py` | Guarda/recupera el estado (posición abierta, PnL del día) entre ejecuciones |
| `main.py` | Bucle continuo (VPS/local) — reutilizado por `run_scheduled.py` |
| `run_scheduled.py` | Un solo ciclo por ejecución (GitHub Actions) |
| `.github/workflows/bot.yml` | Programa el bot cada 15 min en GitHub Actions, gratis |

## Análisis fundamental: qué es real y gratis, y qué no
- **Funding rate y open interest**: reales, vía ccxt, gratis, sin API key.
- **Fear & Greed Index**: real, vía la API pública de Alternative.me, gratis, sin API key
  (con caché de 1 hora para no abusar del servicio). Se usa para evitar abrir largos en
  euforia extrema y cortos en pánico extremo.
- **Flujos de exchanges / movimientos de ballenas**: sin equivalente gratuito real — es
  justo el valor que venden Glassnode o CryptoQuant (etiquetar wallets). Queda como `TODO`
  en `fundamental.py`, no se simula.
- **Calendario macro (FOMC/CPI/NFP)**: no hay una API gratuita fiable para esto. Las fechas
  de FOMC se publican con meses de antelación en federalreserve.gov — la alternativa
  gratuita realista es cargarlas a mano (ver `IMPLEMENTACION.md`).

Ninguna de estas dos últimas es necesaria para que el sistema funcione: sin ellas, opera
igual con el resto del checklist (tendencia, EMA20, RSI, funding rate, Fear & Greed).
- No incluye backtesting sobre datos históricos reales; lo simulado aquí (`data_mode="mock"`)
  es solo para verificar que el código funciona, no para validar la estrategia.
- Ningún resultado en paper trading garantiza resultados iguales con dinero real
  (slippage, comisiones y latencia cambian el resultado).

## Corrección importante en esta revisión
Las versiones anteriores abrían posiciones simuladas pero **nunca las cerraban ni
registraban el resultado** — en la práctica, el límite de pérdida diaria nunca se activaba
porque nunca recibía ningún PnL. `executor.py` ahora revisa en cada ciclo si el precio
actual tocó el stop o el target, cierra la posición, calcula el PnL real y se lo pasa al
`risk_manager`. También se agregó `state_store.py` para que ese seguimiento sobreviva
entre ejecuciones independientes (necesario para GitHub Actions, y como red de seguridad
adicional en un VPS si el proceso llegara a reiniciarse). Quedó cubierto con pruebas
específicas antes de esta entrega.
