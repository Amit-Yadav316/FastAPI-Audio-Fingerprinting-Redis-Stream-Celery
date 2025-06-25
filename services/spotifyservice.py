import httpx
from fastapi import status
from chache.redis_cache import get_cached_metadata, cache_metadata
from app.config.config import settings
import logging


logger = logging.getLogger(__name__)

async def get_spotify_token() -> str | None:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            auth_response = await client.post(
                'https://accounts.spotify.com/api/token',
                data={'grant_type': 'client_credentials'},
                auth=(settings.spotify_client_id, settings.spotify_client_secret)
            )
        auth_response.raise_for_status()

        token = auth_response.json().get("access_token")
        if not token:
            logger.error("[Spotify Token] No access token in response")
            return None
        return token

    except httpx.RequestError as e:
        logger.error(f"[Spotify Token Error] Network issue: {e}")
        return None
    except Exception as e:
        logger.exception(f"[Spotify Token Error] Unexpected: {e}")
        return None


async def search_spotify_metadata(query: str) -> dict | None:
    if not query:
        logger.warning("[Spotify] Empty query received.")
        return None

    cache_key = f"spotify:{query.lower()}"
    cached = await get_cached_metadata(cache_key)
    if cached:
        return cached

    token = await get_spotify_token()
    if not token:
        logger.error("[Spotify] Failed to retrieve token")
        return None

    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': 1}

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params=params
            )
        resp.raise_for_status()
    except httpx.RequestError as e:
        logger.error(f"[Spotify Request Error] {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"[Spotify API Error] {e.response.status_code}: {e.response.text}")
        return None

    tracks = resp.json().get("tracks", {}).get("items", [])
    if not tracks:
        logger.warning(f"[Spotify] No track found for query: {query}")
        return None

    track = tracks[0]
    spotify_metadata = {
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "album": track["album"]["name"],
        "spotify_id": track["id"],
        "external_url": track["external_urls"]["spotify"]
    }

    await cache_metadata(cache_key, spotify_metadata)
    return spotify_metadata

