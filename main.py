from fastapi import FastAPI
import asyncio
from database.database import engine, Base
from app.routers.upload import router as upload_router
from app.routers.checkmatches import router as websocket_router
from database.db_init import ensure_database_exists


app = FastAPI() 

@app.on_event("startup")
async def startup_event():
    await ensure_database_exists()
    
app.include_router(upload_router, tags=["Upload"])
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Real-Time Audio Matcher"}