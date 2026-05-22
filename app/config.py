from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "High-Speed FastAPI"
    REDIS_URL: str = "redis://redis-server:6379/0"
    
    # SỬA: Đổi từ postgresql+asyncpg sang mysql+aiomysql để kết nối tới TiDB
    # Mặc định kết nối tới service 'tidb-server' qua cổng 4000 trong môi trường Docker Network
    DATABASE_URL: str = "mysql+aiomysql://root@tidb-server:4000/test"

    # SỬA: Cập nhật cú pháp chuẩn của Pydantic v2 (Thay thế class Config cũ)
    # Giúp tự động nhận diện và nạp đè dữ liệu từ file .env nếu có ở môi trường Local
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()