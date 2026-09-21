#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Run this installer with sudo." >&2
  exit 1
fi

ROOT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
CONFIG_SOURCE="${ROOT_DIR}/config/dashboard.json"

if [[ ! -f ${CONFIG_SOURCE} ]]; then
  echo "Create config/dashboard.json from dashboard.example.json first." >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends nginx python3 python3-venv i2c-tools fonts-dejavu-core

install -d -m 0755 /opt/webhosting-deck /etc/webhosting-deck /var/lib/webhosting-deck /var/www/webhosting-deck
python3 -m venv /opt/webhosting-deck/venv
/opt/webhosting-deck/venv/bin/pip install --disable-pip-version-check --no-cache-dir Pillow smbus2

install -m 0755 "${ROOT_DIR}/src/webhosting_deck.py" /opt/webhosting-deck/webhosting_deck.py
install -m 0644 "${CONFIG_SOURCE}" /etc/webhosting-deck/dashboard.json
install -m 0644 "${ROOT_DIR}/config/nginx-log.conf" /etc/nginx/conf.d/webhosting-deck-log.conf
install -m 0644 "${ROOT_DIR}/config/nginx-site.conf" /etc/nginx/sites-available/webhosting-deck
ln -sfn /etc/nginx/sites-available/webhosting-deck /etc/nginx/sites-enabled/webhosting-deck
rm -f /etc/nginx/sites-enabled/default

if [[ ! -e /var/www/webhosting-deck/index.html ]]; then
  install -m 0644 "${ROOT_DIR}/site/index.html" /var/www/webhosting-deck/index.html
fi

install -m 0644 "${ROOT_DIR}/systemd/webhosting-deck.service" /etc/systemd/system/webhosting-deck.service
printf '%s\n' i2c-dev > /etc/modules-load.d/webhosting-deck.conf

nginx -t
systemctl daemon-reload
systemctl enable --now nginx webhosting-deck.service

cat <<'EOF'
Installed Webhosting Deck.

Next:
  1. Add config/config.txt.snippet to /boot/firmware/config.txt once.
  2. Install and configure cloudflared using docs/cloudflare-tunnel.md.
  3. Reboot to activate the display overlay.
EOF
