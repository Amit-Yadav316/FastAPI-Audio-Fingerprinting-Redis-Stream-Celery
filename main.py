from fastapi import FastAPI
from database.database import engine, Base
from app.routers.upload import router as upload_router
from app.routers.checkmatches import router as check_router
from celery_worker.updates import router as status_router
from database.db_init import ensure_database_exists
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4


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
app.include_router(check_router, tags=["Check Matches"])
app.include_router(status_router,tags=["WebSocket"])


@app.get("/new-task-id")
async def new_task():
    return {"task_id": str(uuid4())}

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to Real-Time Audio Matcher"}