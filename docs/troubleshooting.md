# Troubleshooting

Start with `sudo ./scripts/check.sh`.

## Blank display

- Confirm `/dev/fb0` exists.
- Inspect `dmesg | grep -Ei 'ili|fb|spi'`.
- Confirm SPI is enabled and the overlay appears only once.
- Try another `rotate` value and verify header alignment.

## UPS data unavailable

- Confirm `/dev/i2c-1` exists.
- `sudo i2cdetect -y 1` should normally show `43` and `2d`.
- Tighten the board so its pogo pins make reliable contact.

## Voltage works but current is near zero

This can be valid when a full battery is balanced. It can also mean the Pi is powered through its own USB input, bypassing the UPS path. Connect charging to the HAT and perform a brief unplug test.

## State is reversed

Toggle `current_polarity` between `1` and `-1` in `/etc/webhosting-deck/dashboard.json`, then restart `webhosting-deck`.

## Local site works but public site does not

```bash
curl -I http://127.0.0.1:8080/
systemctl status nginx cloudflared --no-pager
journalctl -u cloudflared -n 50 --no-pager
```

Confirm the public hostname points to the correct local service and the tunnel is healthy.

## SSH address changed

Use a DHCP reservation. Check the current address locally with `hostname -I`; do not rely on a remembered lease.
