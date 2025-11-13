import os
import json
import sqlite3
import warnings
from time import sleep
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Optional, Dict
from googleapiclient.discovery import build
from database import save_channel_stats, init_db

warnings.filterwarnings("ignore")
BASE_DIR = Path(__file__).parent
load_dotenv()
init_db()

API_KEYS = [os.getenv(f"API_KEY_{i}") for i in range(1, 6) if os.getenv(f"API_KEY_{i}")]

import json

def load_channel_groups(path=None):
    # Nếu path không được cung cấp, sử dụng đường dẫn tương đối
    if path is None:
        path = BASE_DIR / "channel.json"  # Tương đương với BASE_DIR/channel.json

    # Mở tệp bằng path đã được xác định
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data # Nên trả về data
    
    # Lấy từng nhóm (trả về dict)
    channel_groups = {}
    for key, ids in data.items():
        if isinstance(ids, list):  # chỉ lấy các list
            channel_groups[key] = list(set(ids))  # bỏ trùng ID

    return channel_groups

DEFAULT_CHANNEL_GROUPS = load_channel_groups()


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

    key_index = 0
    yt = build_youtube_client(keys[key_index])

    all_data = []

    for group_name, ids in DEFAULT_CHANNEL_GROUPS.items():
        print(f"\n==============================")
        print(f"📂 Nhóm: {group_name} ({len(ids)} kênh)")
        print(f"==============================")

        # API chỉ cho phép lấy tối đa 50 ID / 1 request
        for i in range(0, len(ids), 50):
            batch = ids[i:i + 50]

            try:
                resp = rate_limited_request(
                    yt.channels().list(part="snippet,statistics,contentDetails", id=",".join(batch))
                )
            except Exception as e:
                print(f"❌ Lỗi với batch {i//50 + 1}: {e}")
                # thử đổi API key khác nếu còn
                key_index = (key_index + 1) % len(keys)
                yt = build_youtube_client(keys[key_index])
                continue

            for item in resp.get("items", []):
                cid = item.get("id")
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                details = item.get("contentDetails", {})

                data = {
                    "group": group_name,
                    "channel_id": cid,
                    "name": snippet.get("title"),
                    "customUrl": snippet.get("customUrl"),
                    "description": snippet.get("description"),
                    "country": snippet.get("country") or "N/A", 
                    "publishedAt": snippet.get("publishedAt"), # chưa cập nhật vào DB
                    "thumbnails": snippet.get("thumbnails"), # chưa cập nhật vào json
                    "subscribers": int(stats.get("subscriberCount", 0) or 0),
                    "views": int(stats.get("viewCount", 0) or 0),
                    "videos": int(stats.get("videoCount", 0) or 0),
                    "likes": int(stats.get("likeCount", 0)) if "likeCount" in stats else None, # chưa lấy được
                    "comments": int(stats.get("commentCount", 0)) if "commentCount" in stats else None, # chưa lấy được
                    "relatedPlaylists": details.get("relatedPlaylists", {}), # chưa cập nhật vào json
                }

                print(
                    f"📊 {data['name']:<40} | 👥 Subs: {data['subscribers']:<10} | 👀 Views: {data['views']:<10} | 🎞 Videos: {data['videos']:<10} | 🗺️ Country: {'country':<10}"
                )

                # ✅ Lưu vào DB
                save_channel_stats(
                    channel_id=data["channel_id"],
                    name=data["name"],
                    subs=data["subscribers"],
                    views=data["views"],
                    videos=data["videos"],
                    likes=data["likes"],
                    comments=data["comments"],
                    category=data["group"],
                    country=data["country"],
                )

                all_data.append(data)

    return all_data


if __name__ == "__main__":
    data = fetch_channel_infos()
    print("✅ Fetched data:")
    print(f"→ Tổng số kênh: {len(data)}")

    # --- Gán category cho từng channel ---
    conn = sqlite3.connect("youtube_stats.db")
    cursor = conn.cursor()
    for category, channels in DEFAULT_CHANNEL_GROUPS.items():
        for ch_id in channels:
            cursor.execute(
                "UPDATE Channel_Stats SET category = ? WHERE channel_id = ?",
                (category.replace("_channels", "").upper(), ch_id)
            )
    conn.commit()
    conn.close()
    print("✅ Category assigned successfully to each channel.")

    # --- Chỉ lấy 4 thông tin cần thiết ---
    simple_data = [
        {
            "name": ch["name"],
            "customUrl": ch.get("customUrl", ""),
            "description": ch.get("description", ""),
            "thumbnails": ch.get("thumbnails", ""),
        }
        for ch in data
    ]

    # --- Ghi ra file JSON ---
    output_path = "channels_info.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(simple_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu danh sách kênh (name, description, thumbnail) vào {output_path}")
