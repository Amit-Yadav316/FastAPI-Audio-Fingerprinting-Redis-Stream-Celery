import os, time, numpy as np, tempfile, aiofiles, soundfile as sf, librosa
from fastapi.concurrency import run_in_threadpool
from collections import defaultdict, Counter
from models.models import Song, Fingerprint
from services.fingerprints_generate import generate_fingerprint
from sqlalchemy.ext.asyncio import AsyncSession

async def process_and_match_audio(ws, db: AsyncSession):
    buffer = bytearray()
    start_time = time.time()
    sample_rate = 22050
    recording_duration = 5.0

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

            result = await db.execute(Fingerprint.__table__.select().where(Fingerprint.hash.in_(hash_keys)))
            matches = result.fetchall()

            match_scores = defaultdict(list)
            for match in matches:
                hash_val, song_id, db_offset = match
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
                result = await db.execute(Song.__table__.select().where(Song.id == song_id))
                song = result.fetchone()
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

