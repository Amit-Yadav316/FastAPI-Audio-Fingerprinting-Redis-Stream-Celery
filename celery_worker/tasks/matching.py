import json
from pathlib import Path
from pydub import AudioSegment
from collections import defaultdict, Counter
from sqlalchemy import select
from database.database import SessionLocal
from models.models import Song, Fingerprint
from services.fingerprints_generate import generate_fingerprint
from celery_worker import celery_app
import redis
from app.config.config import settings
import os

redis_stream = redis.Redis.from_url(settings.redis_stream_url)

@celery_app.task(bind=True, name="match_fingerprint_task", max_retries=2)
def match_fingerprint_task(self, audio_path: str, task_id: str):
    try:
        audio = AudioSegment.from_file(audio_path, format="webm")
        audio = audio.set_frame_rate(22050).set_channels(1)
        mp3_path = Path(audio_path).with_suffix(".mp3")
        audio.export(mp3_path, format="mp3")
    except Exception as e:
        redis_stream.xadd(f"match_result_stream:{task_id}", {"data": json.dumps({
            "status": "error", "message": f"Conversion failed: {e}"
        })})
        return

    db = SessionLocal()

    try:
        fingerprints = generate_fingerprint(audio_path)
        if not fingerprints:
            redis_stream.xadd(f"match_result_stream:{task_id}", {
                "data": json.dumps({"status": "error", "message": "No fingerprints"})
            })
            return

        hash_map = {fp[0]: fp[1] for fp in fingerprints}
        result = db.execute(select(Fingerprint.hash, Fingerprint.song_id, Fingerprint.offset)
                            .where(Fingerprint.hash.in_(list(hash_map.keys()))))
        matches = result.fetchall()

        score_map = defaultdict(list)
        for hash_val, song_id, db_offset in matches:
            delta = db_offset - hash_map[hash_val]
            score_map[song_id].append(round(delta, 2))

        confidence = []
        for song_id, deltas in score_map.items():
            most_common, count = Counter(deltas).most_common(1)[0]
            confidence.append((song_id, count, most_common))

        top = sorted(confidence, key=lambda x: x[1], reverse=True)[:5]
        ids = [x[0] for x in top]

        songs = {s.id: s for s in db.execute(select(Song).where(Song.id.in_(ids))).scalars().all()}

        response = []
        for song_id, score, offset in top:
            s = songs.get(song_id)
            if s and s.youtube_data:
                response.append({
                    "song_id": s.id,
                    "title": s.title,
                    "yt_url": s.youtube_data.get("video_url", ""),
                    "thumbnail": s.youtube_data.get("thumbnail_url", ""),
                    "confidence": score,
                    "best_offset": offset
                })

        redis_stream.xadd(f"match_result_stream:{task_id}", {
            "data": json.dumps({"status": "success", "matches": response})
        }, maxlen=1)
        redis_stream.expire(f"match_result_stream:{task_id}", 300)
    except Exception as e:
        redis_stream.xadd(f"match_result_stream:{task_id}", {
            "data": json.dumps({"status": "error", "message": str(e)})
        })
        raise self.retry(exc=e)
    
    finally:
    db.close()
    for path in [audio_path, mp3_path]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error deleting file {path}: {e}")