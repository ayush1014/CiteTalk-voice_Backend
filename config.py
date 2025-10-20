"""
Configuration module for the Live 3D AI Agent backend.
"""
import os
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    openai_api_key: str = Field(default="")
    heygen_api_key: str = Field(default="")
    simli_api_key: str = Field(default="")
    simli_face_id: str = Field(default="")
    
    # Database
    database_url: str = Field(default= os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db"))
    
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=True)
    
    # CORS - stored as string, parsed to list
    cors_origins_str: str = Field(default="http://localhost:3000,http://localhost:5173", alias="cors_origins")
    
    @computed_field  # type: ignore[misc]
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins_str.split(',') if origin.strip()]
    
    # HeyGen
    heygen_video_id: str = Field(default="f395175e7c614214a6547297263ae8c2")
    heygen_api_base: str = Field(default="https://api.heygen.com")
    
    # OpenAI Model
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")
    
    # RAG Settings
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    retrieval_top_k: int = Field(default=4)


# Global settings instance
settings = Settings()
