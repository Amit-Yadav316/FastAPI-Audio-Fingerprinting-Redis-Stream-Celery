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

redis_stream = Redis.from_url(settings.redis_pubsub_url, decode_responses=True)

@router.websocket("/ws/subscribe/{task_id}")
async def subscribe_to_task(task_id: str, ws: WebSocket, timeout: float = 150.0):
    await ws.accept()
    print(redis_stream.connection_pool.connection_kwargs)
    stream_key = f"match_result_stream:{task_id}"
    print(f"Subscribing to stream: {stream_key}")
    start_time = time.monotonic()
    stream_id = "0-0" 

    try:
        while True:
            elapsed = time.monotonic() - start_time
            if elapsed > timeout:
                if ws.application_state == WebSocketState.CONNECTED:
                    await ws.send_json({
                        "status": "error",
                        "message": "Timeout: No result within 90 seconds"
                    })
                break

            result = await redis_stream.xread({stream_key: stream_id}, block=1000, count=1)

            if result:
                _, entries = result[0]
                for stream_id, entry in entries:
                    data = json.loads(entry["data"])
                    if ws.application_state == WebSocketState.CONNECTED:
                        await ws.send_json(data)
                    await redis_stream.xdel(stream_key, stream_id)    
                    return

            await asyncio.sleep(0.2)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        if ws.application_state == WebSocketState.CONNECTED:
            await ws.send_json({"status": "error", "message": str(e)})
    finally:
        if ws.application_state == WebSocketState.CONNECTED:
            await ws.close()