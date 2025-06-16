from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.database import engine, Base
from .upload import router as upload_router
from .checkmatches import router as websocket_router
from .db_init import ensure_database_exists


app = FastAPI() 

@app.on_event("startup")
async def startup_event():
    ensure_database_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



app.include_router(upload_router, prefix="/api", tags=["Upload"])
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Real-Time Audio Matcher"}