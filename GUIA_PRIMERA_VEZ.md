# Guía para principiantes: poner el bot a funcionar (paso a paso)

> **¿Preferís no usar ninguna tarjeta de crédito, ni siquiera para verificar identidad?**
> Esta guía usa Google Cloud, que sí la pide (aunque no cobra). Para una alternativa
> 100% sin tarjeta, usá `GUIA_GITHUB_ACTIONS.md` en su lugar.

Esta guía asume que es la primera vez que hacés cada uno de estos pasos. No vas a tocar
código en ningún momento — solo copiar y pegar comandos en el orden indicado. Tomate tu
tiempo: la primera vez suele llevar entre 30 y 45 minutos, y no pasa nada si te trabás en
algún paso, se puede repetir sin romper nada.

**Marcá tu progreso** a medida que avanzás:
- [ ] Parte 1: Crear tu computadora gratuita en internet
- [ ] Parte 2: Conectarte a ella y subir el bot
- [ ] Parte 3: Prenderlo en modo seguro (sin dinero real)
- [ ] Parte 4: Confirmar que está funcionando
- [ ] Parte 5 (opcional): Alertas por Telegram

---

## El panorama general, antes de empezar

Vamos a "alquilar" gratis una pequeña computadora que vive en un centro de datos de Google
y que va a estar prendida las 24 horas — a eso se le llama VPS o VM (máquina virtual). Le
vamos a copiar los archivos del bot, y vamos a dejarlo corriendo ahí en **modo simulado**:
revisa el mercado y "finge" que opera, sin arriesgar ni un centavo, para que puedas ver
cómo se comporta antes de pensar siquiera en usar dinero real.

## Lo que necesitás antes de arrancar
- Una cuenta de Google (la misma de Gmail sirve).
- Una tarjeta de crédito o débito. Google la pide para confirmar que sos una persona real,
  **no te cobra nada** mientras te quedes dentro de los límites gratuitos (este bot los
  usa de sobra sin acercarse al límite).
- El archivo `btc_intraday_bot.zip` que descargaste de esta conversación. Si no lo tenés a
  mano, pedímelo de nuevo y te lo vuelvo a compartir.
- Este documento abierto en tu celular o en otra pestaña, para ir siguiéndolo.

---

## Parte 1: Crear tu computadora gratuita en internet

### 1.1 Entrar a Google Cloud
Andá a **console.cloud.google.com** e iniciá sesión con tu cuenta de Google. Si es tu
primera vez, Google te va a pedir aceptar unos términos y cargar una tarjeta — seguí ese
asistente, es autoexplicativo.

### 1.2 Crear la máquina virtual
1. Arriba a la izquierda hay un ícono de tres líneas (el "menú"). Tocalo y buscá
   **Compute Engine**. La primera vez que entrás, Google tarda unos segundos en activar
   este servicio — es normal, esperá.
2. Buscá el botón **"Crear instancia"** (o "Create Instance") y hacé clic.
3. Se abre un formulario. Completá solo estos campos, dejá el resto como está:
   - **Nombre**: por ejemplo `btc-bot` (sin espacios).
   - **Región**: elegí **`us-central1`**. *Este paso importa*: solo `us-central1`,
     `us-west1` o `us-east1` entran en el nivel gratuito. Si elegís otra región, te van
     a cobrar.
   - **Tipo de máquina**: buscá la serie **E2** y elegí **`e2-micro`**.
   - **Sistema operativo / disco de arranque**: dejá el que viene por defecto (Debian).
     Es más que suficiente para este bot.
4. Hacé clic en **"Crear"**. En unos 30-60 segundos vas a ver tu máquina aparecer en la
   lista, con un puntito verde indicando que está prendida.

> **Si ves un error de "sin capacidad" (out of capacity):** es un problema temporal de
> Google en esa región, no tuyo. Esperá un par de minutos y volvé a intentar, o probá con
> `us-west1` o `us-east1` en su lugar.

---

## Parte 2: Conectarte a tu máquina y subir el bot

### 2.1 Abrir una terminal dentro de tu máquina
Una "terminal" es una ventana donde le escribís comandos de texto a la computadora en vez
de hacer clic en botones — es como vamos a instalar y prender el bot.

En la lista de instancias, en la fila de tu máquina (`btc-bot`), hacé clic en el botón
**"SSH"**. Se abre una ventana nueva en el navegador con fondo negro y texto: esa es la
terminal de tu máquina en la nube. No necesitás instalar nada para esto, todo pasa en el
navegador.

### 2.2 Subir el archivo del bot
Dentro de esa ventana de SSH, buscá un ícono de **subir archivo** (upload) — suele estar
arriba a la derecha, junto a un ícono de engranaje/configuración. Hacé clic ahí, elegí el
archivo `btc_intraday_bot.zip` que descargaste antes, y subilo. Va a parar directo a la
carpeta principal de tu máquina.

### 2.3 Descomprimir el bot
De vuelta en la terminal negra, escribí este comando y presioná Enter (instala la
herramienta para descomprimir archivos .zip, no viene instalada por defecto):
```bash
sudo apt-get update -y && sudo apt-get install -y unzip
```
Después, confirmá el nombre exacto de tu archivo con:
```bash
ls
```
Vas a ver algo como `btc_intraday_bot.zip` en la lista. Usá ese nombre exacto en el
siguiente comando (ajustalo si tu archivo se llama distinto, por ejemplo si el navegador
le agregó "(1)"):
```bash
unzip btc_intraday_bot.zip -d btc_bot
cd btc_bot
```
`cd` significa "entrar a esa carpeta". A partir de ahora, todos los comandos siguientes
asumen que estás parado dentro de `btc_bot`.

