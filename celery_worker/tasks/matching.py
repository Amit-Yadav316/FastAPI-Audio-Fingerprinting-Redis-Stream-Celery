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

redis_stream = redis.Redis.from_url(settings.redis_pubsub_url)

@celery_app.task(bind=True, name="match_fingerprint_task", max_retries=2)
def match_fingerprint_task(self, audio_path: str, task_id: str):
    print(redis_stream.connection_pool.connection_kwargs)
    try:
        audio_path = Path(audio_path)
        audio = AudioSegment.from_file(audio_path, format="webm")
        audio = audio.set_frame_rate(22050).set_channels(1)
        mp3_path = Path(audio_path).with_suffix(".mp3")
        audio.export(mp3_path, format="mp3")
        print("Audio converted to MP3")

    except Exception as e:
        error_data = json.dumps({
            "status": "error",
            "message": f"Audio conversion error: {e}"
        })
        redis_stream.xadd(f"match_result_stream:{task_id}", {"data": error_data})
        return

    db = SessionLocal()

    try:
        if not audio_path.exists():
            raise FileNotFoundError(f"File does not exist: {audio_path}")

        fingerprints = generate_fingerprint(audio_path)
        if not fingerprints:
            redis_stream.xadd(f"match_result_stream:{task_id}", {
                "data": json.dumps({
                    "status": "error",
                    "message": "No fingerprints generated"
                })
            })
            return

        hash_offset_map = {fp[0]: fp[1] for fp in fingerprints}
        hash_keys = list(hash_offset_map.keys())

        result = db.execute(
            select(Fingerprint.hash, Fingerprint.song_id, Fingerprint.offset)
            .where(Fingerprint.hash.in_(hash_keys))
        )
        matches = result.fetchall()

        match_scores = defaultdict(list)
        for hash_val, song_id, db_offset in matches:
            delta = db_offset - hash_offset_map[hash_val]
            match_scores[song_id].append(round(delta, 2))

        song_confidence = []
        for song_id, deltas in match_scores.items():
            delta_counts = Counter(deltas)
            most_common_delta, count = delta_counts.most_common(1)[0]
            song_confidence.append((song_id, count, most_common_delta))

        top_matches = sorted(song_confidence, key=lambda x: x[1], reverse=True)[:5]
        song_ids = [song_id for song_id, _, _ in top_matches]

        song_result = db.execute(select(Song).where(Song.id.in_(song_ids)))
        songs = {song.id: song for song in song_result.scalars().all()}

        response = []
        for song_id, confidence, best_offset in top_matches:
            song = songs.get(song_id)
            if song and song.youtube_data:
                yt_url = song.youtube_data.get("video_url", "")
                thumbnail = song.youtube_data.get("thumbnail_url", "")
                response.append({
                    "song_id": song.id,
                    "title": song.title,
                    "yt_url": yt_url,
                    "confidence": confidence,
                    "best_offset": best_offset,
                    "thumbnail": thumbnail
                })

        final_data = json.dumps({
            "status": "success",
            "matches": response
        })

        redis_stream.xadd(f"match_result_stream:{task_id}", {"data": final_data})
        redis_stream.expire(f"match_result_stream:{task_id}", 300)
        print(f"Streamed: match_result_stream:{task_id}")

    except Exception as e:
        redis_stream.xadd(f"match_result_stream:{task_id}", {
            "data": json.dumps({
                "status": "error",
                "message": str(e)
            })
        })
        raise self.retry(exc=e)

    finally:
        db.close()
  