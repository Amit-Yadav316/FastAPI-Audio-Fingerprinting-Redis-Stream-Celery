import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal as async_session  
from app.models import Song
from .spotifyservice import search_spotify_metadata
from .youtubeservice import get_yt_metadata

async def get_metadata(song_id: int, raw_title: str) -> None:
    async with async_session() as db:  
        try:
            spotify_task = asyncio.create_task(search_spotify_metadata(raw_title))
            youtube_task = asyncio.create_task(get_yt_metadata(raw_title))

            spotify_metadata, youtube_metadata = await asyncio.gather(
                spotify_task, youtube_task
            )

            if not spotify_metadata or not youtube_metadata:
                raise Exception("Metadata fetch failed for Spotify or YouTube")

            song = await db.get(Song, song_id)
            if not song:
                raise Exception(f"Song with ID {song_id} not found")

            song.spotify_data = spotify_metadata
            song.youtube_data = youtube_metadata
            await db.commit()
            await db.refresh(song)

        except Exception as e:
            await db.rollback()
            print("Metadata fetch failed:", str(e))

