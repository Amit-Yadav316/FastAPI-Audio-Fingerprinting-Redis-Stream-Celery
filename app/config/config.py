from pydantic import  Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")
    youtube_api_key: str = Field(..., env="YOUTUBE_API_KEY")
    redis_cache_url: str = Field(...,env="REDIS_CACHE_URL")
    redis_celery_broker_url: str = Field(...,env="REDIS_CELERY_BROKER_URL")
    redis_celery_backend_url: str = Field(...,env="REDIS_CELERY_BACKEND_URL")
    redis_pubsub_url: str = Field(...,env="REDIS_PUBSUB_URL")

    class Config:
        env_file = ".env"


settings = Settings()