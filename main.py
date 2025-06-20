from fastapi import FastAPI
import asyncio
from database.database import engine, Base
from app.routers.upload import router as upload_router
from app.routers.checkmatches import router as websocket_router
from celery_worker.updates import router as status_router
from database.db_init import ensure_database_exists
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              
    allow_credentials=True,
    allow_methods=["*"],               
    allow_headers=["*"],               
)

@app.on_event("startup")
async def startup_event():
    await ensure_database_exists()
    
app.include_router(upload_router, tags=["Upload"])
app.include_router(websocket_router, tags=["WebSocket"])
app.include_router(status_router,tags=["WebSocket"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Real-Time Audio Matcher"}