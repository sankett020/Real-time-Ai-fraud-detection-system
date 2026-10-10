from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./sentinel.db"
    
    class Config:
        env_file = ".env"

settings = Settings()