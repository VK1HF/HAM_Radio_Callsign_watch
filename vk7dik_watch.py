#!/usr/bin/python3
"""
vk7dik_watch.py — fast production watcher (configurable callsign)

This script is designed to let you know when your mates are on air and feeling sociable.

By default it is configured to watch the callsign **VK7DIK**.
To monitor a different callsign:
  - Change the `CALLSIGN` value in the config section.
  - Or make a copy of this script for each callsign you want to track,
    and run each file separately from `crontab`.

Features:
- Fetches the OnAirLogbook banner directly (no JS/browser)
- Logs every run to vk7dik_watch.log
- Keeps state in vk7dik_watch.json
- Sends Pushover only on OFFLINE -> ONLINE, max once per 2 hours
"""

import os
import json
import time
import requests
from datetime import datetime

# --- Config ---
BASE_DIR   = "/home/bitnami/VK7DIK"
LOG_FILE   = os.path.join(BASE_DIR, "vk7dik_watch.log")
STATE_FILE = os.path.join(BASE_DIR, "vk7dik_watch.json")

# Callsign to monitor (change this to watch a different station)
CALLSIGN   = "VK7DIK"

QRZ_URL     = f"https://www.qrz.com/db/{CALLSIGN}?tab=biography"
ONAIR_URL   = f"https://www.onairlogbook.com/qrz-onairlogbook-display-on-air-now.php?callsign={CALLSIGN.lower()}"
OFFLINE_TXT = "This banner displays my real time HF SSB status. Sorry I am QRT now."

# Pushover
PUSHOVER_USER  = "<key_here>"
PUSHOVER_TOKEN = "<key_here>"

COOLDOWN_SEC = 2 * 60 * 60
TIMEOUT      = 12
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Callsign-Watch/1.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last": "unknown", "last_notify": 0}

def save_state(state) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_pushover(message: str) -> None:
    try:
        r = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": PUSHOVER_TOKEN,
                "user": PUSHOVER_USER,
                "title": f"{CALLSIGN} Online",
                "message": message,
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        log("ALERT pushover sent")
    except Exception as e:
        log(f"ERROR pushover failed: {e}")

def fetch_banner_text() -> str:
    r = requests.get(ONAIR_URL, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text or ""

def classify_status(text: str) -> str:
    return "OFFLINE" if OFFLINE_TXT in text else "ONLINE"

def main():
    state = load_state()
    try:
        txt = fetch_banner_text()
        status = classify_status(txt)
    except Exception as e:
        log(f"ERROR fetch/classify: {e}")
        return

    log(f"status={status}, last={state['last']}, source=onairlogbook, callsign={CALLSIGN}")

    now = int(time.time())
    if state["last"] == "OFFLINE" and status == "ONLINE":
        if now - state.get("last_notify", 0) >= COOLDOWN_SEC:
            send_pushover(
                f"{CALLSIGN} appears ONLINE at {datetime.now().isoformat()}\nURL: {QRZ_URL}"
            )
            log("ALERT transition OFFLINE -> ONLINE")
            state["last_notify"] = now
        else:
            log("INFO transition detected but within cooldown")

    state["last"] = status
    save_state(state)

if __name__ == "__main__":


    main()
