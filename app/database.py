import redis.asyncio as aioredis
from app.config import settings

# Khởi tạo Redis Connection Pool bất đồng bộ
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=100,  # Giới hạn tối đa 100 kết nối đồng thời
    decode_responses=True
)

def get_redis_client():
    return aioredis.Redis(connection_pool=redis_pool)