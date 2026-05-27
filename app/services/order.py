import asyncio
import uuid

import redis.asyncio as aioredis

from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse


class OrderService:
    def __init__(self, redis_client: aioredis.Redis, order_repository: OrderRepository):
        self.redis_client = redis_client
        self.order_repository = order_repository

    async def create_order(self, order: OrderCreate) -> OrderResponse:
        cache_key = f"order:user:{order.user_id}:item:{order.item_id}"
        cached_order = await self.redis_client.get(cache_key)
        if cached_order:
            return OrderResponse(order_id=cached_order, status="SUCCESS_FROM_CACHE", cached=True)

        await asyncio.sleep(0.1)
        generated_id = str(uuid.uuid4())
        await self.redis_client.setex(cache_key, 60, generated_id)
        return OrderResponse(order_id=generated_id, status="CREATED_IN_DB", cached=False)

    async def seed_orders(self, total_records: int = 1_000_000, batch_size: int = 20_000) -> None:
        for _ in range(0, total_records, batch_size):
            await self.order_repository.insert_seed_batch(batch_size=batch_size)
