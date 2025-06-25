import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from celery_worker import celery_app
from services.fingerprints_generate import generate_fingerprint
from models.models import Fingerprint
from database.database import SessionLocal
from sqlalchemy.orm import Session
from itertools import islice


@celery_app.task(bind=True, name="generate_fingerprint_task", max_retries=3, default_retry_delay=10)
def generate_fingerprint_task(self, song_id: int, file_path: str):
    try:
        fingerprints = generate_fingerprint(file_path)
        if not fingerprints:
            logging.warning(f"[Fingerprinting Warning] No fingerprints generated for Song ID {song_id}")
            return

        save_fingerprints_sync(song_id, fingerprints)

        logging.info(f"[Fingerprinting Success] Song ID {song_id} with {len(fingerprints)} fingerprints.")

    except Exception as exc:
        logging.error(f"[Fingerprinting Error] Song ID {song_id}: {str(exc)}")
        raise self.retry(exc=exc)

def save_fingerprints_sync(song_id: int, fingerprints: list[tuple[str, float]]):
    db: Session = SessionLocal()
    batch_size = 1000

    try:
        it = iter(fingerprints)
        total_inserted = 0

        while True:
            batch = list(islice(it, batch_size))
            if not batch:
                break

            objs = [
                Fingerprint(hash=h, offset=float(offset), song_id=song_id)
                for h, offset in batch
            ]

            db.bulk_save_objects(objs)
            db.commit()
            total_inserted += len(objs)

        logging.info(f"[Batch Insert] Successfully inserted {total_inserted} fingerprints for song {song_id}")

    except Exception as e:
        db.rollback()
        logging.error(f"[DB Error] Bulk insert failed for song {song_id}: {e}")
        raise

    finally:
        db.close()

