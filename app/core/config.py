from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kasparro Backend & ETL"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            # Handle Render/Heroku postgres:// vs postgresql://
            if self.DATABASE_URL.startswith("postgres://"):
                return self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
            return self.DATABASE_URL
        
        # Fallback to defaults if env vars are missing
        user = self.POSTGRES_USER or "postgres"
        password = self.POSTGRES_PASSWORD or "postgres"
        server = self.POSTGRES_SERVER or "db"
        port = self.POSTGRES_PORT or "5432"
        db = self.POSTGRES_DB or "kasparro"
        
        return f"postgresql://{user}:{password}@{server}:{port}/{db}"
    
    # Security: Use environment variables for these
    # Do NOT hardcode actual keys here
    API_KEY: Optional[str] = None
    COINPAPRIKA_API_KEY: Optional[str] = None
    DEBUG: bool = False

    model_config = ConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
