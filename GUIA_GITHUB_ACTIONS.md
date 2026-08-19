# Guía sin tarjeta: poner el bot a correr con GitHub Actions

GitHub nunca pide tarjeta de crédito para esto, ni en el registro ni después. Vamos a usar
**GitHub Actions**: en vez de tener un servidor siempre prendido, GitHub va a "despertar"
tu bot cada 15 minutos, ejecutar un ciclo, guardar el resultado, y apagarse. Gratis, sin
límite de tiempo, sin tarjeta.

**Marcá tu progreso:**
- [ ] Parte 1: Crear tu cuenta de GitHub y el repositorio
- [ ] Parte 2: Subir los archivos del bot
- [ ] Parte 3: Configurar tus claves (sin escribirlas nunca en el código)
- [ ] Parte 4: Probarlo y confirmar que funciona de verdad
- [ ] Parte 5: Entender qué vas a ver a partir de ahora

---

## Lo que necesitás
- Un mail (para crear la cuenta de GitHub — sin tarjeta, nunca).
- El archivo `btc_intraday_bot.zip` descargado de esta conversación.
- Tu computadora, para descomprimir el .zip (un clic derecho "Extraer todo" en Windows,
  o doble clic en Mac). No hace falta instalar nada más.
- 20-30 minutos.

---

## Parte 1: Crear tu cuenta y el repositorio

### 1.1 Crear la cuenta
Andá a **github.com** → **Sign up**. Pide mail, usuario y contraseña. Nada más — en
ningún paso del registro gratuito te va a pedir una tarjeta.

### 1.2 Crear el repositorio (la "carpeta" del proyecto en GitHub)
1. Arriba a la derecha, el botón **+** → **New repository**.
2. **Repository name**: por ejemplo `btc-bot`.
3. Marcá **Private** (así solo vos ves tu código y tu historial de operaciones).
4. No marques ninguna otra casilla. Clic en **Create repository**.

---

## Parte 2: Subir los archivos del bot

### 2.1 Descomprimir el .zip
En tu computadora, descomprimí `btc_intraday_bot.zip`. Vas a obtener una carpeta con
varios archivos `.py`, algunos `.md`, y una subcarpeta oculta `.github`.

### 2.2 Subir los archivos "normales"
En la página de tu repositorio recién creado, hacé clic en **"uploading an existing
file"** (o **Add file → Upload files**). Arrastrá **todos los archivos sueltos** de la
carpeta (los `.py`, `.md`, `.txt`, `.env.example` — todo menos la carpeta `.github`, que
vamos a subir aparte en el siguiente paso porque necesita quedar en un lugar exacto).
Bajá y hacé clic en **Commit changes**.

### 2.3 Subir el workflow (el archivo que le dice a GitHub cuándo correr el bot)
Este archivo tiene que quedar en una ubicación exacta, así que lo creamos directo:
1. En tu repositorio, clic en **Add file → Create new file**.
2. En el campo de nombre, escribí exactamente: `.github/workflows/bot.yml`
   (al escribir las `/` GitHub va creando las carpetas solo).
3. Abrí en tu computadora el archivo `.github/workflows/bot.yml` de la carpeta que
   descomprimiste (con el Bloc de notas o TextEdit), copiá todo su contenido, y pegalo en
   el editor de GitHub.
4. Clic en **Commit changes**.

**Checkpoint**: en tu repositorio deberías poder navegar `.github` → `workflows` → ver
`bot.yml` ahí adentro. Si no está en esa ruta exacta, GitHub no lo va a reconocer.

---

## Parte 3: Configurar tus claves (sin tocar código)

Vamos a guardar la configuración en un lugar cifrado y privado de GitHub, para no
escribir nunca ninguna clave dentro del código.

1. En tu repositorio, pestaña **Settings**.
2. Menú izquierdo: **Secrets and variables → Actions**.
3. Botón **New repository secret**, y repetí esto para cada fila de la tabla:

| Name (escribilo exacto) | Value (por ahora) |
|---|---|
| `DATA_MODE` | `mock` |
| `EXECUTION_MODE` | `paper` |

Con esas dos alcanza para arrancar 100% en modo seguro. Cuando más adelante quieras
pasar a datos reales o a Telegram, volvés a esta misma pantalla y agregás:
`EXCHANGE_API_KEY`, `EXCHANGE_API_SECRET`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — ver
Parte 5.