---

## Parte 3: Prender el bot (modo seguro, sin dinero real)

### 3.1 Ejecutar el instalador
Este script instala todo lo necesario automáticamente (puede tardar 1-2 minutos, es
normal ver mucho texto pasando):
```bash
bash deploy.sh
```
Al final te va a decir "Creado .env. EDITALO antes de continuar" — seguí al siguiente paso.

### 3.2 Revisar la configuración
Escribí:
```bash
nano .env
```
Esto abre un editor de texto simple dentro de la terminal. Vas a ver algo así:
```
DATA_MODE=mock
EXECUTION_MODE=paper
```
**Por ahora no cambies nada** — estos valores son justamente el modo 100% seguro. Para
salir del editor sin romper nada: presioná `Ctrl+O` (guarda), después `Enter` (confirma),
después `Ctrl+X` (sale). Es normal sentirse perdido la primera vez en este editor — esos
tres pasos siempre funcionan para guardar y salir.

### 3.3 Arrancar el bot
```bash
sudo systemctl enable --now btc-bot
```
Esto lo prende y hace que se vuelva a prender solo si la máquina se reinicia alguna vez.

### 3.4 Ver qué está haciendo
```bash
journalctl -u btc-bot -f
```
Vas a empezar a ver líneas de texto apareciendo cada un rato — es el bot revisando el
mercado (simulado) y contándote qué decidió y por qué. Para dejar de mirar el log (el bot
sigue corriendo igual en segundo plano): presioná `Ctrl+C`.

---

## Parte 4: Confirmar que está funcionando

Si ves líneas como estas, todo está funcionando correctamente:
```
[BTC/USDT] Sin operacion. Score=3. Razones: ['Tendencia 4H alcista', ...]
```
Eso significa: el bot revisó el mercado, no encontró suficientes señales alineadas
todavía, y no hizo nada — exactamente el comportamiento esperado la mayor parte del
tiempo. De vez en cuando vas a ver una línea que empieza con `LONG` o `SHORT`: esa es una
operación simulada (sin dinero real) que el bot decidió "abrir".

Podés volver a este comando cuando quieras para ver la actividad reciente:
```bash
journalctl -u btc-bot -f
```
Y para cerrar la ventana de SSH tranquilo, sin apagar el bot: simplemente cerrá la
pestaña del navegador. El bot sigue corriendo en Google Cloud, no en tu computadora.

---

## Parte 5 (opcional, pero recomendada): alertas por Telegram

Así te enterás de lo que hace el bot sin tener que entrar a mirar la terminal.

1. Abrí Telegram (la app o web.telegram.org) y buscá el usuario **@BotFather**.
2. Enviale el mensaje `/newbot` y seguí sus instrucciones (te va a pedir un nombre para
   tu bot). Al final te da un **token** — es un texto largo con letras y números, copialo.
3. Buscá el usuario **@userinfobot** y enviale cualquier mensaje: te responde con tu
   **chat_id** (un número), copialo también.
4. De vuelta en tu terminal SSH:
   ```bash
   nano .env
   ```
   Completá estas dos líneas con lo que copiaste:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aca
   TELEGRAM_CHAT_ID=tu_chat_id_aca
   ```
   Guardá y salí igual que antes (`Ctrl+O`, `Enter`, `Ctrl+X`).
5. Reiniciá el bot para que tome el cambio:
   ```bash
   sudo systemctl restart btc-bot
   ```
Desde ahora, cada operación simulada y cada error te va a llegar como mensaje de Telegram.

---

## Qué NO hacer todavía
- No cambies `EXECUTION_MODE` a `live` — eso activaría órdenes con dinero real.
- No cargues claves de tu exchange (`EXCHANGE_API_KEY`) todavía.
- Estos dos pasos son, a propósito, para más adelante — ver `IMPLEMENTACION.md` para la
  ruta completa de migración cuando llegue el momento.

## Si algo sale mal
```bash
sudo systemctl status btc-bot     # ¿está corriendo? te muestra el estado actual
journalctl -u btc-bot -n 50       # las últimas 50 líneas de actividad/errores
sudo systemctl restart btc-bot    # reiniciarlo si algo se ve raro
```
Si algo no coincide con lo que describe esta guía (un botón con otro nombre, un mensaje de
error distinto), copiá y pegame exactamente lo que estás viendo — lo resolvemos juntos.

## Glosario rápido
| Término | Qué es, en una línea |
|---|---|
| VPS / VM | Una computadora que no es tuya físicamente, vive en internet, y alquilás (en este caso gratis) |
| Terminal | Ventana donde escribís comandos de texto en vez de hacer clic |
| SSH | La forma de "entrar" a esa computadora remota desde tu navegador |
| Variable de entorno | Un valor de configuración (como tu clave de API) que el programa lee sin que esté escrito en el código |
| `.env` | El archivo donde guardás esas variables de entorno |
| systemd / `systemctl` | El sistema que mantiene tu bot prendido y lo reinicia solo si se cae |
