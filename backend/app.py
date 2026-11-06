"""CyberCampus - fictional university portal (M111 P1, Group 2).
Local lab only. All data and accounts are FICTIONAL.
"""
import os, time, sqlite3, secrets, logging
from collections import defaultdict, deque
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

BASE = Path(__file__).resolve().parent
FRONT = BASE.parent / "frontend"
DB_PATH = BASE / "cybercampus.db"
LOG_DIR = BASE / "logs"
LOG_DIR.mkdir(exist_ok=True)

HOST = os.environ.get("CC_HOST", "127.0.0.1")   # keep loopback unless on an authorized private network
PORT = int(os.environ.get("CC_PORT", "5000"))
RATE_LIMIT = os.environ.get("CC_RATE_LIMIT", "off").lower() == "on"   # recommendation demo
RATE_MAX, RATE_WINDOW = 20, 10   # 20 requests / 10 s per IP on /api/test when enabled

app = Flask(__name__, static_folder=str(FRONT), static_url_path="")

# ---- server-side access log (to correlate with Wireshark timestamps) ----
logger = logging.getLogger("cybercampus")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_DIR / "access.log", encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(fh)

# ---- database ----
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, pw_hash TEXT,
        full_name TEXT, role TEXT, email TEXT, program TEXT);
    CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY, code TEXT, title TEXT, teacher TEXT, credits INTEGER, description TEXT);
    CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY, day TEXT, start TEXT, end TEXT, course_code TEXT, room TEXT);
    """)
    if con.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        con.executemany("INSERT INTO users(username,pw_hash,full_name,role,email,program) VALUES(?,?,?,?,?,?)", [
            ("student1", generate_password_hash("Demo#2026"), "Student Demo (fictional)", "student", "student1@cybercampus.test", "Cybersecurity Year 1"),
            ("teacher1", generate_password_hash("Demo#2026"), "Prof. Example (fictional)", "teacher", "teacher1@cybercampus.test", "Network Security"),
        ])
        con.executemany("INSERT INTO courses(code,title,teacher,credits,description) VALUES(?,?,?,?,?)", [
            ("M111", "Introduction to Cybersecurity", "Prof. Example", 4, "Core concepts: threats, risks, controls."),
            ("M112", "Computer Networks", "Prof. Example", 4, "TCP/IP, HTTP, DNS and packet analysis."),
            ("M113", "Web Technologies", "Prof. Sample", 3, "HTML, CSS, JavaScript and Flask basics."),
            ("M114", "Operating Systems", "Prof. Sample", 3, "Linux, processes and permissions."),
            ("M115", "Databases", "Prof. Demo", 3, "SQL and data modelling."),
        ])
        con.executemany("INSERT INTO schedule(day,start,end,course_code,room) VALUES(?,?,?,?,?)", [
            ("Monday", "08:30", "10:30", "M111", "Room A1"),
            ("Monday", "10:45", "12:45", "M112", "Lab N2"),
            ("Tuesday", "08:30", "10:30", "M113", "Lab D1"),
            ("Wednesday", "14:00", "16:00", "M114", "Room B3"),
            ("Thursday", "10:45", "12:45", "M115", "Room A2"),
        ])
        con.commit()
    con.close()

# ---- tiny in-memory sessions and rate limiter ----
SESSIONS = {}              # token -> username
HITS = defaultdict(deque)  # ip -> timestamps

def current_user():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        username = SESSIONS.get(auth[7:])
        if username:
            con = db(); u = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone(); con.close()
            return u
    return None

@app.after_request
def log_request(resp):
    logger.info("%s %s %s %s -> %s", request.remote_addr, request.method, request.full_path.rstrip("?"),
                request.headers.get("User-Agent", "-")[:40], resp.status_code)
    return resp

# ---- pages ----
@app.route("/")
def home():
    return send_from_directory(FRONT, "index.html")

@app.errorhandler(404)
def not_found(_e):
    if request.path.startswith("/api/"):
        return jsonify(error="not_found", path=request.path), 404
    return send_from_directory(FRONT, "404.html"), 404

# ---- API ----
@app.get("/api/health")
def health():
    return jsonify(status="ok", service="CyberCampus", time=time.strftime("%Y-%m-%dT%H:%M:%S"))

@app.get("/api/courses")
def courses():
    con = db(); rows = [dict(r) for r in con.execute("SELECT * FROM courses")]; con.close()
    return jsonify(rows)

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    con = db(); u = con.execute("SELECT * FROM users WHERE username=?", (data.get("username", ""),)).fetchone(); con.close()
    if u and check_password_hash(u["pw_hash"], data.get("password", "")):
        token = secrets.token_hex(16)
        SESSIONS[token] = u["username"]
        return jsonify(token=token, username=u["username"], role=u["role"])
    return jsonify(error="invalid_credentials"), 401

@app.post("/api/logout")
def logout():
    SESSIONS.pop(request.headers.get("Authorization", "")[7:], None)
    return jsonify(status="logged_out")

@app.get("/api/profile")
def profile():
    u = current_user()
    if not u:
        return jsonify(error="unauthorized"), 401
    return jsonify(username=u["username"], full_name=u["full_name"], role=u["role"], email=u["email"], program=u["program"])

@app.get("/api/schedule")
def schedule():
    if not current_user():
        return jsonify(error="unauthorized"), 401
    con = db(); rows = [dict(r) for r in con.execute("SELECT * FROM schedule")]; con.close()
    return jsonify(rows)

@app.get("/api/test")
def test_endpoint():
    """Harmless endpoint used for the controlled repeated-request scenario."""
    if RATE_LIMIT:
        now, q = time.time(), HITS[request.remote_addr]
        while q and now - q[0] > RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_MAX:
            resp = jsonify(error="too_many_requests")
            resp.status_code = 429
            resp.headers["Retry-After"] = str(RATE_WINDOW)
            return resp
        q.append(now)
    return jsonify(ok=True, ts=time.time())

if __name__ == "__main__":
    init_db()
    print(f"CyberCampus (fictional lab) on http://{HOST}:{PORT}  rate-limit={'ON' if RATE_LIMIT else 'OFF'}")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
