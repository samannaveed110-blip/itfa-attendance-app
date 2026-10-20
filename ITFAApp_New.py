from flask import Flask, request, redirect, url_for, session, abort
import sqlite3
from datetime import date, datetime, timedelta
import secrets
import os

# ITFA Attendance System - EF 101
# Run with: python ITFAApp.py
# Optional QR images require: pip install qrcode[pil]

app = Flask(__name__)
app.secret_key = os.environ.get("ITFA_SECRET_KEY", "change-this-secret-before-online-use")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attendance.db")
ADMIN_PASSWORD = os.environ.get("ITFA_ADMIN_PASSWORD", "fezan123")

STUDENTS = [
    ("NABIA", "EE-001"),
    ("SADIA", "EE-002"),
    ("AIMAN KASHIF KHAN", "EE-003"),
    ("SAMAN NAVEED", "EE-004"),
    ("IQRA MUSHTAQ", "EE-005"),
    ("SYEDA SOHAIRAH ALI", "EE-006"),
    ("ZAINAB IRFAN", "EE-007"),
    ("SAMIA ATHAR", "EE-008"),
    ("WANIA HASSAN KHAN", "EE-009"),
    ("AREEZA REHAN", "EE-010"),
    ("FIZZAH JAMAL", "EE-011"),
    ("RUDAH SHOAIB KHAN", "EE-012"),
    ("MANAHIL MUZAMMIL", "EE-013"),
    ("SYEDA AMNA ATHAR", "EE-014"),
    ("SYEDA AAIZA IRFAN", "EE-015"),
    ("ABDUL HAMEED BHATTI", "EE-016"),
    ("MUNEEB AHMED SHAIKH", "EE-017"),
    ("SYED AYAAN HUSSAIN", "EE-018"),
    ("SYED DAYYAN AHMED", "EE-019"),
    ("AHSAN ASLAM", "EE-020"),
    ("ABDUL HADI", "EE-021"),
    ("ABDUL REHMAN", "EE-022"),
    ("MUHAMMAD RAYYAN KHAN GHAURI", "EE-023"),
    ("ABDUL RAFAY", "EE-024"),
    ("MUHAMMAD HAMZA", "EE-025"),
    ("MUHAMMAD KHIZER", "EE-026"),
    ("SYED MUJTABA AHMED ZAIDI", "EE-027"),
    ("SYED MUZAMMIL ADNAN", "EE-028"),
    ("MUHAMMAD SHAREEL KHILI", "EE-029"),
    ("SYED MUHAMMAD JARI ABBAS", "EE-030"),
    ("SYED ZOHAIB HUSSAIN", "EE-031"),
    ("MUHAMMAD ANAS PARACHA", "EE-032"),
    ("MUHAMMAD ROHAIL BAQAI", "EE-033"),
    ("MUHAMMAD BILAL SHEIKH", "EE-034"),
    ("SYED RASIB ALI", "EE-035"),
    ("SYED MUHAMMAD AHMED ALAM", "EE-036"),
    ("HAMMAD TARIQ", "EE-037"),
    ("ABDUL MUQEET SHAIKH", "EE-038"),
    ("GHULAM MOHIUDDIN HASHIR", "EE-039"),
    ("MEHTAB ALAM", "EE-040"),
    ("SHAHROZ IFTIKHAR", "EE-041"),
    ("ABDUL HASEEB", "EE-042"),
    ("MUHAMMAD NAQI ABBAS", "EE-043"),
    ("MUHAMMAD FAHAM KHAN", "EE-044"),
    ("ABDULLAH TAYYEB ZUBARI", "EE-045"),
    ("SARIM", "EE-046"),
]

