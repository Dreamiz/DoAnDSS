from database.database import SessionLocal, ChannelStats
from flask import Flask, jsonify, render_template
from api_youtube import fetch_channel_infos
from sqlalchemy import func
from fastapi import APIRouter
import pandas as pd

router = APIRouter()

app = Flask(__name__)

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
    # Đọc dữ liệu CSV do models.py tạo ra
    df = pd.read_csv("youtube_prediction_result.csv")

    # Chuyển DataFrame sang danh sách dict để render dễ hơn
    data = df.to_dict(orient="records")

    # Gửi dữ liệu sang template HTML
    return render_template("index.html", data=data)


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
            "subscribers": row.subscribers
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
