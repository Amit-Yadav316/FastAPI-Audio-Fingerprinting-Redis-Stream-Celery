import os
import uuid
import time
import numpy as np
import tempfile
import aiofiles
import soundfile as sf
import librosa
from fastapi import APIRouter, WebSocket, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict, Counter
from app.database import get_db
from app.models import Song, Fingerprint
from app.fingerprints_generate import generate_fingerprint
from app.redis_cache import get_cached_metadata

router = APIRouter()

@router.websocket("/ws/match")
async def match_songs(ws: WebSocket, db: AsyncSession = Depends(get_db)):
    await ws.accept()

    buffer = bytearray()
    start_time = time.time()
    sample_rate = 22050
    recording_duration = 5.0

    try:
        while True:
            data = await ws.receive_bytes()
            buffer.extend(data)

            if time.time() - start_time >= recording_duration:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    temp_filename = tmp_file.name

                async with aiofiles.open(temp_filename, 'wb') as f:
                    await f.write(buffer)

                y, orig_sr = await run_in_threadpool(sf.read, temp_filename)
                os.remove(temp_filename)

                if y.ndim > 1:
                    y = np.mean(y, axis=1)
                if orig_sr != sample_rate:
                    y = await run_in_threadpool(librosa.resample, y, orig_sr, sample_rate)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as converted_file:
                    temp_path = converted_file.name
                await run_in_threadpool(sf.write, temp_path, y, sample_rate)

                fingerprints = await run_in_threadpool(generate_fingerprint, temp_path)
                os.remove(temp_path)

                
                hash_offset_map = {fp[0]: fp[1] for fp in fingerprints}
                hash_keys = list(hash_offset_map.keys())

                matches = (
                    db.query(Fingerprint.hash, Fingerprint.song_id, Fingerprint.offset)
                    .filter(Fingerprint.hash.in_(hash_keys))
                    .all()
                )

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

                response = []
                for song_id, confidence, best_offset in top_matches:
                    song = db.query(Song).filter(Song.id == song_id).first()
                    if song and song.youtube_data:
                        yt_data = song.youtube_data
                        response.append({
                            "song_id": song.id,
                            "title": song.title,
                            "yt_url": yt_data.get("video_url"),
                            "confidence": confidence,
                            "best_offset": best_offset,
                        })

                await ws.send_json({"matches": response})

                buffer.clear()
                start_time = time.time()

    except Exception as e:
        await ws.close(code=1001)
        print("WebSocket error:", e)
