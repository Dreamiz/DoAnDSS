import os
import warnings
import json
from time import sleep
from dotenv import load_dotenv
from typing import List, Optional, Dict
from googleapiclient.discovery import build
from database import save_channel_stats, init_db

warnings.filterwarnings("ignore")
load_dotenv()
init_db()

API_KEYS = [os.getenv(f"API_KEY_{i}") for i in range(1, 6) if os.getenv(f"API_KEY_{i}")]

import json

def load_channel_ids(path="D:\Quan\Practice_Data\my_flask_app\channel.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(set(data.get("channels", [])))  # bỏ trùng ID

DEFAULT_CHANNEL_IDS = load_channel_ids()


def build_youtube_client(api_key: str):
    return build("youtube", "v3", developerKey=api_key)

def rate_limited_request(request, retries: int = 3, delay: float = 1.0):
    last_exc = None
    for attempt in range(retries):
        try:
            return request.execute()
        except Exception as e:
            last_exc = e
            print(f"⚠️ API error: {e}")
            if 'quota' in str(e).lower() and attempt < retries - 1:
                print("🔁 Quota exceeded, retrying with delay...")
                sleep(delay)
                delay *= 2
                continue
            raise
    raise last_exc

def fetch_channel_infos(api_key: Optional[str] = None, channel_ids: Optional[List[str]] = None) -> List[Dict]:
    keys = [k for k in API_KEYS if k]
    key = api_key or (keys[0] if keys else None)
    if not key:
        raise RuntimeError("No YouTube API key configured.")

    yt = build_youtube_client(key)
    ids = list(channel_ids or DEFAULT_CHANNEL_IDS)

    print(f"📡 Fetching data for {len(ids)} channels...")

    resp = rate_limited_request(
        yt.channels().list(part="snippet,statistics", id=",".join(ids))
    )
    items = resp.get("items", [])
    out = []
    for item in items:
        cid = item.get("id")
        cname = item.get("snippet", {}).get("title")
        stats = item.get("statistics", {})

        print(f"\n📊 Fetching data for: {cname}")

        # Lấy video mới nhất
        uploads_resp = rate_limited_request(
            yt.search().list(
                part="id",
                channelId=cid,
                order="date",
                maxResults=1
            )
        )
        video_items = uploads_resp.get("items", [])
        video_id = video_items[0]["id"]["videoId"] if video_items else None

        like_count, comment_count = 0, 0
        if video_id:
            video_resp = rate_limited_request(
                yt.videos().list(
                    part="statistics",
                    id=video_id
                )
            )
            v_stats = video_resp["items"][0]["statistics"]
            like_count = int(v_stats.get("likeCount", 0))
            comment_count = int(v_stats.get("commentCount", 0))
        data = {
            "channel_id": item.get("id"),
            "name": item.get("snippet", {}).get("title"),
            "subscribers": int(stats.get("subscriberCount", 0) or 0),
            "views": int(stats.get("viewCount", 0) or 0),
            "videos": int(stats.get("videoCount", 0) or 0),
            "likes": int(like_count),
            "comments": int(comment_count)
        }
        out.append(data)

        # 🔹 Lưu vào database
        save_channel_stats(
            channel_id=data["channel_id"],
            name=data["name"],
            subs=data["subscribers"],
            views=data["views"],
            videos=data["videos"],
            likes=data["likes"],
            comments=data["comments"],
        )

    return out

if __name__ == "__main__":
    data = fetch_channel_infos()
    print("✅ Fetched data:")
    print(data)
