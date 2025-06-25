from fastapi import APIRouter, UploadFile, File
from services.checkmatches import match_songs
from fastapi import Form

router = APIRouter()

@router.post("/match")
async def matched(file: UploadFile = File(...),task_id: str = Form(...)):
   return await match_songs(file,task_id)


    