CLASS_TYPES = ["Theory", "Practical"]


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def setup_db():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll TEXT NOT NULL,
                course TEXT NOT NULL DEFAULT 'ITFA',
                class_type TEXT NOT NULL DEFAULT 'Theory',
                status TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS qr_tokens (
                token TEXT PRIMARY KEY,
                class_type TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        """)
        # Existing database files are supported if they use the same attendance columns.


def page(title, body):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:Arial,sans-serif;background:#f3f5f9;margin:0;color:#172033}}
header{{background:#173b70;color:white;padding:18px 5%;}}
main{{max-width:1100px;margin:22px auto;padding:0 14px}}
.card{{background:white;padding:18px;border-radius:12px;box-shadow:0 2px 10px #0001;margin:14px 0;overflow-x:auto}}
a,button{{display:inline-block;padding:8px 11px;border-radius:7px;text-decoration:none;border:0;cursor:pointer;font-size:14px;margin:2px}}
a{{background:#e8eef8;color:#173b70}}button{{background:#173b70;color:white}}
input,select{{padding:9px;border:1px solid #ccd3df;border-radius:7px;margin:4px}}
table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:9px;border-bottom:1px solid #e2e6ed;text-align:left}}
th{{background:#edf2fa}}.present{{color:#137547;font-weight:bold}}.absent{{color:#b42318;font-weight:bold}}
.small{{color:#596579;font-size:13px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}
</style></head><body><header><h2>ITFA Attendance System</h2><div>Course: ITFA / EF 101 &nbsp; | &nbsp; Instructor: Sir Fezan</div></header>
<main>{body}</main></body></html>"""


def is_admin():
    return session.get("admin") is True


@app.route("/")
def home():
    body = """
    <div class="card"><h2>Welcome</h2>
    <p>Choose the portal you need.</p>
    <a href="/admin">Admin dashboard</a>
    <a href="/student">Student portal</a>
    <a href="/attendance">Attendance records</a>
    </div>
    """
    return page("ITFA Attendance", body)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not is_admin():
        if request.method == "POST":
            if request.form.get("password") == ADMIN_PASSWORD:
                session["admin"] = True
                return redirect(url_for("admin"))
            return page("Admin login", '<div class="card"><h3>Incorrect password.</h3><a href="/admin">Try again</a></div>')
        return page("Admin login", """
        <div class="card"><h2>Admin login</h2>
        <form method="post"><label>Admin password </label><input name="password" type="password" required>
        <button type="submit">Log in</button></form>
        <p class="small">Initial local password: <b>fezan123</b>. Change it before putting this app online.</p></div>""")

    rows = []
    with get_db() as con:
        for name, roll in STUDENTS:
            counts = con.execute(
                "SELECT COUNT(*) AS held, SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS attended "
                "FROM attendance WHERE roll=?",
                (roll,)
            ).fetchone()
            held = counts["held"] or 0
            attended = counts["attended"] or 0
            percent = round(attended * 100 / held, 1) if held else 0
            rows.append(
                f"<tr><td>{roll}</td><td>{name}</td><td>{held}</td><td>{attended}</td>"
                f"<td>{held-attended}</td><td>{percent}%</td><td>"
                f"<form style='display:inline' method='post' action='/mark/{roll}/Present'>"
                f"<input type='hidden' name='class_type' value='Theory'><button>Present (T)</button></form>"
                f"<form style='display:inline' method='post' action='/mark/{roll}/Absent'>"
                f"<input type='hidden' name='class_type' value='Theory'><button>Absent (T)</button></form>"
                f"<form style='display:inline' method='post' action='/mark/{roll}/Present'>"
                f"<input type='hidden' name='class_type' value='Practical'><button>Present (P)</button></form>"
                f"<form style='display:inline' method='post' action='/mark/{roll}/Absent'>"
                f"<input type='hidden' name='class_type' value='Practical'><button>Absent (P)</button></form>"
                "</td></tr>"
            )
    body = f"""
    <div class="card"><h2>Admin dashboard</h2>
    <p>Students: {len(STUDENTS)}. Attendance percentage is calculated from the records saved so far.</p>
    <form method="post" action="/new-qr">
    <label>QR class type</label><select name="class_type"><option>Theory</option><option>Practical</option></select>
    <button>Create 20-second QR attendance link</button></form>
    <a href="/attendance">View all records</a> <a href="/logout">Log out</a>
    </div>
    <div class="card"><table><tr><th>Roll</th><th>Student</th><th>Records</th><th>Present</th><th>Not present</th><th>Rate</th><th>Mark attendance</th></tr>
    {''.join(rows)}</table></div>"""
    return page("Admin dashboard", body)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/mark/<roll>/<status>", methods=["GET", "POST"])
def mark(roll, status):
    if not is_admin():
        return redirect(url_for("admin"))
    student = next((name for name, student_roll in STUDENTS if student_roll == roll), None)
    if student is None or status not in ("Present", "Absent"):
        abort(404)
    class_type = request.values.get("class_type", "Theory")
    if class_type not in CLASS_TYPES:
        class_type = "Theory"
    with get_db() as con:
        # One record per student, class type and date. Re-marking updates today's record.
        existing = con.execute(
            "SELECT id FROM attendance WHERE roll=? AND course='ITFA' AND class_type=? AND date=?",
            (roll, class_type, date.today().isoformat())
        ).fetchone()
        if existing:
            con.execute("UPDATE attendance SET status=? WHERE id=?", (status, existing["id"]))
        else:
            con.execute(
                "INSERT INTO attendance (roll, course, class_type, status, date) VALUES (?, 'ITFA', ?, ?, ?)",
                (roll, class_type, status, date.today().isoformat())
            )
    return redirect(url_for("admin"))


@app.route("/attendance")
def attendance():
    if not is_admin():
        return redirect(url_for("admin"))
    with get_db() as con:
        records = con.execute(
            "SELECT roll, course, class_type, status, date FROM attendance ORDER BY date DESC, roll"
        ).fetchall()
    rows = "".join(
        f"<tr><td>{r['date']}</td><td>{r['roll']}</td><td>{r['course']}</td>"
        f"<td>{r['class_type']}</td><td class='{'present' if r['status']=='Present' else 'absent'}'>{r['status']}</td></tr>"
        for r in records
    )
    return page("Attendance records", f"""
    <div class="card"><h2>Attendance records</h2><a href="/admin">Back to dashboard</a>
    <table><tr><th>Date</th><th>Roll</th><th>Course</th><th>Class type</th><th>Status</th></tr>
    {rows or '<tr><td colspan="5">No attendance records yet.</td></tr>'}</table></div>""")


@app.route("/student", methods=["GET", "POST"])
def student():
    selected_roll = request.values.get("roll", "")
    if not any(roll == selected_roll for _, roll in STUDENTS):
        options = "".join(f'<option value="{roll}">{roll} — {name}</option>' for name, roll in STUDENTS)
        return page("Student portal", f"""
        <div class="card"><h2>Student portal</h2><form method="get">
        <label>Select your student ID</label><select name="roll" required>{options}</select>
        <button>View attendance</button></form>
        <p class="small">This is a basic student lookup, not secure identity verification.</p></div>""")
    name = next(name for name, roll in STUDENTS if roll == selected_roll)
    sections = []
    with get_db() as con:
        for class_type in CLASS_TYPES:
            row = con.execute(
                "SELECT COUNT(*) AS held, SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS attended "
                "FROM attendance WHERE roll=? AND class_type=?",
                (selected_roll, class_type)
            ).fetchone()
            held = row["held"] or 0
            attended = row["attended"] or 0
            percent = round(attended * 100 / held, 1) if held else 0
            sections.append(
                f"<div class='card'><h3>{class_type}</h3><div class='grid'>"
                f"<div><b>Records / classes held</b><p>{held}</p></div>"
                f"<div><b>Present</b><p>{attended}</p></div>"
                f"<div><b>Absent</b><p>{held-attended}</p></div>"
                f"<div><b>Attendance rate</b><p>{percent}%</p></div></div></div>"
            )
    return page("Student portal", f"""
    <div class="card"><h2>{name}</h2><p>Student ID: {selected_roll}</p>
    <a href="/student">Choose another student</a></div>{''.join(sections)}""")


@app.route("/new-qr", methods=["POST"])
def new_qr():
    if not is_admin():
        return redirect(url_for("admin"))
    class_type = request.form.get("class_type", "Theory")
    if class_type not in CLASS_TYPES:
        class_type = "Theory"
    token = secrets.token_urlsafe(18)
    expires = datetime.now() + timedelta(seconds=20)
    with get_db() as con:
        con.execute("DELETE FROM qr_tokens")
        con.execute(
            "INSERT INTO qr_tokens (token, class_type, expires_at) VALUES (?, ?, ?)",
            (token, class_type, expires.isoformat())
        )
    link = "https://magma-prolonged-plasma.ngrok-free.dev" + url_for("qr_checkin", token=token) 
    try:
        import qrcode
        import io
        import base64
        image = qrcode.make(link)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        qr_html = f'<p><img alt="Attendance QR code" width="230" src="data:image/png;base64,{encoded}"></p>'
    except ImportError:
        qr_html = "<p>QR image library is not installed. The temporary link below still works.</p>"
    return page("Temporary QR", f"""
    <div class="card"><h2>{class_type} attendance QR</h2>{qr_html}
    <p>This link expires in 20 seconds.</p><p><a href="{link}">Open check-in link</a></p>
    <p class="small">For phones on another network, the app must be deployed to a public HTTPS address first.</p>
    <a href="/admin">Back to admin</a></div>""")


@app.route("/checkin/<token>", methods=["GET", "POST"])
def qr_checkin(token):
    with get_db() as con:
        qr = con.execute("SELECT * FROM qr_tokens WHERE token=?", (token,)).fetchone()
    if not qr or datetime.now() > datetime.fromisoformat(qr["expires_at"]):
        return page("QR expired", "<div class='card'><h2>QR expired</h2><p>Please ask the instructor for a new QR code.</p></div>"), 410
    if request.method == "POST":
        roll = request.form.get("roll", "")
        if not any(student_roll == roll for _, student_roll in STUDENTS):
            abort(400)
        with get_db() as con:
            existing = con.execute(
                "SELECT id FROM attendance WHERE roll=? AND course='ITFA' AND class_type=? AND date=?",
                (roll, qr["class_type"], date.today().isoformat())
            ).fetchone()
            if existing:
                con.execute("UPDATE attendance SET status='Present' WHERE id=?", (existing["id"],))
            else:
                con.execute(
                    "INSERT INTO attendance (roll, course, class_type, status, date) VALUES (?, 'ITFA', ?, 'Present', ?)",
                    (roll, qr["class_type"], date.today().isoformat())
                )
        return page("Attendance marked", "<div class='card'><h2>Attendance marked present!</h2></div>")
    options = "".join(f'<option value="{roll}">{roll} — {name}</option>' for name, roll in STUDENTS)
    return page("QR check-in", f"""
    <div class="card"><h2>{qr['class_type']} check-in</h2>
    <p>Choose your ID and submit before the QR expires.</p>
    <form method="post"><select name="roll" required>{options}</select><button>Mark me present</button></form></div>""")


setup_db()

if __name__ == "__main__":
    app.run(debug=True)
