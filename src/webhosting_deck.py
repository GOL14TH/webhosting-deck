#!/usr/bin/env python3
"""Framebuffer status dashboard for the Webhosting Deck reference build."""

import argparse
import hashlib
import ipaddress
import json
import os
import secrets
import socket
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from smbus2 import SMBus

WIDTH, HEIGHT = 480, 320
BG, PANEL, MUTED, WHITE = "#070a0e", "#111820", "#94a3b8", "#f8fafc"
ORANGE, GREEN, RED, AMBER = "#ff4d12", "#22c55e", "#ef4444", "#f59e0b"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_config(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


class INA219:
    """Minimal Waveshare UPS HAT (D) INA219 reader."""

    def __init__(self, address=0x43, bus=1):
        self.bus = SMBus(bus)
        self.address = address
        self.calibration = 4096
        self.write(0x05, self.calibration)
        # 32 V range, gain /8, 32-sample ADCs, continuous conversions.
        self.write(0x00, 0x3EEF)

    def write(self, register, value):
        self.bus.write_i2c_block_data(
            self.address, register, [(value >> 8) & 0xFF, value & 0xFF]
        )

    def read(self, register, signed=False):
        data = self.bus.read_i2c_block_data(self.address, register, 2)
        value = (data[0] << 8) | data[1]
        if signed and value > 32767:
            value -= 65536
        return value

    def sample(self):
        # Restore calibration in case it reset after a bus or power event.
        self.write(0x05, self.calibration)
        voltage = (self.read(0x02) >> 3) * 0.004
        current_ma = self.read(0x04, signed=True) * 0.1
        power_w = self.read(0x03) * 0.002
        return voltage, current_ma, power_w


def local_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "NO NETWORK"
    finally:
        sock.close()


def website_online(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            return 200 <= response.status < 400
    except Exception:
        return False


def cpu_temp():
    try:
        return int(Path("/sys/class/thermal/thermal_zone0/temp").read_text()) / 1000
    except (OSError, ValueError):
        return 0.0


def load_state(path):
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if "salt" in state and "visitors" in state:
            return state
    except (OSError, ValueError, TypeError):
        pass
    return {"salt": secrets.token_hex(16), "visitors": {}}


def visitor_counts(log_path, state_path, window_seconds):
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state = load_state(state_path)
    visitors = state["visitors"]
    salt = bytes.fromhex(state["salt"])

    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-5000:]
    except OSError:
        lines = []

    for line in lines:
        fields = line.split("|", 4)
        if len(fields) != 5:
            continue
        stamp, address, status, method, _uri = fields
        if method not in {"GET", "HEAD"} or not status.startswith(("2", "3")):
            continue
        try:
            ipaddress.ip_address(address)
            seen = datetime.fromisoformat(stamp).timestamp()
        except (ValueError, TypeError):
            continue
        digest = hashlib.blake2b(address.encode(), key=salt, digest_size=12).hexdigest()
        visitors[digest] = max(float(visitors.get(digest, 0)), seen)

    now = time.time()
    state_path.write_text(json.dumps(state, separators=(",", ":")), encoding="utf-8")
    return sum(1 for seen in visitors.values() if now - seen <= window_seconds), len(visitors)


def card(draw, box, label, value, accent=WHITE):
    draw.rounded_rectangle(box, radius=9, fill=PANEL, outline="#263241", width=1)
    x1, y1, _x2, _y2 = box
    draw.text((x1 + 12, y1 + 8), label, font=font(12, True), fill=MUTED)
    draw.text((x1 + 12, y1 + 27), value, font=font(20, True), fill=accent)


def render(config, sensor):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    online = website_online(config["health_url"])
    current_viewers, total_viewers = visitor_counts(
        Path(config["access_log"]),
        Path(config["state_file"]),
        int(config.get("visitor_window_seconds", 300)),
    )

    try:
        voltage, raw_current_ma, power_w = sensor.sample()
        current_ma = raw_current_ma * int(config.get("current_polarity", 1))
        low = float(config.get("battery_empty_v", 3.0))
        high = float(config.get("battery_full_v", 4.2))
        percent = max(0, min(100, round((voltage - low) / (high - low) * 100)))
        threshold = float(config.get("current_idle_threshold_ma", 10))
        if current_ma > threshold:
            state, state_color = "DISCHARGING", RED
        elif current_ma < -threshold:
            state, state_color = "CHARGING", GREEN
        else:
            state, state_color = "IDLE / BALANCED", AMBER
    except Exception:
        voltage = current_ma = power_w = 0.0
        percent, state, state_color = 0, "UPS READ ERROR", RED

    draw.text((14, 10), config.get("title", "WEBHOSTING DECK"), font=font(17, True), fill=WHITE)
    draw.text((14, 31), config.get("subtitle", "WEB + POWER STATUS"), font=font(10), fill=MUTED)
    draw.ellipse((368, 13, 380, 25), fill=GREEN if online else RED)
    draw.text((388, 11), "WEBSITE", font=font(9, True), fill=MUTED)
    draw.text((388, 23), "ONLINE" if online else "OFFLINE", font=font(13, True), fill=GREEN if online else RED)

    draw.text((14, 58), "UPS BATTERY", font=font(11, True), fill=MUTED)
    draw.text((14, 72), f"{percent}%", font=font(44, True), fill=WHITE)
    draw.text((172, 65), state, font=font(13, True), fill=state_color)
    draw.rounded_rectangle((172, 89, 466, 103), radius=7, fill="#263241")
    draw.rounded_rectangle((172, 89, 172 + int(294 * percent / 100), 103), radius=7, fill=state_color)

    card(draw, (12, 112, 155, 172), "VOLTAGE", f"{voltage:.2f} V", GREEN)
    card(draw, (168, 112, 311, 172), "CURRENT", f"{abs(current_ma)/1000:.2f} A", WHITE)
    card(draw, (324, 112, 468, 172), "POWER", f"{power_w:.2f} W", ORANGE)
    card(draw, (12, 182, 155, 242), "VIEWERS NOW", str(current_viewers), GREEN)
    card(draw, (168, 182, 311, 242), "TOTAL VIEWERS", str(total_viewers), WHITE)
    card(draw, (324, 182, 468, 242), "CPU TEMP", f"{cpu_temp():.0f} C", AMBER)

    draw.text((14, 262), local_ip(), font=font(15, True), fill=WHITE)
    draw.text((14, 285), f"{datetime.now():%d %b %Y  %H:%M:%S}", font=font(12), fill=MUTED)
    return image


def write_frame(image, framebuffer):
    rgb = image.tobytes()
    data = bytearray(WIDTH * HEIGHT * 2)
    output = 0
    for position in range(0, len(rgb), 3):
        red, green, blue = rgb[position : position + 3]
        value = ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)
        data[output] = value & 0xFF
        data[output + 1] = value >> 8
        output += 2
    with framebuffer.open("wb", buffering=0) as device:
        device.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    address = int(str(config.get("ina219_address", "0x43")), 0)
    sensor = INA219(address=address)
    framebuffer = Path(config.get("framebuffer", "/dev/fb0"))

    while True:
        try:
            write_frame(render(config, sensor), framebuffer)
        except Exception as error:
            print(f"dashboard error: {error}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
