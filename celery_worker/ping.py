import asyncio
from starlette.websockets import WebSocket, WebSocketState

async def ping_ws(ws: WebSocket):
    try:
        while ws.application_state == WebSocketState.CONNECTED:
            await asyncio.sleep(10)  
            await ws.send_json({"type": "ping"})  
    except Exception:
        pass