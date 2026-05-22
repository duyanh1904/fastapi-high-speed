import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Khởi tạo Redis Connection Pool bất đồng bộ
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=100,  # Giới hạn tối đa 100 kết nối đồng thời
    decode_responses=True
)

def get_redis_client():
    return aioredis.Redis(connection_pool=redis_pool)

# Tạo Async Engine kết nối tới TiDB connection pool
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,       # Duy trì tối đa 20 kết nối mở sẵn tới TiDB
    max_overflow=10,
    pool_recycle=3600
)

AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session