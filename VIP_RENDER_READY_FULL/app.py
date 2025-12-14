from flask import Flask, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required
import sqlite3, datetime

# =====================
# App setup
# =====================
app = Flask(__name__)
app.secret_key = "CHANGE_ME"

login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================
# Auth
# =====================
class Admin(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    return Admin()

# =====================
# Database
# =====================
def conn():
    return sqlite3.connect("data.db")

def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            clicked_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS signups (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            user_id INTEGER,
            amount INTEGER,
            signed_at TEXT
        )
    """)

    c.commit()
    c.close()

# init database on startup
init_db()

# =====================
# Routes
# =====================

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>VIP System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f0f0f;
                color: #ffffff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .box {
                background: #1a1a1a;
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                width: 320px;
            }
            h1 { margin-bottom: 10px; }
            p { color: #bbbbbb; margin-bottom: 30px; }
            a {
                display: block;
                text-decoration: none;
                margin: 10px 0;
                padding: 12px;
                border-radius: 6px;
                background: #ff2d2d;
                color: #fff;
                font-weight: bold;
            }
            a.secondary { background: #444; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>VIP Content System</h1>
            <p>สมัคร VIP เพื่อเข้าถึงคอนเทนต์พิเศษ</p>

            <a href="/login">เข้าสู่ระบบแอดมิน</a>
            <a href="/go/1" class="secondary">สมัคร VIP</a>
            <a href="https://t.me/BRSmokeHub71626" class="secondary">ติดต่อ Telegram</a>
        </div>
    </body>
    </html>
    """

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == "admin123":
            login_user(Admin())
            return redirect("/dashboard")
    return """
    <form method="post">
        Password: <input name="password" type="password">
        <input type="submit" value="เข้าสู่ระบบ">
    </form>
    """

@app.route("/dashboard")
@login_required
def dashboard():
    c = conn()
    cur = c.cursor()

    cur.execute("SELECT COUNT(*) FROM clicks")
    clicks = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signups")
    signups = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount),0) FROM signups")
    revenue = cur.fetchone()[0]

    conversion = round((signups / clicks) * 100, 2) if clicks else 0
    c.close()

    return f"""
    <h2>VIP Dashboard</h2>
    <p>Clicks: {clicks}</p>
    <p>Signups: {signups}</p>
    <p>Revenue: {revenue} THB</p>
    <p>Conversion: {conversion}%</p>
    """

@app.route("/go/<int:pid>")
def go(pid):
    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO clicks (post_id, clicked_at) VALUES (?, ?)",
        (pid, datetime.datetime.utcnow().isoformat())
    )

    c.commit()
    c.close()

    # TODO: เปลี่ยนเป็นลิงก์จริงของคุณ
    return redirect("https://t.me/BRSmokeHub71626")

@app.route("/payment/webhook", methods=["POST"])
def payment():
    data = request.json or {}

    c = conn()
    cur = c.cursor()

    cur.execute(
        "INSERT INTO signups (post_id, user_id, amount, signed_at) VALUES (?, ?, ?, ?)",
        (
            data.get("post_id"),
            data.get("user_id"),
            data.get("amount"),
            datetime.datetime.utcnow().isoformat()
        )
    )

    c.commit()
    c.close()
    return {"status": "ok"}

# =====================
# Run
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
