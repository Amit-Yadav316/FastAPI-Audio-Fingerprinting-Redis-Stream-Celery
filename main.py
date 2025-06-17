from fastapi import FastAPI
import asyncio
from database.database import engine, Base
from app.routers.upload import router as upload_router
from app.routers.checkmatches import router as websocket_router
from database.db_init import ensure_database_exists


app = FastAPI() 

@app.on_event("startup")
async def startup_event():
    ensure_database_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



app.include_router(upload_router, tags=["Upload"])
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Real-Time Audio Matcher"}