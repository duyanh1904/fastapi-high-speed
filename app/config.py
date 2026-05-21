from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "High-Speed FastAPI"
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"

    class Config:
        env_file = ".env"

settings = Settings()