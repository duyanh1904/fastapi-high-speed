import uuid
import asyncio
import random
from fastapi import FastAPI, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy import text
from app.dependencies import rate_limiter
from app.database import get_redis_client, redis_pool, get_db, engine
from app.models.order import OrderModel
from app.schemas.order import OrderCreate, OrderResponse
from app.database_util import create_db_lifespan
from app.routers.api import api_router
from app.core.database import Base

# 1. Khởi tạo db_lifespan bảo vệ
db_lifespan = create_db_lifespan(engine, base_metadata=Base.metadata, retries=12, delay=5)

# 2. Khởi tạo ứng dụng FastAPI DUY NHẤT một lần, cấu hình chuẩn
app = FastAPI(
    title="High-Performance API Demo",
    lifespan=db_lifespan
)

app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_event():
    # Đóng kết nối Pool một cách an toàn khi tắt app
    await redis_pool.disconnect()

@app.get("/")
async def root():
    return {"message": "FastAPI & TiDB Cluster are running perfectly!"}

@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter)]
)
async def create_order(order: OrderCreate):
    redis = get_redis_client()
    cache_key = f"order:user:{order.user_id}:item:{order.item_id}"

    cached_order = await redis.get(cache_key)
    if cached_order:
        return OrderResponse(order_id=cached_order, status="SUCCESS_FROM_CACHE", cached=True)

    await asyncio.sleep(0.1)
    generated_id = str(uuid.uuid4())
    await redis.setex(cache_key, 60, generated_id)

    return OrderResponse(order_id=generated_id, status="CREATED_IN_DB", cached=False)

@app.post("/api/v1/test/seed-orders", status_code=status.HTTP_202_ACCEPTED)
async def seed_million_orders(db: AsyncSession = Depends(get_db)):
    """
    API Sinh ngẫu nhiên và nạp 1 triệu bản ghi vào TiDB theo cơ chế Async Batching
    """
    total_records = 1_000_000
    batch_size = 20_000

    async def insert_batch(start_idx: int):
        orders_batch = [
            {
                "user_id": random.randint(1, 50000),
                "item_id": random.randint(1, 2000),
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(10.0, 500.0), 2)
            }
            for _ in range(batch_size)
        ]
        # Ép worker làm việc trên đúng scope database test
        await db.execute(text("USE test"))
        await db.execute(OrderModel.__table__.insert(), orders_batch)
        await db.commit()

    async def background_worker():
        print("🚀 Bắt đầu quá trình nạp 1.000.000 bản ghi vào TiDB...")
        start_time = asyncio.get_event_loop().time()

        for i in range(0, total_records, batch_size):
            try:
                await insert_batch(i)
                print(f"📦 Đã nạp thành công {i + batch_size} / {total_records} bản ghi...")
            except Exception as e:
                print(f"❌ Lỗi tại batch {i}: {e}")
            
        end_time = asyncio.get_event_loop().time()
        print(f"✨ HOÀN THÀNH! Tổng thời gian nạp: {end_time - start_time:.2f} giây.")

    asyncio.create_task(background_worker())
    
    return {"message": "Quá trình nạp 1 triệu đơn hàng đã được kích hoạt ngầm hệ thống thành công!"}