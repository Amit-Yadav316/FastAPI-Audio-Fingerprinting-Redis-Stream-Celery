from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from app.database import get_db
from app.models import Song, Fingerprint
from app.metadata import get_metadata
from app.fingerprints_generate import generate_fingerprint
import os
import uuid
import aiofiles

router = APIRouter()

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith((".wav", ".mp3", ".flac")):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOADS_DIR, file_id)

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving error: {str(e)}")

    try:
        fingerprint = generate_fingerprint(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fingerprint error: {str(e)}")

    result = await db.execute(select(Song).where(Song.title == file.filename))
    existing_song = result.scalars().first()
    if existing_song:
        return {"message": "File already exists", "song_id": existing_song.id}

    new_song = Song(title=file.filename)
    db.add(new_song)
    await db.commit()
    await db.refresh(new_song)

    for h, offset in fingerprint:
        db.add(Fingerprint(hash=h, offset=offset, song_id=new_song.id))
    await db.commit()

    background_tasks.add_task(get_metadata, new_song.id, file.filename)

    return {
        "message": "File uploaded successfully",
        "song_id": new_song.id,
        "title": new_song.title,
    }

@router.delete("/upload/delete/{name}", status_code=200)
async def delete_upload(name: str, db: AsyncSession = Depends(get_db)):
    pattern = f"%{name}%"

    result = await db.execute(select(Song.id).where(Song.title.ilike(pattern)))
    song_ids = [id  for (id,) in result]

    if not song_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No songs matched the given name pattern."
        )

    await db.execute(delete(Fingerprint).where(Fingerprint.song_id.in_(song_ids)))
    await db.execute(delete(Song).where(Song.id.in_(song_ids)))
    await db.commit()

    return {"message": f"Deleted {len(song_ids)} song(s) and associated fingerprint(s)."}