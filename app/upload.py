from fastapi import APIRouter, UploadFile, File,HTTPException,BackgroundTasks,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Song, Fingerprint
from app.config import settings
import os
import uuid
import shutil

router = APIRouter()

UPLOADS_DIR = "uploads"
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

router.post("/upload")    
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    if not file.filename.endswith(".wav", ".mp3", ".flac"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOADS_DIR, file_id)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        fingerprint = fingerprint_create(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating fingerprint: {str(e)}") 
    existing_song = db.query(Song).filter(Song.title == file.filename).first()
    if existing_song:
        return {
            "message": "File already exists",
            "song_id": existing_song.id,
        }
    new_song = Song(
        title=file.filename, 
    )
    fingerprint_db = Fingerprint(
        hash=fingerprint,
        offset=0,
        song_id=new_song.id
    )
    db.add(new_song)
    db.add(fingerprint_db)
    db.commit()
    db.refresh(new_song)
    db.refresh(fingerprint)
    background_tasks.add_task(get_metadata, new_song.id, file.filename)
    return {
        "message": "File uploaded successfully",
        "song_id": new_song.id,
        "title": new_song.title,
    }