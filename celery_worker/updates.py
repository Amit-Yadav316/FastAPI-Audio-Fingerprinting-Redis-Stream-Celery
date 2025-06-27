from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from starlette.websockets import WebSocketState
from celery.result import AsyncResult
from celery_worker import celery_app
import asyncio
import logging
from redis.asyncio import Redis
import json
from app.config.config import settings
import time 

router = APIRouter()

logger = logging.getLogger(__name__)

@router.websocket("/ws/status/{task_id}")
async def task_status_ws(task_id: str, websocket: WebSocket):

    await websocket.accept()
    
    try:
        if not task_id:
            await websocket.send_json({"error": "Missing task_id"})
            await websocket.close()
            return

        while True:
            result = AsyncResult(task_id, app=celery_app)
            state = result.state

            response = {"task_id": task_id, "status": state}

            if state == "FAILURE":
                response["error"] = str(result.result)
                await websocket.send_json(response)
                await websocket.close()
                break

            if state == "SUCCESS":
                response["result"] = result.result
                await websocket.send_json(response)
                await websocket.close()
                break

            await websocket.send_json(response)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logging.error(f"WebSocket disconnected for task: {task_id}")

redis_stream = Redis.from_url(settings.redis_stream_url, decode_responses=True)

@router.websocket("/ws/subscribe/{task_id}")
async def subscribe_to_task(task_id: str, ws: WebSocket, timeout: float = 150.0):
    await ws.accept()
    stream_key = f"match_result_stream:{task_id}"
    stream_id = "0-0"
    start_time = time.monotonic()

    try:
        while True:
            if (time.monotonic() - start_time) > timeout:
                await ws.send_json({
                    "status": "error",
                    "message": f"Timeout: No result in {timeout} seconds"
                })
                break

            result = await redis_stream.xread({stream_key: stream_id}, block=5000, count=1)

            if result:
                _, entries = result[0]
                for stream_id, entry in entries:
                    data = json.loads(entry["data"])
                    await ws.send_json(data)
                    await redis_stream.xdel(stream_key, stream_id)
                    return
    except WebSocketDisconnect:
        print(f"[WS] Disconnected: {task_id}")
    except Exception as e:
        await ws.send_json({"status": "error", "message": str(e)})
    finally:
        await ws.close()