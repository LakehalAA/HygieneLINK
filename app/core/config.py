import os
from typing import List
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "HygieneLINK"
    DEBUG: bool = False
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:IgPaFbYZbWgOlpKquCtazxOBpSckdlhV@shortline.proxy.rlwy.net:13259/railway"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://hygienelinkfe-production.up.railway.app"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Cardano blockchain settings
    CARDANO_NETWORK: str = "preprod"
    BLOCKFROST_API_KEY: str = ""
    
    # External APIs
    WEATHER_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()