from flask import Flask, render_template
import requests
import random
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def get_random_skill_video():
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"

    # Step 1: Search for video IDs with embeddable and short duration filters
    search_params = {
        "part": "snippet",
        "q": "5 minute skill",
        "type": "video",
        "videoDuration": "short",
        "videoEmbeddable": "true",
        "maxResults": 25,
        "key": YOUTUBE_API_KEY
    }

    search_res = requests.get(search_url, params=search_params).json()
    video_ids = [item["id"]["videoId"] for item in search_res.get("items", [])]

    if not video_ids:
        return None

    # Step 2: Get full video details and filter further
    detail_params = {
        "part": "snippet,contentDetails,status",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    video_res = requests.get(video_url, params=detail_params).json()
    valid_videos = []

    for video in video_res.get("items", []):
        status = video.get("status", {})
        if status.get("embeddable") and status.get("privacyStatus") == "public":
            valid_videos.append({
                "video_id": video["id"],
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"]
            })

    if not valid_videos:
        return None

    return random.choice(valid_videos)

@app.route('/')
def index():
    skill = get_random_skill_video()
    if not skill:
        skill = {
            "title": "No Skill Found",
            "description": "Could not load a suitable video.",
            "video_id": None
        }
    return render_template("index.html", skill=skill)

if __name__ == '__main__':
    app.run(debug=True)
