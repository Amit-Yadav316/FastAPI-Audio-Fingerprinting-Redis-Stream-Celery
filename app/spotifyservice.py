import requests
import json
from app.config import settings
from redis_cache import get_cached_metadata, cache_metadata
from fastapi import HTTPException, status , BackgroundTasks

def get_spotify_token():
    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(settings.spotify_client_id, settings.spotify_client_secret)
    )
    return auth_response.json().get("access_token")

def search_track_metadata(query: str, background_tasks: BackgroundTasks):
    cache_key = f"spotify:{query.lower()}"
    cached = get_cached_metadata(cache_key)
    if cached:
        return cached

    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': 1}
    resp = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    if resp.status_code != 200:
        return None

    data = resp.json().get("tracks", {}).get("items", [])
    if not data:
        return None

    track = data[0]
    spotify_metadata = {
        "title": track["name"],
        "artist": track["artists"][0]["name"],
        "album": track["album"]["name"],
        "spotify_id": track["id"],
        "external_url": track["external_urls"]["spotify"]
    }
    background_tasks.add(cache_metadata, cache_key, spotify_metadata)
    return spotify_metadata