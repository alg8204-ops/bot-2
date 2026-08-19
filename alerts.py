"""
Alertas opcionales por Telegram, para poder monitorear el bot sin estar frente a la pantalla.
Requiere crear un bot en @BotFather y obtener el chat_id. Si no se configuran, se omiten
silenciosamente (el bot sigue funcionando igual).
"""
import urllib.request
import urllib.parse


def send_telegram_alert(cfg, message: str):
    if not cfg.telegram_bot_token or not cfg.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{cfg.telegram_bot_token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": cfg.telegram_chat_id, "text": message}).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=5)
    except Exception:
        pass  # un fallo de red en las alertas no debe tumbar el bot
