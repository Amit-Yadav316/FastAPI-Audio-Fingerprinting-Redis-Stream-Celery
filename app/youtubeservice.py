import httpx
from fastapi import HTTPException, status
from app.config import settings
from .redis_cache import get_cached_metadata, cache_metadata


async def get_yt_metadata(query: str) -> dict:
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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch YouTube metadata: {str(e)}"
        )

    items = response.json().get("items", [])
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No video found for the given query"
        )

    video = items[0]
    yt_metadata = {
        "title": video["snippet"]["title"],
        "video_url": f"https://www.youtube.com/watch?v={video['id']['videoId']}",
        "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"]
    }

    await cache_metadata(cache_key, yt_metadata)
    return yt_metadata


