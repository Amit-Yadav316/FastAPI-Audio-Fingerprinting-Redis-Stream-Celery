from fastapi import WebSocket, WebSocketDisconnect,APIRouter
from celery.result import AsyncResult
from celery_worker import celery_app
import asyncio
import logging

router = APIRouter()

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
            await asyncio.sleep(1.5)

    except WebSocketDisconnect:
        logging.error(f"WebSocket disconnected for task: {task_id}")
