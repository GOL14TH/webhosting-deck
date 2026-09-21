# Dashboard

The dashboard writes a 480×320 RGB565 image directly to `/dev/fb0` every five seconds. It shows UPS percentage and state, website health, voltage, current, power, approximate visitors, CPU temperature, LAN address and time.

## Current direction

UPS HAT revisions can expose opposite INA219 shunt polarity. Start with `current_polarity: 1`, then test:

1. Remove external charging briefly. The screen should say `DISCHARGING`.
2. Reconnect it. While charge current flows, it should say `CHARGING`.
3. If both are reversed, set `current_polarity` to `-1` and restart the service.

At 100%, charging can fall below the configured threshold and correctly show `IDLE / BALANCED`.

## Visitor counts

Nginx records Cloudflare's connecting address in a dedicated log. The dashboard transforms addresses with a keyed BLAKE2 hash and persists only hashes and timestamps. `VIEWERS NOW` is the unique count in a rolling window; `TOTAL VIEWERS` is the count retained since state creation.

This is an operational estimate, not audited analytics. Bots, shared networks, rotating addresses and privacy relays affect the values.
