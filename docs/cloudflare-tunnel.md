# Cloudflare Tunnel

Cloudflare Tunnel publishes local Nginx through an outbound encrypted connection, so the router needs no inbound port forwarding.

1. Add a domain you control to Cloudflare.
2. In Cloudflare Zero Trust, create a tunnel.
3. Select the Debian/Raspberry Pi connector instructions.
4. Install `cloudflared` from Cloudflare's repository.
5. Run the generated service-install command directly on the Pi.
6. Add a public hostname such as `www.example.com` targeting `http://127.0.0.1:8080`.
7. Add the apex hostname separately if required.

The service-install command contains a secret token. Never paste it into source control or public support requests.

Advanced users can adapt `config/cloudflared.example.yml`. Keep the actual credentials file under `/etc/cloudflared/` with restrictive permissions.

Verify with:

```bash
systemctl status cloudflared --no-pager
curl -I http://127.0.0.1:8080/
curl -I https://www.example.com/
```

A named tunnel can be moved to replacement hardware using its protected token or credential file; another browser authorization is not always required.
