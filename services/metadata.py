import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_session_maker as async_session  
from models.models import Song
from .spotifyservice import search_spotify_metadata
from .youtubeservice import get_yt_metadata

logger = logging.getLogger(__name__)

async def get_metadata(song_id: int, raw_title: str) -> None:
    async with async_session() as db:  
        try:
            spotify_task = asyncio.create_task(search_spotify_metadata(raw_title))
            youtube_task = asyncio.create_task(get_yt_metadata(raw_title))

            spotify_metadata, youtube_metadata = await asyncio.gather(
                spotify_task, youtube_task
            )

            if not spotify_metadata or not youtube_metadata:
                logger.warning(f"[Metadata Missing] Spotify or YouTube metadata not found for '{raw_title}'")
                return 

            song = await db.get(Song, song_id)
            if not song:
                logger.error(f"[DB Error] Song with ID {song_id} not found in DB")
                return

            song.spotify_data = spotify_metadata
            song.youtube_data = youtube_metadata
            await db.commit()
            await db.refresh(song)

            logger.info(f"[Metadata Saved] Metadata successfully saved for song ID {song_id}")

        except Exception as e:
            await db.rollback()
            logger.exception(f"[Metadata Fetch Failed] For song ID {song_id}, title: '{raw_title}'. Error: {str(e)}")


