# Implementación: de tu máquina a corriendo solo, 24/7

Camino recomendado: **una VPS pequeña + systemd**. Es la combinación más simple que es
realmente eficaz: systemd reinicia el bot solo si se cae, lo arranca automáticamente si
el servidor se reinicia, y no depende de que tu laptop esté encendida ni conectada.

Si prefieres no administrar ningún servidor, plataformas tipo Railway, Render o Fly.io
permiten desplegar un script Python como "worker" conectando un repositorio, sin SSH ni
systemd — es una alternativa válida, algo menos flexible pero más simple aún.

## 0. Elegir una VPS — incluida la opción $0/mes
Este bot necesita muy pocos recursos (un script que consulta datos cada pocos minutos), así
que hasta el nivel gratuito más pequeño de cualquier proveedor le sobra:

- **Google Cloud, instancia e2-micro**: nivel "Always Free" permanente (no es una prueba de
  30 días), 1 instancia gratis para siempre mientras se cree en `us-west1`, `us-central1` o
  `us-east1`. Es la opción gratuita más consistente y predecible ahora mismo.
- **Oracle Cloud, Always Free**: también existe y también sirve, pero Oracle redujo los
  límites de este nivel recientemente — revisa las condiciones actuales al crear la cuenta
  en vez de fiarte de una cifra fija.
- **Sin ningún servidor**: correr `python main.py` directo en tu propia computadora, con el
  Programador de tareas (Windows) o `launchd`/`cron` (Mac/Linux) para que arranque solo. Es
  gratis con certeza total, pero tu equipo debe quedar encendido y conectado — es exactamente
  la presencia que buscabas evitar, así que solo tiene sentido como opción temporal de prueba.

Si prefieres un proveedor de pago de todas formas (DigitalOcean, Hetzner, Vultr...), el plan
más económico (1 vCPU, 1 GB RAM, unos pocos dólares al mes) también es más que suficiente —
la elección es tuya, no una necesidad técnica del bot.

Ubuntu 22.04/24.04 como sistema operativo en cualquiera de los casos; los pasos de `deploy.sh`
de aquí en adelante son los mismos sin importar el proveedor.

## 1. Subir el proyecto
Desde tu máquina, con la carpeta ya descomprimida:
```bash
scp -r btc_bot usuario@IP_DE_TU_VPS:~/
ssh usuario@IP_DE_TU_VPS
cd btc_bot
```

## 2. Desplegar
```bash
bash deploy.sh
```
Esto instala Python, crea un entorno virtual, instala dependencias, prepara `.env` a partir
de `.env.example`, y registra el servicio systemd. Al final te dirá los comandos exactos
para arrancarlo.

## 3. Configurar `.env`
```bash
nano .env
```
Empieza siempre así (son los valores por defecto, no hace falta tocarlos aún):
```
DATA_MODE=mock
EXECUTION_MODE=paper
```

## 4. Arrancar el servicio
```bash
sudo systemctl enable --now btc-bot
journalctl -u btc-bot -f
```
`enable --now` lo activa ya y además hace que arranque solo si la VPS se reinicia.
`journalctl -f` te deja ver en vivo lo que decide el bot en cada ciclo. Ctrl+C para salir
del log (el bot sigue corriendo en segundo plano).

## 5. La ruta de migración (no te saltes pasos)
| Fase | `.env` | Qué valida |
|---|---|---|
| 1. Local, ya probado | `DATA_MODE=mock` `EXECUTION_MODE=paper` | Que el código funciona sin errores |
| 2. En la VPS, semanas | `DATA_MODE=live` `EXECUTION_MODE=paper` | Que las señales tienen sentido contra el mercado real, sin arriesgar nada |
| 3. Capital real, pequeño | `DATA_MODE=live` `EXECUTION_MODE=live` | El sistema completo, empezando con lo mínimo que estés dispuesto a perder |

Para pasar de fase: edita `.env` y `sudo systemctl restart btc-bot`. Nunca saltes directo
de la fase 1 a la 3.

Antes de la fase 3, además:
```bash
export EXCHANGE_API_KEY="tu_key"      # o mejor, agrégalas directamente en .env
export EXCHANGE_API_SECRET="tu_secret"
```
En tu exchange, la API key debe tener permiso **solo de trading**, nunca de retiro.

## 6. Enterarte sin estar delante de la pantalla
Rellena en `.env`:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
(@BotFather crea el bot y te da el token; @userinfobot te da tu chat_id). Reinicia el
servicio y cada operación y cada error te llegará como mensaje de Telegram.

## Mantenimiento habitual
```bash
sudo systemctl status btc-bot     # ¿está corriendo?
journalctl -u btc-bot -f          # logs en vivo
sudo systemctl restart btc-bot    # tras editar .env o actualizar código
sudo systemctl stop btc-bot       # detenerlo del todo
cat trade_journal.csv             # historial de señales/operaciones
```

## Actualizar el código más adelante
```bash
scp -r btc_bot usuario@IP_DE_TU_VPS:~/   # sobreescribe con la version nueva
ssh usuario@IP_DE_TU_VPS
cd btc_bot && source venv/bin/activate && pip install -r requirements.txt -q
sudo systemctl restart btc-bot
```

## Antes de la fase 3, un recordatorio honesto
Que el bot corra solo no reduce el riesgo del sistema en sí — solo automatiza su ejecución.
Sigue arriesgando únicamente capital que puedas perder por completo, revisa el journal y
las alertas con regularidad, y no hay combinación de VPS + systemd + alertas que sustituya
haber validado la estrategia en la fase 2 durante el tiempo suficiente.
