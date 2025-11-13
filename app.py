from database.database import SessionLocal, ChannelStats
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from api_youtube import fetch_channel_infos
from sqlalchemy import func
from fastapi import APIRouter
import sqlite3
import pandas as pd
import json

router = APIRouter()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Đổi khóa thật khi deploy

# ==================== DB =====================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            display_name TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


def get_channel_stats_live():
    try:
        infos = fetch_channel_infos()  # will read API key from env
    except Exception:
        return []  # no API key or error
    return [
        {
            'channel_id': i['channel_id'],
            'name': i['name'],
            'subscribers': i['subscribers'],
            'views': i['views'],
            'videos':i['videos'],
            'likes':i['likes'],
            'comments':i['comments']
        } for i in infos
    ]


@app.route("/data")
def get_data():
    db = SessionLocal()
    try:
        # Fetch data from the database
        stats = db.query(ChannelStats).all()
        # Convert to a list of dictionaries
        if stats:
            data = [{
                'channel_id': s.channel_id,
                'name':s.name,
                'subscribers': s.subscribers,
                'views': s.views,
                'videos':s.videos,
                'likes':s.likes,
                'comments':s.comments
            } for s in stats]
            return jsonify(data)
        # DB empty -> try live fetch (requires YOUTUBE_API_KEY)
        live = get_channel_stats_live()
        return jsonify(live)
    finally:
        db.close()

@app.route("/")
def index():

    if "user" not in session:
        return redirect(url_for("auth"))
    
    # Lấy thể loại từ query string (?category=...)
    selected_category = request.args.get("category", "ALL")  # mặc định là ALL

    # Đọc dữ liệu CSV
    df = pd.read_csv("youtube_prediction_result.csv")

    # Đọc JSON
    with open("channels_info.json", "r", encoding="utf-8") as f:
        channels_info = pd.DataFrame(json.load(f))

    # Gộp 2 bảng theo tên kênh hoặc channel_id
    df = pd.merge(df, channels_info, on="name", how="left")

    # Nếu người dùng chọn một category cụ thể (không phải ALL)
    if selected_category != "ALL":
        df = df[df["category"].str.upper() == selected_category]

    data = df.to_dict(orient="records")

    return render_template(
        "index.html",
        data=data,
        selected_category=selected_category,
        user=session["user"]
    )


@app.route("/login")
@app.route("/register")
def auth_alias():
    mode = "register" if request.path == "/register" else "login"
    return redirect(url_for("auth", mode=mode))

@app.route("/auth", methods=["GET", "POST"])
def auth():
    mode = request.args.get("mode", "login")  # "login" hoặc "register"

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        # ============ Đăng ký ============
        if mode == "register":
            display_name = request.form["display_name"].strip()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            if c.fetchone():
                flash("Tên người dùng đã tồn tại!", "error")
            else:
                hashed_pw = generate_password_hash(password)
                c.execute(
                    "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
                    (username, hashed_pw, display_name)
                )
                conn.commit()
                flash("Đăng ký thành công! Mời bạn đăng nhập.", "success")
                return redirect(url_for("auth", mode="login"))

        # ============ Đăng nhập ============
        elif mode == "login":
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()
            if user and check_password_hash(user[2], password):
                session["user"] = user[3] or user[1]  # display_name nếu có, nếu không thì username
                flash("Đăng nhập thành công!", "success")
                return redirect(url_for("index"))
            else:
                flash("Sai tên đăng nhập hoặc mật khẩu!", "error")

        conn.close()

    return render_template("auth.html", mode=mode)



@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for("auth"))


@app.route("/api/chart-data")
def chart_data():
    db = SessionLocal()

    # ✅ Lấy dữ liệu mới nhất của mỗi channel
    subquery = db.query(
        ChannelStats.channel_id,
        func.max(ChannelStats.id).label("latest_id")
    ).group_by(ChannelStats.channel_id).subquery()

    rows = (
        db.query(ChannelStats)
        .join(subquery, ChannelStats.id == subquery.c.latest_id)
        .all()
    )

    db.close()

    result = [
        {
            "name": row.name,
            "views": row.views,
            "subscribers": row.subscribers,
            "category": row.category
        }
        for row in rows
    ]

    return jsonify(result)

@app.route("/fetch")
def fetch_data():
    from api_youtube import fetch_channel_infos
    data = fetch_channel_infos()
    return data


@app.errorhandler(500)
def handle_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
