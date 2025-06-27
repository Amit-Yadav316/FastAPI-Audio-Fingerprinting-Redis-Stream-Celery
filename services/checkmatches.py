from pathlib import Path
import aiofiles
import uuid
from fastapi import HTTPException
from celery_worker.tasks.matching import match_fingerprint_task
from app.config.config import settings
from fastapi import UploadFile

UPLOAD_DIR = Path("temp_audio")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

async def match_songs(file: UploadFile, task_id: str):
    filename = UPLOAD_DIR / f"{uuid.uuid4().hex}.webm"

    try:
        async with aiofiles.open(filename, "wb") as f:
            while chunk := await file.read(1024 * 50): 
                await f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

    if not filename.exists() or filename.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="Empty or failed upload.")

    match_fingerprint_task.delay(str(filename), task_id)
    return {"task_id": task_id, "filename": str(filename)}
