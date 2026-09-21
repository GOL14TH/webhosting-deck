#!/usr/bin/env bash
set -u

echo "== Services =="
systemctl --no-pager --full status nginx webhosting-deck cloudflared 2>/dev/null | sed -n '1,45p'
echo
echo "== Local website =="
curl --fail --silent --show-error --output /dev/null --write-out 'HTTP %{http_code} in %{time_total}s\n' http://127.0.0.1:8080/ || true
echo
echo "== Hardware =="
[[ -e /dev/fb0 ]] && echo "Framebuffer: present" || echo "Framebuffer: missing"
[[ -e /dev/i2c-1 ]] && echo "I2C bus 1: present" || echo "I2C bus 1: missing"
command -v i2cdetect >/dev/null && i2cdetect -y 1 2>/dev/null || true
echo
echo "== Recent dashboard log =="
journalctl -u webhosting-deck -n 20 --no-pager 2>/dev/null || true
