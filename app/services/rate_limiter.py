import redis.asyncio as aioredis
from fastapi import HTTPException, status


class RateLimiterService:
    def __init__(self, redis_client: aioredis.Redis, max_requests: int = 5, ttl_seconds: int = 10):
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.ttl_seconds = ttl_seconds

    async def enforce(self, key: str) -> None:
        requests = await self.redis_client.incr(key)
        if requests == 1:
            await self.redis_client.expire(key, self.ttl_seconds)

        if requests > self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please slow down!",
            )
