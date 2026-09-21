# Installation

## Base system

Install a current 64-bit Raspberry Pi OS Lite image. In Raspberry Pi Imager, choose a generic hostname, configure networking and add an SSH public key. Reserve an address in the router by MAC address if predictable LAN access is useful.

Update while external power is stable and the UPS is charged:

```bash
sudo apt update
sudo apt full-upgrade
sudo reboot
```

Enable I²C and SPI with `sudo raspi-config`. Append `config/config.txt.snippet` to `/boot/firmware/config.txt` once, then reboot. If orientation is wrong, try another supported `rotate` value.

## Install the appliance

```bash
git clone https://github.com/YOUR_ACCOUNT/webhosting-deck.git
cd webhosting-deck
cp config/dashboard.example.json config/dashboard.json
nano config/dashboard.jsonsudo bash scripts/install.sh
sudo reboot
```

The installer deploys Nginx, an isolated Python environment, the dashboard service and a placeholder page. It intentionally does not install Cloudflare credentials.

## Deploy your static website

Place the built site under `/var/www/webhosting-deck/`, then validate and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Keep the website's source elsewhere under version control. Avoid destructive synchronization options until both source and destination paths have been checked and backed up.
