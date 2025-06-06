import requests
import json
from app.config import settings
from redis.cache import get_cached_metadata,cache_metadata
from fastapi import HTTPException, status, BackgroundTasks

def get_yt_metadata(query:str, background_tasks: BackgroundTasks):
    cache_key= f"youtube:{query.lower()}"
    cached = get_cached_metadata(cache_key)
    if cached  :
        return cached
    url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "key": settings.YOUTUBE_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None

    items = response.json().get("items", [])
    if not items:
        return None

    video = items[0]
    yt_metadata = {
        "title": video["snippet"]["title"],
        "video_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
        "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"]
    }

    background_tasks.add(cache_metadata, cache_key, yt_metadata)

    return yt_metadata
