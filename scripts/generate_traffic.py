"""Controlled traffic generator for the CyberCampus lab (M111 P1).
Targets ONLY loopback / private addresses. Low volume, no degradation.

  python scripts/generate_traffic.py normal
  python scripts/generate_traffic.py abnormal      # rapid repeated requests to /api/test
  python scripts/generate_traffic.py ambiguous     # mixed benign-but-odd activity
  python scripts/generate_traffic.py all
"""
import argparse, ipaddress, json, sys, time, urllib.request, urllib.error

def check_host(h):
    try:
        ip = ipaddress.ip_address(h)
    except ValueError:
        sys.exit("Use an IP address (127.0.0.1 or a private lab IP).")
    if not (ip.is_loopback or ip.is_private):
        sys.exit("Refusing: target is not loopback/private. Lab use only.")

def req(base, path, method="GET", body=None, token=None, ua="CyberCampusLab/1.0"):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(base + path, data=data, method=method)
    r.add_header("User-Agent", ua)
    if data: r.add_header("Content-Type", "application/json")
    if token: r.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(r, timeout=5) as resp:
            code, payload = resp.status, resp.read()
    except urllib.error.HTTPError as e:
        code, payload = e.code, e.read()
    print(f"{time.strftime('%H:%M:%S')} {method:4} {path:22} -> {code}")
    try: return code, json.loads(payload)
    except Exception: return code, None

def normal(b):
    print("== NORMAL: browsing session ==")
    req(b, "/"); time.sleep(1)
    req(b, "/courses.html"); req(b, "/api/courses"); time.sleep(1)
    _, d = req(b, "/api/login", "POST", {"username": "student1", "password": "Demo#2026"})
    tok = d and d.get("token"); time.sleep(1)
    req(b, "/api/profile", token=tok); req(b, "/api/schedule", token=tok); time.sleep(1)
    req(b, "/page-inexistante.html")          # normal 404 (resource that does not exist)
    req(b, "/api/logout", "POST", token=tok)

def abnormal(b, n=40, delay=0.05):
    print(f"== ABNORMAL (benign): {n} rapid requests to /api/test ==")
    for _ in range(n):
        req(b, "/api/test"); time.sleep(delay)

def ambiguous(b):
    print("== AMBIGUOUS: odd but plausibly innocent ==")
    for pw in ("wrong1", "wrong2", "wrong3"):   # forgotten password
        req(b, "/api/login", "POST", {"username": "student1", "password": pw}); time.sleep(2)
    req(b, "/robots.txt"); req(b, "/favicon.ico"); req(b, "/admin"); time.sleep(1)   # crawler/curious user
    for _ in range(6):                          # impatient refresh
        req(b, "/api/courses", ua="Mozilla/5.0 (refresh)"); time.sleep(0.3)
    req(b, "/api/schedule")                     # unauthenticated -> 401
    _, d = req(b, "/api/login", "POST", {"username": "student1", "password": "Demo#2026"})
    req(b, "/api/schedule", token=d and d.get("token"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario", choices=["normal", "abnormal", "ambiguous", "all"])
    ap.add_argument("--host", default="127.0.0.1"); ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--count", type=int, default=40, help="requests for 'abnormal'")
    a = ap.parse_args(); check_host(a.host)
    base = f"http://{a.host}:{a.port}"
    if a.scenario in ("normal", "all"): normal(base); time.sleep(3)
    if a.scenario in ("abnormal", "all"): abnormal(base, a.count); time.sleep(3)
    if a.scenario in ("ambiguous", "all"): ambiguous(base)
