#!/usr/bin/env python3
"""Poll every Minehut server in servers.txt, append readings to data.csv.
Run by GitHub Actions.  Schema: ts,server,online,count"""
import csv, os, time, requests

FILE = "data.csv"
SERVERS_FILE = "servers.txt"
NEW_HEADER = ["ts", "server", "online", "count"]
OLD_HEADER = ["ts", "online", "count"]

def load_servers():
    if not os.path.exists(SERVERS_FILE):
        return ["AltarExtra"]
    out = []
    for line in open(SERVERS_FILE):
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out or ["AltarExtra"]

def migrate_if_needed():
    """Upgrade an old 3-column data.csv in place (tags existing rows AltarExtra)."""
    if not os.path.exists(FILE):
        return
    with open(FILE, newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] == NEW_HEADER:
        return
    if rows[0] == OLD_HEADER:
        out = [NEW_HEADER]
        for r in rows[1:]:
            if len(r) >= 3 and r[0].strip().isdigit():
                out.append([r[0], "AltarExtra", r[1], r[2]])
        with open(FILE, "w", newline="") as f:
            csv.writer(f).writerows(out)
        print(f"migrated {len(out)-1} rows to new schema")

def poll(server):
    url = f"https://api.minehut.com/server/{server}?byName=true"
    r = requests.get(url, headers={"User-Agent": "altar-tracker"}, timeout=20)
    r.raise_for_status()
    s = r.json()["server"]
    return (1 if s.get("online") else 0, int(s.get("playerCount") or 0))

def main():
    servers = load_servers()
    migrate_if_needed()
    new = not os.path.exists(FILE)
    ts = int(time.time())
    rows = []
    for srv in servers:
        try:
            online, count = poll(srv)
            rows.append([ts, srv, online, count])
            print("ok", srv, online, count)
        except Exception as e:
            print("poll failed", srv, e)
    if not rows:
        print("no readings this tick"); return
    with open(FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(NEW_HEADER)
        w.writerows(rows)

if __name__ == "__main__":
    main()
