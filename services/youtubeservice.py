import httpx
import logging
from app.config.config import settings
from chache.redis_cache import get_cached_metadata, cache_metadata

logger = logging.getLogger(__name__)

async def get_yt_metadata(query: str) -> dict | None:
    cache_key = f"youtube:{query.lower()}"
    cached = await get_cached_metadata(cache_key)
    if cached:
        return cached

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "key": settings.youtube_api_key,
        "maxResults": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
    except httpx.RequestError as e:
        logger.error(f"[YouTube Request Error] {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"[YouTube API Error] {e.response.status_code} - {e.response.text}")
        return None

    items = response.json().get("items", [])
    if not items:
        logger.warning(f"[YouTube] No results found for query: {query}")
        return None

    video = items[0]
    yt_metadata = {
        "title": video["snippet"]["title"],
        "video_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
        "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"]
    }

    await cache_metadata(cache_key, yt_metadata)
    return yt_metadata


