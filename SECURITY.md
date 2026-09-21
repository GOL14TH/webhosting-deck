# Security and privacy

## Never commit

- Passwords or password hashes
- SSH private keys
- Cloudflare tunnel tokens, credential JSON files or origin certificates
- Real private/public IP addresses tied to a deployment
- Personal email addresses, telephone numbers or home addresses
- Unredacted production logs

The examples use reserved names such as `example.com`, `server-hostname` and `192.0.2.10`.

## Recommended baseline

- Use SSH keys and disable password authentication after verifying key access.
- Keep Raspberry Pi OS, Nginx and `cloudflared` updated.
- Do not forward ports 22, 80 or 443 from the router.
- Bind Nginx to loopback when only Cloudflare Tunnel should reach it.
- Use Cloudflare Access for private administrative applications.
- Serve only a static site from this appliance; do not expose the status dashboard.
- Back up site content and configuration to another machine.
- Review `journalctl`, Nginx logs and Cloudflare security events periodically.

## Visitor privacy

The sample dashboard derives approximate unique counts from Cloudflare's connecting-IP header, transforms addresses using a keyed BLAKE2 hash, and stores only those hashes. Change the generated salt when rebuilding a machine. If you enable additional analytics, disclose it appropriately and follow the laws applicable to your visitors.

## Reporting a vulnerability

Open a GitHub security advisory for the repository rather than posting credentials or exploit details in a public issue.
