from fastapi import APIRouter,BackgroundTasks,UploadFile, File,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from services.upload import upload_file,delete_upload
import os

router = APIRouter()


@router.post("/upload")
async def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await upload_file(background_tasks,file,db)

@router.delete("/upload/delete/{name}")
async def delete(name: str, db: AsyncSession = Depends(get_db)):
    return await delete_upload(name,db)