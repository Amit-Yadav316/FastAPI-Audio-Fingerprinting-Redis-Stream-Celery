from fastapi import APIRouter,WebSocket,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.checkmatches import process_and_match_audio

router = APIRouter()




@router.websocket("/ws/match")
async def match_songs(ws: WebSocket, db: AsyncSession = Depends(get_db)):
    await ws.accept()
    try:
        await process_and_match_audio(ws, db)
    except Exception as e:
        await ws.close(code=1001)
        print("WebSocket error:", e)
