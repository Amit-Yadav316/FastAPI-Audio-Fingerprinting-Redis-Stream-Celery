import httpx
from fastapi import HTTPException, status
from chache.redis_cache import get_cached_metadata, cache_metadata
from app.config.config import settings


async def get_spotify_token() -> str:
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
            raise ValueError("No access token in response")
        return token

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to connect to Spotify: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


async def search_spotify_metadata(query: str) -> dict:
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty."
        )

    cache_key = f"spotify:{query.lower()}"
    cached = await get_cached_metadata(cache_key)
    if cached:
        return cached

    token = await get_spotify_token()
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
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Spotify search failed: {str(e)}"
        )

    tracks = resp.json().get("tracks", {}).get("items", [])
    if not tracks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No track found for the given query."
        )

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

