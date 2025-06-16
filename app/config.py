from pydantic import  Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")

    spotify_client_id: str = Field(..., env="SPOTIFY_CLIENT_ID")
    spotify_client_secret: str = Field(..., env="SPOTIFY_CLIENT_SECRET")

    youtube_api_key: str = Field(..., env="YOUTUBE_API_KEY")

    class Config:
        env_file = ".env"


settings = Settings()