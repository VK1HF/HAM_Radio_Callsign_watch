# vk7dik_watch

### What is this?
A lightweight Python script that monitors the online/offline status of amateur radio callsigns by checking the QRZ *OnAirLogbook* banner.  

It logs results on every run and sends a **Pushover** notification whenever the station transitions from **OFFLINE → ONLINE** (with a 2-hour cooldown to prevent spam).  

By default, this script is set up for **VK7DIK**, but you can easily change the callsign in the config section. If you want to track multiple callsigns, make a copy of the script for each one and run them separately from `crontab`.

## This script is designed to let you know when your mates are on air and feeling sociable.  (if they are not, they will not update their status) 

---

## Why Pushover?
Pushover is a simple, reliable push notification service that delivers alerts straight to your phone, tablet, or desktop.  

Compared to traditional channels like **SMS, email, or carrier TXT**, Pushover has some big advantages:
- **Instant delivery** — no carrier delays or spam filters.  
- **Cross-platform** — iOS, Android, and desktop clients available.  
- **Configurable** — custom sounds, priorities, and quiet hours.  
- **Reliable** — works anywhere you have internet.  

For hobby projects like this one, Pushover is perfect: if your mate comes online at 3 am, you’ll know instantly.  
👉 Try it yourself at [https://pushover.net](https://pushover.net).

here is a good video about it : https://www.youtube.com/watch?v=z_e39lmd5b4

---

## How it works
- Fetches the OnAirLogbook iframe directly:  
  `https://www.onairlogbook.com/qrz-onairlogbook-display-on-air-now.php?callsign=<callsign>`
- Classifies status:
  - If the offline banner text is present → **OFFLINE**  
  - Otherwise → **ONLINE**
- Logs every run to `vk7dik_watch.log`  
- Maintains state in `vk7dik_watch.json` (last status + last notify timestamp)  
- Sends a **Pushover** alert only on **OFFLINE → ONLINE** transitions (with 2-hour cooldown).  

---

## Files
- `vk7dik_watch.py` — the watcher script  
- `vk7dik_watch.log` — rolling log of status checks  
- `vk7dik_watch.json` — state tracking  

---




## Setup

Copy vk7dik_watch.py into your server directory (e.g. /home/bitnami/VK7DIK/).

Make it executable:

chmod +x /home/bitnami/VK7DIK/vk7dik_watch.py

Edit the script to update the CALLSIGN value in the config section.

To monitor multiple callsigns, duplicate the script (e.g. vk2abc_watch.py) and set a different callsign in each file.

Add a cron job to run the script every 5 minutes:

*/5 * * * * /home/bitnami/VK7DIK/vk7dik_watch.py



## Example log entries

Every run appends one line to vk7dik_watch.log. When status changes from OFFLINE → ONLINE, extra alert lines are logged.

[2025-09-15 10:25:00] status=OFFLINE, last=ONLINE, source=onairlogbook, callsign=VK7DIK  
[2025-09-15 12:40:00] status=ONLINE, last=OFFLINE, source=onairlogbook, callsign=VK7DIK  
[2025-09-15 12:40:00] ALERT pushover sent  
[2025-09-15 12:40:00] ALERT transition OFFLINE -> ONLINE  




## Dependencies
- Python 3.11+  
- [`requests`](https://pypi.org/project/requests/)  

Install via pip:
pip install requests






