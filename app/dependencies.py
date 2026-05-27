from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_redis_client
from app.repositories.order import OrderRepository
from app.services.order import OrderService
from app.services.rate_limiter import RateLimiterService


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    redis_client = get_redis_client()
    order_repo = OrderRepository(db_session=db)
    return OrderService(redis_client=redis_client, order_repository=order_repo)


async def rate_limiter(request: Request) -> None:
    redis_client = get_redis_client()
    service = RateLimiterService(redis_client=redis_client)
    client_ip = request.client.host if request.client else "unknown"
    redis_key = f"rate_limit:{client_ip}"
    await service.enforce(redis_key)