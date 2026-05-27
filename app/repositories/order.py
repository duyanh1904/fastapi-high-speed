import random

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderModel


class OrderRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def insert_seed_batch(self, batch_size: int) -> None:
        orders_batch = [
            {
                "user_id": random.randint(1, 50000),
                "item_id": random.randint(1, 2000),
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(10.0, 500.0), 2),
            }
            for _ in range(batch_size)
        ]
        await self.db_session.execute(text("USE test"))
        await self.db_session.execute(OrderModel.__table__.insert(), orders_batch)
        await self.db_session.commit()
