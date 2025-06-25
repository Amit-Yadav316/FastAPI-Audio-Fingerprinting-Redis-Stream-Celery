from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

from app.config.config import settings


DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

SYNC_DATABASE_URL = settings.database_url 

sync_engine = create_engine(SYNC_DATABASE_URL, echo=False)

SessionLocal = sync_sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()
