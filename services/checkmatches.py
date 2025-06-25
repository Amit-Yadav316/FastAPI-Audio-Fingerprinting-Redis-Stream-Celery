from pathlib import Path
import aiofiles
import uuid
from fastapi import HTTPException
from celery_worker.tasks.matching import match_fingerprint_task
from app.config.config import settings
from fastapi import UploadFile
from fastapi import BackgroundTasks
async def match_songs(file:UploadFile , task_id :str):
    Path("temp_audio").mkdir(exist_ok=True, parents=True)
    filename = Path("temp_audio") / f"{uuid.uuid4().hex}.webm"
    try:
        async with aiofiles.open(filename, "wb") as f:
            while chunk := await file.read(1024 * 2): 
                await f.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    if not filename.exists() or filename.stat().st_size == 0:
        raise HTTPException(status_code=500, detail="Audio file not written or empty.")
    print(f"[INFO] Audio saved to: {filename}")
 
    def dispatch():
        match_fingerprint_task.delay(str(filename), task_id)

    background_tasks.add_task(dispatch)
    print(f"[INFO] Task started with ID: {task_id}")
    
    return {"task_id": task_id, "filename": str(filename)}