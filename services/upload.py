from fastapi import UploadFile, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.models import Song
from models.models import Fingerprint
from services.metadata import get_metadata
from services.fingerprints_generate import generate_fingerprint
import uuid
import os
from pathlib import Path
import aiofiles


async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: AsyncSession
):
    if not file.filename.lower().endswith((".wav", ".mp3", ".flac")):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_id = f"{uuid.uuid4()}_{file.filename}"
    file_path = Path(os.path.UPLOADS_DIR) / file_id

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024): 
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")


    result = await db.execute(select(Song).where(Song.title == file.filename))
    if result.scalars().first():
        return {"message": "File already exists"}


    try:
        fingerprints = generate_fingerprint(str(file_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fingerprinting failed: {str(e)}")

    new_song = Song(title=file.filename)
    db.add(new_song)
    await db.commit()
    await db.refresh(new_song)


    db.add_all([
        Fingerprint(hash=h, offset=offset, song_id=new_song.id)
        for h, offset in fingerprints
    ])
    await db.commit()

    background_tasks.add_task(get_metadata, new_song.id, file.filename)

    return {
        "message": "File uploaded and fingerprinted",
        "song_id": new_song.id,
        "title": new_song.title
    }


async def delete_upload(name: str, db: AsyncSession):
    pattern = f"%{name}%"
    result = await db.execute(select(Song.id).where(Song.title.ilike(pattern)))
    song_ids = [song_id for (song_id,) in result.fetchall()]

    if not song_ids:
        raise HTTPException(status_code=404, detail="No matching songs found.")

    await db.execute(delete(Fingerprint).where(Fingerprint.song_id.in_(song_ids)))
    await db.execute(delete(Song).where(Song.id.in_(song_ids)))
    await db.commit()

    return {"message": f"Deleted {len(song_ids)} song(s) and their fingerprints."}
