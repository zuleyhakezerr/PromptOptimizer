from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Ayarları
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Prompt Optimizer"
    VERSION: str = "0.1.0"
    
    # OpenAI Ayarları
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    
    # MongoDB Ayarları
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = "prompt_optimizer"
    
    # Uygulama Ayarları
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Token Limitleri
    MAX_PROMPT_TOKENS: int = 4000
    MAX_COMPLETION_TOKENS: int = 1000
    
    # Performans Ayarları
    MAX_RESPONSE_TIME: int = 2  # saniye
    MAX_MEMORY_USAGE: int = 512  # MB
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Ayarları önbellekle ve döndür"""
    return Settings() 