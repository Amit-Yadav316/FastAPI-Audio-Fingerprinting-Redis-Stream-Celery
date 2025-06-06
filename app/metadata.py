import json
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Song
from spotifyservice import search_track_metadata
from youtubeservice import get_yt_metadata
from redis_cache import cache_metadata


def get_metadata(song_id: int, raw_title: str):
    db: Session = SessionLocal()
    try:
        spotify_metadata = search_track_metadata(raw_title)
        if not spotify_metadata:
            return None

        youtube_metadata = get_yt_metadata(raw_title)
        if not youtube_metadata:
            return None
        song = db.query(Song).filter(Song.id == song_id).first()
        if not song:
            return None
        song.spotify_data = spotify_metadata
        song.youtube_data = youtube_metadata

        db.commit()

    finally:
        db.close()