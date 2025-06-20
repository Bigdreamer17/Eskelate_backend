from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    jwt_secret: str
    jwt_expires_minutes: int = 60
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # class Config:
    #     env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
