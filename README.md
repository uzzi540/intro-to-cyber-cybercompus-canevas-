# M111-G2-CyberCampus

Fictional university portal for the **M111 - P1 network traffic investigation** (ENSIASD Taroudant, Group 2).
Flask + SQLite backend, plain HTML/CSS/JS frontend. **Local lab only - all data and accounts are fictional.**

## Quick start
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/app.py             # http://127.0.0.1:5000
```
Demo accounts (fictional): `student1` / `teacher1`, password `Demo#2026`.

Options (environment variables): `CC_HOST` (default 127.0.0.1), `CC_PORT` (5000), `CC_RATE_LIMIT=on` (enables 429 on `/api/test`).
If loopback capture is hard, run on a private network with `CC_HOST=0.0.0.0` between two personal, authorized devices only.

## Pages
`/` home, `/courses.html`, `/login.html`, `/profile.html` (auth), `/schedule.html` (auth), any missing URL -> 404.

## API
| Method | Path | Auth | Responses |
|---|---|---|---|
| GET | `/api/health` | no | 200 |
| GET | `/api/courses` | no | 200 |
| POST | `/api/login` | no | 200 / 401 |
| POST | `/api/logout` | token | 200 |
| GET | `/api/profile` | token | 200 / 401 |
| GET | `/api/schedule` | token | 200 / 401 |
| GET | `/api/test` | no | 200 / 429 (rate limit on) |
| GET | unknown path | - | 404 |

## Wireshark lab
1. Install Wireshark (+ Npcap on Windows, tick "Support loopback traffic").
2. Capture on the loopback interface, filter `tcp.port == 5000`.
3. Generate traffic:
```bash
python scripts/generate_traffic.py normal
python scripts/generate_traffic.py abnormal --count 40
python scripts/generate_traffic.py ambiguous
```
4. Save captures in `captures/`, screenshots in `screenshots/`. Server log with timestamps: `backend/logs/access.log`.
5. Analysis templates: `network-analysis/filters.md`, `network-analysis/timeline_and_risks.md`. Diagram: `diagrams/architecture.svg`.

Advanced (optional): compare HTTP vs HTTPS locally - e.g. `ssl_context="adhoc"` in `app.run` (needs `pip install cryptography`) with a self-signed certificate.

## Layout
```
frontend/ backend/ scripts/ network-analysis/ captures/ screenshots/ diagrams/ docs/ README.md requirements.txt
```
Workflow: feature branch -> Pull Request -> Member 1 reviews -> merge to `main`.

## Safety
Only machines/accounts owned by the group or explicitly authorized. No public targets, no scans, no real data. The traffic script refuses non-private IPs.