---

## Parte 4: Probarlo ahora mismo (no hace falta esperar 15 minutos)

1. Pestaña **Actions** de tu repositorio.
2. A la izquierda, clic en **"Bot BTC intradia"**.
3. Botón **Run workflow** (a la derecha) → **Run workflow** de nuevo para confirmar.
4. Esperá 30-60 segundos y actualizá la página. Va a aparecer una corrida con un círculo:
   amarillo (corriendo), verde (funcionó), o rojo (falló).
5. Hacé clic en esa corrida y despues en **run-bot** para ver el detalle línea por línea
   — es exactamente lo mismo que verías en una terminal.

**Si te da verde:** andá a tu repositorio (la página principal) y confirmá que ahora
existen dos archivos nuevos: `state.json` y `trade_journal.csv`. Eso confirma que el bot
corrió un ciclo completo y guardó el resultado — la prueba de que está funcionando de
verdad, no solo que "no dio error".

**Si te da rojo:** entrá igual a ver el detalle (paso 5) — el error va a estar escrito ahí
en texto plano. Copiámelo tal cual y lo resolvemos.

A partir de acá, sin que hagas nada más, va a volver a correr solo cada 15 minutos.

---

## Parte 5: Qué vas a ver de ahora en adelante

- Cada 15 minutos aparece una corrida nueva en la pestaña **Actions**.
- El archivo `trade_journal.csv` en tu repositorio va acumulando cada operación simulada
  — podés abrirlo directo en GitHub (se ve como una tabla) o descargarlo.
- `state.json` es la "memoria" del bot: cuánto lleva ganado/perdido hoy y si hay una
  posición abierta. No hace falta que lo edites nunca a mano.

### Alertas por Telegram (opcional)
Mismos pasos que ya vimos: @BotFather te da un token, @userinfobot te da tu chat_id.
Volvé a **Settings → Secrets and variables → Actions → New repository secret** y agregá
`TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` con esos valores. Nada más — el workflow ya
está preparado para usarlos apenas existan.

### Cuando quieras avanzar de fase
Volvé a **Settings → Secrets and variables → Actions**, hacé clic en el lápiz al lado de
`DATA_MODE` o `EXECUTION_MODE`, y cambiá el valor (`live` en vez de `mock`/`paper`). La
misma tabla de migración de `IMPLEMENTACION.md` aplica acá igual — no te saltees fases.

---

## Qué es distinto acá respecto de un servidor (VPS)
- No hay nada "prendido todo el tiempo": cada 15 minutos se crea una máquina nueva,
  corre un ciclo, y se apaga. Por eso el estado se guarda en `state.json` en vez de
  quedar solo en la memoria del programa.
- GitHub no promete el minuto exacto (puede tardar un par de minutos de más en
  horarios pico) — para un bot que revisa velas de 15 minutos, esa variación no importa.
- Si el repositorio estuviera 60 días sin ningún cambio, GitHub pausa automáticamente
  las tareas programadas. En la práctica esto no te va a pasar: como el bot actualiza
  `state.json` en cada corrida, siempre hay actividad reciente.

## Si algo sale mal
- **El workflow no aparece en la pestaña Actions**: revisá que el archivo esté exactamente
  en `.github/workflows/bot.yml` (Parte 2.3).
- **Corrida en rojo**: abrí el detalle (Parte 4, paso 5) y pegame el mensaje de error.
- **No ves `state.json` después de una corrida verde**: revisá en Settings que el
  workflow tenga permiso de escritura — Settings → Actions → General → baja hasta
  "Workflow permissions" → marcá **Read and write permissions** → **Save**.

## Una nota honesta sobre las pruebas
Probé toda la lógica del bot en un entorno propio: apertura y cierre de posiciones,
límite de pérdida diaria, y que el estado sobrevive entre ejecuciones independientes
(exactamente lo que simula GitHub Actions al usar un contenedor nuevo cada vez) — todo
funcionó correctamente. Lo único que no puedo probar desde acá es la ejecución real
dentro de GitHub (no tengo forma de conectarme a internet ni una cuenta real), por eso
la Parte 4 te deja confirmarlo vos mismo en menos de un minuto, con una forma clara de
saber si funcionó (verde + archivos nuevos) o no (rojo + mensaje de error para traerme).
