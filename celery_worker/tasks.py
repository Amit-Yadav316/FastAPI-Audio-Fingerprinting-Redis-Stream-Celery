import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from celery_worker import celery_app
from services.fingerprints_generate import generate_fingerprint
from models.models import Fingerprint
from database.database import async_session_maker
import logging
import asyncio

@celery_app.task(bind=True, name="generate_fingerprint_task", max_retries=3, default_retry_delay=10)
def generate_fingerprint_task(self, song_id: int, file_path: str):
    try:
        fingerprints = generate_fingerprint(file_path)
        if not fingerprints:
            logging.warning(f"[Fingerprinting Warning] No fingerprints generated for Song ID {song_id}")
            return
        asyncio.run(save_fingerprints(song_id, fingerprints))

        logging.info(f"[Fingerprinting Success] Song ID {song_id} with {len(fingerprints)} fingerprints.")

    except Exception as exc:
        logging.error(f"[Fingerprinting Error] Song ID {song_id}: {str(exc)}")
        raise self.retry(exc=exc)


async def save_fingerprints(song_id: int, fingerprints: list[tuple[str, float]]):
    async with async_session_maker() as session:
        session.add_all([
            Fingerprint(hash=h, offset=offset, song_id=song_id)
            for h, offset in fingerprints
        ])
        await session.commit()

