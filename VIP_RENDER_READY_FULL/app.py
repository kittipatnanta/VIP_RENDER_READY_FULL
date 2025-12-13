
from flask import Flask, redirect, request
from flask_login import LoginManager, UserMixin, login_user, login_required
import sqlite3, datetime

app = Flask(__name__)
app.secret_key = "CHANGE_ME"

login_manager = LoginManager(app)

class Admin(UserMixin):
    id = 1

@login_manager.user_loader
def load_user(user_id):
    return Admin()

def conn():
    return sqlite3.connect("data.db")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST" and request.form.get("password")=="admin123":
        login_user(Admin())
        return redirect("/dashboard")
    return "<form method=post>Password:<input name=password><input type=submit></form>"

@app.route("/dashboard")
@login_required
def dashboard():
    c = conn()
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS clicks (id INTEGER PRIMARY KEY, post_id INTEGER, clicked_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS signups (id INTEGER PRIMARY KEY, post_id INTEGER, user_id INTEGER, amount INTEGER, signed_at TEXT)")
    cur.execute("SELECT COUNT(*) FROM clicks")
    clicks = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM signups")
    signups = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(amount),0) FROM signups")
    revenue = cur.fetchone()[0]
    conversion = round((signups/clicks)*100,2) if clicks else 0
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
    cur.execute("INSERT INTO clicks (post_id, clicked_at) VALUES (?,?)",
                (pid, datetime.datetime.utcnow().isoformat()))
    c.commit()
    c.close()
    return redirect("https://example.com")

@app.route("/payment/webhook", methods=["POST"])
def payment():
    data = request.json or {}
    c = conn()
    cur = c.cursor()
    cur.execute("INSERT INTO signups (post_id,user_id,amount,signed_at) VALUES (?,?,?,?)",
                (data.get("post_id"), data.get("user_id"), data.get("amount"),
                 datetime.datetime.utcnow().isoformat()))
    c.commit()
    c.close()
    return {"status":"ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
