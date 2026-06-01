import random
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import OrderModel

class OrderRepository:
    # Không giữ cứng session ở __init__ nữa để đảm bảo tính cô lập (Stateless)
    def __init__(self):
        pass

    async def insert_seed_batch(self, session: AsyncSession, batch_size: int) -> None:
        orders_batch = [
            {
                "user_id": random.randint(1, 50000),
                "item_id": random.randint(1, 2000),
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(10.0, 500.0), 2),
            }
            for _ in range(batch_size)
        ]

        # Thực thi an toàn tuyệt đối trên session riêng biệt được cấp phát
        await session.execute(text("USE test"))
        await session.execute(OrderModel.__table__.insert(), orders_batch)
        await session.commit()