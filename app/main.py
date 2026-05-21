import uuid
import asyncio
from fastapi import FastAPI, Depends, status
from app.schemas import OrderCreate, OrderResponse
from app.dependencies import rate_limiter
from app.database import get_redis_client, redis_pool

app = FastAPI(title="High-Performance API Demo")

@app.on_event("shutdown")
async def shutdown_event():
    # Đóng kết nối Pool một cách an toàn khi tắt app
    await redis_pool.disconnect()

@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter)] # Ép tất cả request đi qua bộ lọc chống spam
)
async def create_order(order: OrderCreate):
    redis = get_redis_client()
    cache_key = f"order:user:{order.user_id}:item:{order.item_id}"

    # 1. Kiểm tra cache trong Redis trước để tối ưu tốc độ phản hồi
    cached_order = await redis.get(cache_key)
    if cached_order:
        return OrderResponse(order_id=cached_order, status="SUCCESS_FROM_CACHE", cached=True)

    # 2. Giả lập I/O Bound nặng khi ghi dữ liệu xuống Database (ví dụ: mất 100ms)
    # Nhờ từ khóa async, Uvicorn sẽ không bị block mà đi xử lý request khác ngay lập tức
    await asyncio.sleep(0.1)

    generated_id = str(uuid.uuid4())

    # 3. Ghi dữ liệu mới vào Cache với TTL = 60 giây để tái sử dụng
    await redis.setex(cache_key, 60, generated_id)

    return OrderResponse(order_id=generated_id, status="CREATED_IN_DB", cached=False)