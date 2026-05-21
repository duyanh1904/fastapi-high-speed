from fastapi import HTTPException, status, Request
from app.database import get_redis_client

async def rate_limiter(request: Request):
    redis = get_redis_client()

    # Giả lập lấy IP người dùng hoặc User ID từ Token làm Key
    client_ip = request.client.host
    redis_key = f"rate_limit:{client_ip}"

    # Giới hạn: Tối đa 5 request trong vòng 10 giây
    requests = await redis.incr(redis_key)
    if requests == 1:
        await redis.expire(redis_key, 10)

    if requests > 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please slow down!"
        )