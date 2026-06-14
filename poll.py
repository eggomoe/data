#!/usr/bin/env python3
"""Take one AltarExtra reading and append it to data.csv. Run by GitHub Actions."""
import csv, os, time, requests

API  = "https://api.minehut.com/server/AltarExtra?byName=true"
FILE = "data.csv"

try:
    r = requests.get(API, headers={"User-Agent": "altar-tracker"}, timeout=20)
    r.raise_for_status()
    s = r.json()["server"]
    online = 1 if s.get("online") else 0
    count  = int(s.get("playerCount") or 0)
except Exception as e:
    print("poll failed (skipping this tick):", e)
    raise SystemExit(0)  # green run, just no new row

new = not os.path.exists(FILE)
with open(FILE, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["ts", "online", "count"])
    w.writerow([int(time.time()), online, count])
print("ok", online, count)
