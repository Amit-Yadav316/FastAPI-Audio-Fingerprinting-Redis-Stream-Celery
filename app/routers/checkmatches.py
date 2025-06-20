from fastapi import APIRouter,WebSocket
from database.database import get_db
from services.checkmatches import process_and_match_audio

router = APIRouter()




@router.websocket("/ws/match")
async def match_songs(ws: WebSocket):
    await ws.accept()
    try:
        async with get_db() as db:
            await process_and_match_audio(ws, db)
    except Exception as e:
        await ws.send_json({"error": "Internal server error. Please try again later."})
        await ws.close(code=1001)
