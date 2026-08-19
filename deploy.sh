#!/usr/bin/env bash
# Despliegue simple del bot en una VPS Ubuntu/Debian.
# Ejecutar DESDE DENTRO de la carpeta del proyecto (donde esta main.py): bash deploy.sh
set -e

echo "== 1/5 Instalando dependencias del sistema =="
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip

echo "== 2/5 Creando entorno virtual e instalando paquetes =="
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "== 3/5 Preparando archivo de variables de entorno =="
if [ ! -f .env ]; then
  cp .env.example .env
  chmod 600 .env
  echo "  -> Creado .env. EDITALO antes de continuar: nano .env"
fi

echo "== 4/5 Instalando servicio systemd =="
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)
sed -e "s#{{WORKDIR}}#$CURRENT_DIR#g" -e "s#{{USER}}#$CURRENT_USER#g" \
  btc-bot.service.template | sudo tee /etc/systemd/system/btc-bot.service > /dev/null
sudo systemctl daemon-reload

echo "== 5/5 Listo =="
echo ""
echo "Antes de arrancar, revisa/edita .env (nano .env)."
echo "Luego:"
echo "  sudo systemctl enable --now btc-bot   # arranca y lo deja activo tras reinicios"
echo "  journalctl -u btc-bot -f              # ver logs en vivo"
echo "  sudo systemctl stop btc-bot           # detenerlo"
echo "  sudo systemctl restart btc-bot        # reiniciar (ej. tras editar .env)"
